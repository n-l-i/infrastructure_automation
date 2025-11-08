from utils.inventory import Host
from utils.ssh import Ssh_command_output, run_ssh_command


def ensure_apt_packages_are_up_to_date(host: Host) -> bool:
    # Ensure apt sources does not list any DVDs
    result: Ssh_command_output = run_ssh_command(
        host, "sudo sed -i '/^deb cdrom:/d' /etc/apt/sources.list"
    )

    # Ensure apt repositories are up to date
    result: Ssh_command_output = run_ssh_command(host, "sudo apt update")

    # Ensure apt packages are up to date
    result: Ssh_command_output = run_ssh_command(
        host,
        # Include phased updates to ensure we're fully up to date
        "sudo apt -o APT::Get::Always-Include-Phased-Updates=true full-upgrade -y",
    )
    changed = not result.stdout.split("\n")[-1].startswith(
        "0 upgraded, 0 newly installed"
    ) and not result.stdout.split("\n")[-1].strip().startswith(
        "Upgrading: 0, Installing: 0"
    )

    # Ensure no longer used apt packages are removed
    result: Ssh_command_output = run_ssh_command(
        host,
        "sudo apt autoremove -y",
    )
    changed = changed or (
        not result.stdout.split("\n")[-1].startswith(
            "0 upgraded, 0 newly installed"
        )
        and not result.stdout.split("\n")[-1]
        .strip()
        .startswith("Upgrading: 0, Installing: 0")
    )
    return changed
