from pathlib import Path
from typing import Any
from modules._modules import Module, Module_function_result, State, Module_step
from utils.inventory import Host
from utils.ssh import Ssh_command_output, run_ssh_command as _run_ssh_command


def file(
    dest_file_path: Path,
    host: Host,
    sudo: bool = False,
    src_file_path: Path | None = None,
    src_text: str | None = None,
) -> list[Module_function_result]:
    assert src_file_path or src_text, '"src_file_path" or "src_text" is required'
    assert (
        src_file_path is None or src_text is None
    ), 'Module values "src_file_path" and "src_text" cannot both be specified'
    assert dest_file_path, 'Module value "dest_file_path" is required'
    if src_file_path:
        with open(src_file_path, "r") as file_obj:
            src_text = file_obj.read().strip()
    current_dest_text = _get_file_contents_from_host(host, dest_file_path)
    if src_text == current_dest_text:
        return Module_function_result(
            state=State.UNCHANGED,
            return_value=None,
            module_values={},
        )
    _write_file_to_host(host, src_text, dest_file_path)
    current_dest_text = _get_file_contents_from_host(host, dest_file_path)
    if src_text != current_dest_text:
        raise Exception(
            f"File contents were not copied over properly on host '{host.host_name}'."
            f"{src_text} != {current_dest_text}"
        )
    return Module_function_result(
        state=State.CHANGED, return_value=None, module_values={}
    )


def _get_file_contents_from_host(host, file_path):
    file_path = file_path.replace("'", "")
    assert file_path[0] != "-", file_path
    try:
        result: Ssh_command_output = _run_ssh_command(
            host,
            f"cat {file_path}",
        )
    except Exception as e:
        if type(e.args[0]) != Ssh_command_output:
            raise e
        output = e.args[0]
        if not output.stderr.endswith(": No such file or directory"):
            raise e
        return None
    return result.stdout.strip()


def _write_file_to_host(host, src_text, dest_file_path):
    dest_file_path = dest_file_path.replace(" ", "")
    assert dest_file_path[0] != "-", dest_file_path
    src_text = src_text.replace("'", "")
    try:
        result: Ssh_command_output = _run_ssh_command(
            host,
            f"printf '%s\n' '{src_text}' > {dest_file_path}",
        )
    except Exception as e:
        raise Exception(f"Failed to run command on host '{host.host_name}': {e}") from e
