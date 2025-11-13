from typing import Any
from playbooks._playbooks import Play
from modules._modules import Module, Module_function_result, State
from modules.template import template as _template
from utils.inventory import Host
from utils.ssh import Ssh_command_output, run_ssh_command as _run_ssh_command
from pathlib import Path


def play() -> Play:
    current_directory = Path(__file__).parent.resolve()
    return Play(
        name="configure_sudo",
        modules=[
            Module(
                name="Get sudoers file location",
                steps=lambda host, play_values: [_get_sudoers_file_location],
                play_values={},
            ),
            _template(
                {
                    "template_file_path": Path.joinpath("sudoers.j2"),
                }
            ),
        ],
        results={},
    )


def _get_sudoers_file_location(
    host: Host,
    module_values: dict[str:Any],
    play_values: dict[str:Any],
) -> Module_function_result[None]:
    file_exists: dict[str:bool] = {}
    try:
        result: Ssh_command_output = _run_ssh_command(
            host, "test -f /etc/sudoers && echo true || false"
        )
    except Exception as e:
        raise Exception(
            f"Failed to run command on host '{host.host_name}': {e}"
        ) from e
    assert result.stdout.strip() in ("true", "false"), result
    file_exists["/etc/sudoers"] = result.stdout.strip() == "true"
    try:
        result: Ssh_command_output = _run_ssh_command(
            host, "test -f /usr/local/etc/sudoers && echo true || false"
        )
    except Exception as e:
        raise Exception(
            f"Failed to run command on host '{host.host_name}': {e}"
        ) from e
    assert result.stdout.strip() in ("true", "false"), result
    file_exists["/usr/local/etc/sudoers"] = result.stdout.strip() == "true"

    assert (
        file_exists["/etc/sudoers"]
        or file_exists["/usr/local/etc/sudoers"]
        and not (
            file_exists["/etc/sudoers"]
            and file_exists["/usr/local/etc/sudoers"]
        )
    ), f"{file_exists['/etc/sudoers']}, {file_exists['/usr/local/etc/sudoers']}"

    module_values["dest_file_path"] = (
        "/etc/sudoers"
        if file_exists["/etc/sudoers"]
        else "/usr/local/etc/sudoers"
    )
    return Module_function_result(
        state=State.UNCHANGED,
        return_value=None,
        module_values=module_values,
    )
