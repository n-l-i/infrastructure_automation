from playbooks._playbooks import Play
from modules._modules import Module_function_result, State
from modules import ping as _ping
from utils.inventory import Host
from utils.ssh import Ssh_command_output, run_ssh_command as _run_ssh_command


def play() -> Play:
    return Play(
        name="ping_and_become",
        steps=[
            _ping,
            _test_non_become_command,
            _test_become_command,
        ],
        results={},
    )


def _test_non_become_command(host: Host) -> Module_function_result[None]:
    try:
        result: Ssh_command_output = _run_ssh_command(host, "whoami")
    except Exception as e:
        raise Exception(
            f"Failed to run command on host '{host.host_name}': {e}"
        ) from e
    assert (
        result.stdout.strip() == host.username
    ), f'Expected user "{host.username}" != actual user "{result.stdout.strip()}"'

    return Module_function_result(
        state=State.UNCHANGED,
        return_value=None,
    )


def _test_become_command(host: Host) -> Module_function_result[None]:
    try:
        result: Ssh_command_output = _run_ssh_command(host, "sudo whoami")
    except Exception as e:
        raise Exception(
            f"Failed to run command on host '{host.host_name}': {e}"
        ) from e
    expected_root_user = "root"
    assert (
        result.stdout.strip() == expected_root_user
    ), f'Expected user "{expected_root_user}" != actual user "{result.stdout.strip()}"'

    return Module_function_result(
        state=State.UNCHANGED,
        return_value=None,
    )
