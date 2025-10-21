from dataclasses import asdict
import json
from pathlib import Path
from playbooks.ping_and_become import play as ping_and_become
from playbooks.update_system import play as update_system
from utils.gather_facts import gather_facts
from utils.inventory import Host, Inventory, load_inventory


def main():
    current_path = Path(__file__).resolve().parent
    inventory_path = current_path.joinpath("secrets/inventory.yml")
    inventory: Inventory = load_inventory(inventory_path)

    print(inventory.keys())

    for host_name, host in inventory.items():
        try:
            host = gather_facts(host)
            inventory[host_name] = host
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
        try:
            update_system(host)
        except Exception as e:
            print(
                f"Failed to run play update_system for host '{host_name}': {e}"
            )
            continue


if __name__ == "__main__":
    main()
