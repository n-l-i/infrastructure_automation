import json
from utils.ssh import Ssh_command_output, run_ssh_command
from utils.inventory import Host


def gather_facts(host: Host) -> Host:
    host_data = {}

    result: Ssh_command_output = run_ssh_command(host, "whoami")
    host_data["username"] = result.stdout
    result: Ssh_command_output = run_ssh_command(host, "hostname")
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
    if os_release_data["ID"] == "ubuntu":
        host_data["os_id"] = "ubuntu"
        host_data["os_version"] = os_release_data["VERSION"].split(" ")[0]
    elif os_release_data["ID"] == "debian":
        host_data["os_id"] = "debian"
        result: Ssh_command_output = run_ssh_command(
            host, "cat /etc/debian_version"
        )
        host_data["os_version"] = result.stdout.strip()
    else:
        print(json.dumps(os_release_data, indent=4))
        raise ValueError(
            f"Unsupported OS ID '{os_release_data['ID']}' on host '{host.host_name}'"
        )

    return host_data


def _gather_package_managers(host: Host) -> list[str]:
    package_managers = []
    for pkg_mgr in ["apt", "snap", "pacman", "apk", "dnf", "yum"]:
        try:
            result: Ssh_command_output = run_ssh_command(
                host, f"which {pkg_mgr}"
            )
            package_managers.append(pkg_mgr)
        except Exception as e:
            continue

    return package_managers
