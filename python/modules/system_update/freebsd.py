from typing import Any
import urllib.request
from modules._modules import Module_function_result, State
from utils.inventory import Host
from utils.ssh import Ssh_command_output, run_ssh_command as _run_ssh_command


def ensure_freebsd_system_is_up_to_date(
    host: Host,
    module_values: dict[str:Any],
    play_values: dict[str:Any],
) -> Module_function_result[None]:
    # Ensure freebsd repositories are up to date
    needs_version_update = False
    try:
        result: Ssh_command_output = _run_ssh_command(
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
            and last_paragraph[0].endswith(" HAS PASSED ITS END-OF-LIFE DATE.")
        ):
            raise e
        if not (
            last_paragraph[1].startswith("Any security issues discovered after ")
            and last_paragraph[1].endswith(" will not have been corrected.")
        ):
            raise e
        needs_version_update = True
        result = e.args[0]
    packages_to_update_exist = (
        "No updates needed to update system to " not in result.stdout
    )
    changed = packages_to_update_exist

    # Ensure freebsd version is up to date
    if packages_to_update_exist:
        result: Ssh_command_output = _run_ssh_command(
            host, "sudo freebsd-update install"
        )

    if needs_version_update:
        latest_freebsd_version = sorted(_available_freebsd_versions())[-1]
        result: Ssh_command_output = _run_ssh_command(
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
            result: Ssh_command_output = _run_ssh_command(
                host, "sudo freebsd-update install"
            )
            result: Ssh_command_output = _run_ssh_command(host, "sudo shutdown -r now")
            attempt_count = 120
            successful = False
            for _ in range(attempt_count):
                try:
                    result: Ssh_command_output = _run_ssh_command(host, "echo ping")
                    successful = True
                    break
                except:
                    pass
            if not successful:
                raise Exception(
                    f"Not able to reconnect to host {host.host_name} since restarting after update"
                )
            result: Ssh_command_output = _run_ssh_command(
                host, "sudo freebsd-update install"
            )
    return Module_function_result(
        state=State.UNCHANGED if not changed else State.CHANGED,
        return_value=None,
        module_values=module_values,
    )


def _available_freebsd_versions() -> list[str]:
    try:
        response = (
            urllib.request.urlopen("https://download.freebsd.org/ftp/releases/amd64/")
            .read()
            .decode("utf-8")
        )
    except Exception as e:
        raise Exception("Failed to fetch FreeBSD releases data.") from e
    versions = []
    for line in response.split("\n"):
        if line.strip().startswith('<tr><td class="link"><a href="'):
            version = line.split('<tr><td class="link"><a href="')[1].split("/")[0]
            if "RELEASE" in version:
                versions.append(version)
    if not versions:
        raise Exception("No available FreeBSD versions found.")
    return versions
