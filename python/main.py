from dataclasses import asdict
import json
from pathlib import Path
from playbooks.ping_and_become import play
from utils.gather_facts import gather_facts
from utils.inventory import Host, Inventory, load_inventory


def main():
    current_path = Path(__file__).resolve().parent
    inventory_path = current_path.joinpath("secrets/inventory.yml")
    inventory: Inventory = load_inventory(inventory_path)

    print(inventory.keys())

    for host_name in ("ubuntu_host_local", "ubuntu_host_1", "debian_host_1"):
        data = gather_facts(inventory[host_name])
        data.ssh_key_path = str(data.ssh_key_path)
        print(json.dumps(asdict(data), indent=4))


main()
