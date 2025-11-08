from modules._modules import Module_function_result, State
from utils.inventory import Host
from utils.ssh import Ssh_command_output, run_ssh_command
from modules.system_update.apt import ensure_apt_packages_are_up_to_date
from modules.system_update.snap import ensure_snap_packages_are_up_to_date
from modules.system_update.pacman import ensure_pacman_packages_are_up_to_date
from modules.system_update.pkg import ensure_pkg_packages_are_up_to_date
from modules.system_update.freebsd import ensure_freebsd_system_is_up_to_date


def ensure_system_is_up_to_date(host: Host) -> Module_function_result[None]:
    changed = False
    if "apt" in host.package_manager:
        changed = changed or ensure_apt_packages_are_up_to_date(host)
    if "snap" in host.package_manager:
        changed = changed or ensure_snap_packages_are_up_to_date(host)
    if "pacman" in host.package_manager:
        changed = changed or ensure_pacman_packages_are_up_to_date(host)
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
        changed = changed or ensure_freebsd_system_is_up_to_date(host)
        changed = changed or ensure_pkg_packages_are_up_to_date(host)

    if host.package_manager and not any(
        pkg_mgr in host.package_manager
        for pkg_mgr in ["apt", "snap", "pacman", "apk", "dnf", "yum", "pkg"]
    ):
        raise NotImplementedError(
            f"Unsupported package manager: {host.package_manager}"
        )

    return Module_function_result(
        state=State.CHANGED if changed else State.UNCHANGED,
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
