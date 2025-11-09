from typing import Any
from modules._modules import Module, Module_function_result, State, Module_step
from utils.inventory import Host
from utils.ssh import Ssh_command_output, run_ssh_command as _run_ssh_command
from modules.system_update.apt import (
    ensure_apt_packages_are_up_to_date as _ensure_apt_packages_are_up_to_date,
)
from modules.system_update.snap import (
    ensure_snap_packages_are_up_to_date as _ensure_snap_packages_are_up_to_date,
)
from modules.system_update.pacman import (
    ensure_pacman_packages_are_up_to_date as _ensure_pacman_packages_are_up_to_date,
)
from modules.system_update.pkg import (
    ensure_pkg_packages_are_up_to_date as _ensure_pkg_packages_are_up_to_date,
)
from modules.system_update.freebsd import (
    ensure_freebsd_system_is_up_to_date as _ensure_freebsd_system_is_up_to_date,
)


def ensure_system_is_up_to_date() -> Module:
    return Module(name="Ensure system is up to date", steps=_steps)


def _steps(host: Host, play_values: dict[str:Any]) -> list[Module_step]:
    list_of_steps = []
    if "apt" in host.package_manager:
        list_of_steps.append(_ensure_apt_packages_are_up_to_date)
    if "snap" in host.package_manager:
        list_of_steps.append(_ensure_snap_packages_are_up_to_date)
    if "pacman" in host.package_manager:
        list_of_steps.append(_ensure_pacman_packages_are_up_to_date)
    if "apk" in host.package_manager:

        def apk_not_implemented(host, module_values, play_values):
            raise NotImplementedError(
                "APK package manager support is not fully implemented yet."
            )

        list_of_steps.append(apk_not_implemented)
    if "dnf" in host.package_manager:

        def dnf_not_implemented(host, module_values, play_values):
            raise NotImplementedError(
                "dnf package manager support is not fully implemented yet."
            )

        list_of_steps.append(dnf_not_implemented)
    if "yum" in host.package_manager:

        def yum_not_implemented(host, module_values, play_values):
            raise NotImplementedError(
                "yum package manager support is not fully implemented yet."
            )

        list_of_steps.append(yum_not_implemented)
    if "pkg" in host.package_manager:
        list_of_steps.append(_ensure_freebsd_system_is_up_to_date)
        list_of_steps.append(_ensure_pkg_packages_are_up_to_date)

    if host.package_manager and not any(
        pkg_mgr in host.package_manager
        for pkg_mgr in ["apt", "snap", "pacman", "apk", "dnf", "yum", "pkg"]
    ):

        def unsupported_package_manager(host, module_values, play_values):
            raise NotImplementedError(
                f"Unsupported package manager: {host.package_manager}"
            )

        list_of_steps.append(unsupported_package_manager)

    return list_of_steps


def get_installed_packages(host: Host) -> list[str]:
    installed_packages = []
    if "apt" in host.package_manager:
        result: Ssh_command_output = _run_ssh_command(host, "apt list --installed")
        package_list = result.stdout.split("\n")[1:]
        package_names = [pkg.split("/")[0] for pkg in package_list if pkg]
        installed_packages += package_names
    if "snap" in host.package_manager:
        result: Ssh_command_output = _run_ssh_command(host, "snap list")
        package_list = result.stdout.split("\n")[1:]
        package_names = [pkg.split(" ")[0] for pkg in package_list if pkg]
        installed_packages += package_names
    if "pacman" in host.package_manager:
        result: Ssh_command_output = _run_ssh_command(host, "pacman -Q")
        package_list = result.stdout.split("\n")
        package_names = [pkg.split(" ")[0] for pkg in package_list if pkg]
        installed_packages += package_names
    if "apk" in host.package_manager:
        result: Ssh_command_output = _run_ssh_command(host, "apk info")
        package_list = result.stdout.split("\n")
        installed_packages += package_list
        raise NotImplementedError(
            "APK package manager support is not fully implemented yet."
        )
    if "dnf" in host.package_manager:
        result: Ssh_command_output = _run_ssh_command(host, "dnf list installed")
        package_list = result.stdout.split("\n")
        installed_packages += package_list
        raise NotImplementedError(
            "APK package manager support is not fully implemented yet."
        )
    if "yum" in host.package_manager:
        result: Ssh_command_output = _run_ssh_command(host, "yum list installed")
        package_list = result.stdout.split("\n")
        installed_packages += package_list
        raise NotImplementedError(
            "APK package manager support is not fully implemented yet."
        )
    if "pkg" in host.package_manager:
        result: Ssh_command_output = _run_ssh_command(host, "pkg query %n")
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
