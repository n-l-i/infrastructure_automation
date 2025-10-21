from dataclasses import asdict
import json
from pathlib import Path
from playbooks.ping_and_become import play as ping_and_become
from utils.gather_facts import gather_facts
from utils.inventory import Host, Inventory, load_inventory


def main():
    current_path = Path(__file__).resolve().parent
    inventory_path = current_path.joinpath("secrets/inventory.yml")
    inventory: Inventory = load_inventory(inventory_path)

    print(inventory.keys())

    for host_name, host in inventory.items():
        try:
            inventory[host_name] = gather_facts(host)
        except Exception as e:
            print(f"Failed to gather facts for host '{host_name}': {e}")
            continue
        try:
            ping_and_become(host)
        except Exception as e:
            print(
                f"Failed to run play ping_and_become for host '{host_name}': {e}"
            )
            continue


main()
