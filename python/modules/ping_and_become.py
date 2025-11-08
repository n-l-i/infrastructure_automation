from modules._modules import Module_function_result, State
from utils.inventory import Host
from utils.ssh import Ssh_command_output, run_ssh_command


def ping_and_become(host: Host) -> Module_function_result[None]:
    try:
        result: Ssh_command_output = run_ssh_command(host, "whoami")
    except Exception as e:
        raise Exception(
            f"Failed to run command on host '{host.host_name}': {e}"
        ) from e
    assert (
        result.stdout.strip() == host.username
    ), f'Expected user "{host.username}" != actual user "{result.stdout.strip()}"'

    try:
        result: Ssh_command_output = run_ssh_command(host, "sudo whoami")
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
