import json
from utils.ssh import Ssh_command_output, run_ssh_command
from utils.inventory import Host


def gather_facts(host: Host) -> Host:
    host_data = {}

    result: Ssh_command_output = run_ssh_command(host, "whoami")
    host_data["username"] = result.stdout
    try:
        result: Ssh_command_output = run_ssh_command(host, "hostname")
    except Exception as e:
        result: Ssh_command_output = run_ssh_command(host, "echo $HOSTNAME")
        if not result.stdout:
            raise Exception(
                f"Failed to gather hostname for host '{host.host_name}'"
            )
    host_data["host_name"] = result.stdout
    host_data |= _gather_os_data(host)
    host_data["package_managers"] = _gather_package_managers(host)

    return Host(
        host_name=host_data["host_name"],
        username=host_data["username"],
        ip_address=host.ip_address,
        ssh_port=host.ssh_port,
        ssh_key_path=host.ssh_key_path,
        groups=host.groups,
        package_manager=host_data["package_managers"],
        os_id=host_data["os_id"],
        os_version=host_data["os_version"],
    )


# See: https://unix.stackexchange.com/questions/6345/how-can-i-get-distribution-name-and-version-number-in-a-simple-shell-script
def _gather_os_data(host: Host) -> dict[str, str]:
    host_data = {}
    result: Ssh_command_output = run_ssh_command(host, "cat /etc/os-release")
    os_release_data = {
        key.strip(): value.strip().replace('"', "")
        for line in result.stdout.split("\n")
        if (key := line.split("=")[0]) and (value := line.split("=")[1])
    }
    host_data["os_id"] = os_release_data["ID"]
    if os_release_data["ID"] == "ubuntu":
        host_data["os_version"] = os_release_data["VERSION"].split(" ")[0]
    elif os_release_data["ID"] == "debian":
        result: Ssh_command_output = run_ssh_command(
            host, "cat /etc/debian_version"
        )
        host_data["os_version"] = result.stdout
    elif os_release_data["ID"] == "freebsd":
        host_data["os_version"] = os_release_data["VERSION"]
    elif os_release_data["ID"] == "arch":
        # Arch Linux does not have version numbers so using the date of
        # the last full system upgrade as a proxy. If no upgrades have been
        # performed, the first line of the pacman log is used instead. This
        # should be the date of the initial installation.
        try:
            result: Ssh_command_output = run_ssh_command(
                host,
                'cat /var/log/pacman.log | grep "starting full system upgrade"',
            )
        except Exception as e:
            result: Ssh_command_output = run_ssh_command(
                host,
                "head -n 1 /var/log/pacman.log",
            )
            if not result.stdout:
                raise Exception(
                    f"Failed to gather OS version for host '{host.host_name}'"
                )
        host_data["os_version"] = (
            result.stdout.split("\n")[-1].split("[")[1].split("]")[0]
        )
    else:
        raise ValueError(
            f"Unsupported OS ID '{os_release_data['ID']}' on host '{host.host_name}'"
        )

    return host_data


def _gather_package_managers(host: Host) -> list[str]:
    package_managers = []
    for package_manager, package_manager_test_command in {
        "apt": "apt list --installed",
        "snap": "snap list",
        "pacman": "pacman -Q",
        "apk": "apk info",
        "dnf": "dnf list installed",
        "yum": "yum list installed",
        "pkg": "pkg info",
    }.items():
        try:
            result: Ssh_command_output = run_ssh_command(
                host, package_manager_test_command
            )
            package_managers.append(package_manager)
        except Exception as e:
            continue

    return package_managers
