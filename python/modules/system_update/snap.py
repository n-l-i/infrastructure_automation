from typing import Any
from modules._modules import Module_function_result, State
from utils.inventory import Host
from utils.ssh import Ssh_command_output, run_ssh_command as _run_ssh_command


def ensure_snap_packages_are_up_to_date(
    host: Host,
    module_values: dict[str:Any],
    play_values: dict[str:Any],
) -> Module_function_result[None]:
    result: Ssh_command_output = _run_ssh_command(host, "sudo snap refresh")
    changed = result.stderr != "All snaps up to date."
    return Module_function_result(
        state=State.UNCHANGED if not changed else State.CHANGED,
        return_value=None,
        module_values=module_values,
    )
