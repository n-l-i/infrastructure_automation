from dataclasses import asdict
import json
from utils.inventory import Host, Inventory
from utils.ssh import Ssh_command_output, run_ssh_command


def play(
    inventory: Inventory,
    hosts: list[str] = ["ubuntu_host_local"],
    host_groups: list[str] = [],
):
    hosts: list[Host] = [inventory[host_name] for host_name in hosts]
    for host in hosts:
        result: Ssh_command_output = run_ssh_command(host, "whoami")
        print(json.dumps(asdict(result), indent=4))

        result: Ssh_command_output = run_ssh_command(host, "sudo whoami")
        print(json.dumps(asdict(result), indent=4))
