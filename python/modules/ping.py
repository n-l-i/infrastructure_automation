from typing import Any
from modules._modules import Module, Module_function_result, State, Module_step
from utils.inventory import Host
from utils.ssh import Ssh_command_output, run_ssh_command as _run_ssh_command


def ping() -> Module:
    return Module(name="Ping", steps=_steps, play_values={})


def _steps(host: Host, play_values: dict[str:Any]) -> list[Module_step]:
    return [_ping]


def _ping(
    host: Host,
    module_values: dict[str:Any],
) -> Module_function_result[None]:
    try:
        result: Ssh_command_output = _run_ssh_command(host, "echo ping")
    except Exception as e:
        raise Exception(
            f"Failed to run command on host '{host.host_name}': {e}"
        ) from e
    assert (
        result.stdout.strip() == "ping"
    ), f'Expected output "ping" != actual output "{result.stdout.strip()}"'

    return Module_function_result(
        state=State.UNCHANGED, return_value=None, module_values=module_values
    )
