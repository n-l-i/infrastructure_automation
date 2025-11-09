from typing import Any
from modules._modules import Module_function_result, State
from utils.inventory import Host
from utils.ssh import Ssh_command_output, run_ssh_command as _run_ssh_command


def ensure_pacman_packages_are_up_to_date(
    host: Host,
    module_values: dict[str:Any],
    play_values: dict[str:Any],
) -> Module_function_result[None]:
    result: Ssh_command_output = _run_ssh_command(host, "sudo pacman -Syu --noconfirm")
    changed = result.stdout.split("\n")[-1].strip() != "there is nothing to do"

    # Ensure no longer used pacman packages are removed
    orphaned_packages_exists: bool
    try:
        result: Ssh_command_output = _run_ssh_command(host, "pacman -Qdtq")
        orphaned_packages_exists = True
    except Exception as e:
        orphaned_packages_exists = False
    if orphaned_packages_exists:
        result: Ssh_command_output = _run_ssh_command(
            host, "sudo pacman -Rns $(pacman -Qdtq) --noconfirm"
        )
        changed = True
    return Module_function_result(
        state=State.UNCHANGED if not changed else State.CHANGED,
        return_value=None,
        module_values=module_values,
    )
