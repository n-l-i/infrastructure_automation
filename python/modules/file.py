from typing import Any
from modules._modules import Module, Module_function_result, State, Module_step
from utils.inventory import Host
from utils.ssh import Ssh_command_output, run_ssh_command as _run_ssh_command


def file() -> Module:
    return Module(name="File", steps=_steps)


def _steps(host: Host, play_values: dict[str:Any]) -> list[Module_step]:
    return [_file]


def _file(
    host: Host,
    module_values: dict[str:Any],
) -> Module_function_result[None]:
    assert (
        "src_file_path" in module_values.keys()
        or "src_text" in module_values.keys()
    ), 'Module value "src_file_path" or "src_text" is required'
    assert (
        "src_file_path" in module_values.keys()
        and "src_text" in module_values.keys()
    ), 'Module values "src_file_path" and "src_text" cannot both be specified'
    assert (
        "dest_file_path" in module_values.keys()
    ), 'Module value "dest_file_path" is required'
    if "src_text" in module_values.keys():
        src_text = module_values["src_text"].strip()
    else:
        with open(module_values["src_file_path"], "r") as file_obj:
            src_text = file_obj.read().strip()
    current_dest_text = _get_file_contents_from_host(
        host, module_values["dest_file_path"]
    ).strip()
    if src_text == current_dest_text:
        return Module_function_result(
            state=State.UNCHANGED,
            return_value=None,
            module_values=module_values,
        )
    _write_file_to_host(host, src_text, module_values["dest_file_path"])
    current_dest_text = _get_file_contents_from_host(
        host, module_values["dest_file_path"]
    ).strip()
    if src_text != current_dest_text:
        raise Exception(
            f"File contents were not copied over properly on host '{host.host_name}'"
        )
    return Module_function_result(
        state=State.CHANGED, return_value=None, module_values=module_values
    )


def _get_file_contents_from_host(host, file_path):
    try:
        result: Ssh_command_output = _run_ssh_command(
            host,
            'cat -- "$file_path"',
            parameters={
                "file_path": file_path,
            },
        )
    except Exception as e:
        raise Exception(
            f"Failed to run command on host '{host.host_name}': {e}"
        ) from e
    return result.stdout


def _write_file_to_host(host, src_text, dest_file_path):
    try:
        result: Ssh_command_output = _run_ssh_command(
            host,
            'printf \'%s\n\' "$src_text" > "$dest_file_path"',
            parameters={
                "src_text": src_text,
                "dest_file_path": dest_file_path,
            },
        )
    except Exception as e:
        raise Exception(
            f"Failed to run command on host '{host.host_name}': {e}"
        ) from e
