import json
from modules.modules import Module_function_result
from utils.inventory import Host
from utils.ssh import Ssh_command_output, run_ssh_command


def update_installed_packages(host: Host) -> Module_function_result[None]:
    changed = False
    if "apt" in host.package_manager:
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
        changed = changed or not result.stdout.split("\n")[-1].startswith(
            "0 upgraded, 0 newly installed"
        )

        # Ensure no longer used apt packages are removed
        result: Ssh_command_output = run_ssh_command(
            host,
            "sudo apt autoremove -y",
        )
        changed = changed or not result.stdout.split("\n")[-1].startswith(
            "0 upgraded, 0 newly installed"
        )

    if "snap" in host.package_manager:
        # Ensure snap packages are up to date
        result: Ssh_command_output = run_ssh_command(host, "sudo snap refresh")
        changed = changed or result.stdout != "All snaps up to date."
    if "pacman" in host.package_manager:
        # Ensure pacman packages are up to date
        result: Ssh_command_output = run_ssh_command(
            host, "sudo pacman -Syu --noconfirm"
        )
        changed = (
            changed
            or result.stdout.split("\n")[-1].strip() != "there is nothing to do"
        )

        # Ensure no longer used pacman packages are removed
        orphaned_packages_exists: bool
        try:
            result: Ssh_command_output = run_ssh_command(host, "pacman -Qdtq")
            orphaned_packages_exists = True
        except Exception as e:
            orphaned_packages_exists = False
        if orphaned_packages_exists:
            result: Ssh_command_output = run_ssh_command(
                host, "sudo pacman -Rns $(pacman -Qdtq) --noconfirm"
            )
            changed = True
    if "apk" in host.package_manager:
        raise NotImplementedError(
            "APK package manager support is not fully implemented yet."
        )
    if "dnf" in host.package_manager:
        raise NotImplementedError(
            "dnf package manager support is not fully implemented yet."
        )
    if "yum" in host.package_manager:
        raise NotImplementedError(
            "yum package manager support is not fully implemented yet."
        )
    if "pkg" in host.package_manager:
        raise NotImplementedError(
            "yum package manager support is not fully implemented yet."
        )

    if host.package_manager and not any(
        pkg_mgr in host.package_manager
        for pkg_mgr in ["apt", "snap", "pacman", "apk", "dnf", "yum", "pkg"]
    ):
        raise NotImplementedError(
            f"Unsupported package manager: {host.package_manager}"
        )

    return Module_function_result(
        changed=changed,
        return_value=None,
    )


def get_installed_packages(host: Host) -> list[str]:
    installed_packages = []
    if "apt" in host.package_manager:
        result: Ssh_command_output = run_ssh_command(
            host, "apt list --installed"
        )
        package_list = result.stdout.split("\n")[1:]
        package_names = [pkg.split("/")[0] for pkg in package_list if pkg]
        installed_packages += package_names
    if "snap" in host.package_manager:
        result: Ssh_command_output = run_ssh_command(host, "snap list")
        package_list = result.stdout.split("\n")[1:]
        package_names = [pkg.split(" ")[0] for pkg in package_list if pkg]
        installed_packages += package_names
    if "pacman" in host.package_manager:
        result: Ssh_command_output = run_ssh_command(host, "pacman -Q")
        package_list = result.stdout.split("\n")
        package_names = [pkg.split(" ")[0] for pkg in package_list if pkg]
        installed_packages += package_names
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
        result: Ssh_command_output = run_ssh_command(host, "pkg query %n")
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
