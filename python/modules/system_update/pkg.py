from utils.inventory import Host
from utils.ssh import Ssh_command_output, run_ssh_command as _run_ssh_command


def ensure_pkg_packages_are_up_to_date(host: Host) -> bool:
    # Ensure pkg repositories are up to date
    result: Ssh_command_output = _run_ssh_command(host, "sudo pkg update")

    # Ensure pkg packages are up to date
    result: Ssh_command_output = _run_ssh_command(
        host,
        # Include phased updates to ensure we're fully up to date
        "sudo pkg upgrade -y",
    )
    changed = not result.stdout.split("\n")[-1].endswith(
        "Your packages are up to date."
    )

    # Ensure no longer used apt packages are removed
    result: Ssh_command_output = _run_ssh_command(
        host,
        "sudo pkg autoremove -y",
    )
    changed = changed or not result.stdout.split("\n")[-1].endswith(
        "Nothing to do."
    )
    return changed
