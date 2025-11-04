from utils.inventory import Host
from utils.ssh import Ssh_command_output, run_ssh_command


def ensure_snap_packages_are_up_to_date(host: Host) -> bool:
    result: Ssh_command_output = run_ssh_command(host, "sudo snap refresh")
    return result.stdout != "All snaps up to date."
