from utils.inventory import Host
from utils.ssh import Ssh_command_output, run_ssh_command


def get_installed_packages(host: Host) -> list[str]:
    installed_packages = []
    if "apt" in host.package_manager:
        result: Ssh_command_output = run_ssh_command(
            host, "apt list --installed"
        )
        package_list = result.stdout.split("\n")[1:]
        installed_packages += package_list
    if "snap" in host.package_manager:
        result: Ssh_command_output = run_ssh_command(host, "snap list")
        package_list = result.stdout.split("\n")
        installed_packages += package_list
    if "pacman" in host.package_manager:
        result: Ssh_command_output = run_ssh_command(host, "pacman -Q")
        package_list = result.stdout.split("\n")
        installed_packages += package_list
    if "apk" in host.package_manager:
        result: Ssh_command_output = run_ssh_command(host, "apk info")
        package_list = result.stdout.split("\n")
        installed_packages += package_list
        raise NotImplementedError(
            "APK package manager support is not fully implemented yet."
        )
    if "dnf" in host.package_manager:
        result: Ssh_command_output = run_ssh_command(host, "dnf list installed")
        package_list = result.stdout.split("\n")
        installed_packages += package_list
        raise NotImplementedError(
            "APK package manager support is not fully implemented yet."
        )
    if "yum" in host.package_manager:
        result: Ssh_command_output = run_ssh_command(host, "yum list installed")
        package_list = result.stdout.split("\n")
        installed_packages += package_list
        raise NotImplementedError(
            "APK package manager support is not fully implemented yet."
        )
    if "pkg" in host.package_manager:
        result: Ssh_command_output = run_ssh_command(host, "pkg info")
        package_list = result.stdout.split("\n")
        installed_packages += package_list

    if host.package_manager and not any(
        pkg_mgr in host.package_manager
        for pkg_mgr in ["apt", "snap", "pacman", "apk", "dnf", "yum", "pkg"]
    ):
        raise NotImplementedError(
            f"Unsupported package manager: {host.package_manager}"
        )

    # Filter out empty strings
    installed_packages = [pkg for pkg in installed_packages if pkg]
    return installed_packages
