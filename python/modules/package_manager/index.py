import urllib.request
from modules.modules import Module_function_result
from utils.inventory import Host
from utils.ssh import Ssh_command_output, run_ssh_command


def update_installed_packages(host: Host) -> Module_function_result[None]:
    changed = False
    print(host.package_manager)
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
        # Ensure freebsd repositories are up to date
        needs_version_update = False
        try:
            result: Ssh_command_output = run_ssh_command(
                host, "sudo freebsd-update fetch --not-running-from-cron"
            )
        except Exception as e:
            if type(e.args[0]) != Ssh_command_output:
                raise e
            if e.args[0].stderr:
                raise e
            stdout = e.args[0].stdout.split("\n")
            if len(stdout) < 2:
                raise e
            last_paragraph_delimiter_index = 0
            for i, line in enumerate(stdout):
                if not line:
                    last_paragraph_delimiter_index = i
            last_paragraph = stdout[last_paragraph_delimiter_index + 1 :]
            last_paragraph = (last_paragraph[0], " ".join(last_paragraph[1:]))
            if not (
                last_paragraph[0].startswith("WARNING: FreeBSD ")
                and last_paragraph[0].endswith(
                    " HAS PASSED ITS END-OF-LIFE DATE."
                )
            ):
                raise e
            if not (
                last_paragraph[1].startswith(
                    "Any security issues discovered after "
                )
                and last_paragraph[1].endswith(" will not have been corrected.")
            ):
                raise e
            needs_version_update = True
            result = e.args[0]
        packages_to_update_exist = (
            "No updates needed to update system to " not in result.stdout
        )
        changed = changed or packages_to_update_exist

        # Ensure freebsd version is up to date
        if packages_to_update_exist:
            result: Ssh_command_output = run_ssh_command(
                host, "sudo freebsd-update install"
            )

        if needs_version_update:
            latest_freebsd_version = sorted(_available_freebsd_versions())[-1]
            result: Ssh_command_output = run_ssh_command(
                host,
                f"yes y | sudo freebsd-update upgrade -r {latest_freebsd_version}",
                with_pty=True,
            )
            packages_to_update_exist = (
                "The following files will be removed as part of updating to"
                in result.stdout
                or "The following files will be added as part of updating to"
                in result.stdout
                or "The following files will be updated as part of updating to"
                in result.stdout
            )
            changed = changed or packages_to_update_exist
            if packages_to_update_exist:
                result: Ssh_command_output = run_ssh_command(
                    host, "sudo freebsd-update install"
                )
                result: Ssh_command_output = run_ssh_command(
                    host, "sudo shutdown -r now"
                )
                attempt_count = 120
                for attempt in range(attempt_count):
                    try:
                        result: Ssh_command_output = run_ssh_command(
                            host, "echo ping"
                        )
                        break
                    except:
                        print(
                            f"Failed to connect, {attempt_count-attempt-1} attempts left."
                        )
                result: Ssh_command_output = run_ssh_command(
                    host, "sudo freebsd-update install"
                )

        # Ensure pkg repositories are up to date
        result: Ssh_command_output = run_ssh_command(host, "sudo pkg update")

        # Ensure pkg packages are up to date
        result: Ssh_command_output = run_ssh_command(
            host,
            # Include phased updates to ensure we're fully up to date
            "sudo pkg upgrade -y",
        )
        changed = changed or not result.stdout.split("\n")[-1].endswith(
            "Your packages are up to date."
        )

        # Ensure no longer used apt packages are removed
        result: Ssh_command_output = run_ssh_command(
            host,
            "sudo pkg autoremove -y",
        )
        changed = changed or not result.stdout.split("\n")[-1].endswith(
            "Nothing to do."
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


def _available_freebsd_versions() -> list[str]:
    try:
        response = (
            urllib.request.urlopen(
                "https://download.freebsd.org/ftp/releases/amd64/"
            )
            .read()
            .decode("utf-8")
        )
    except Exception as e:
        raise Exception("Failed to fetch FreeBSD releases data.") from e
    versions = []
    for line in response.split("\n"):
        if line.strip().startswith('<tr><td class="link"><a href="'):
            version = line.split('<tr><td class="link"><a href="')[1].split(
                "/"
            )[0]
            if "RELEASE" in version:
                versions.append(version)
    if not versions:
        raise Exception("No available FreeBSD versions found.")
    return versions
