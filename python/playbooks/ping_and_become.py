from dataclasses import asdict
import json
from utils.inventory import Host
from utils.ssh import Ssh_command_output, run_ssh_command


def play(host: Host):
    try:
        result: Ssh_command_output = run_ssh_command(host, "whoami")
        print(json.dumps(asdict(result), indent=4))

        result: Ssh_command_output = run_ssh_command(host, "sudo whoami")
        print(json.dumps(asdict(result), indent=4))
    except Exception as e:
        print(f"Failed to run commands on host '{host.host_name}': {e}")
