from pathlib import Path
from playbooks.ping_and_become import play
from utils.inventory import Host, Inventory, load_inventory


def main():
    current_path = Path(__file__).resolve().parent
    inventory_path = current_path.joinpath("secrets/inventory.yml")
    inventory: Inventory = load_inventory(inventory_path)

    play(inventory)


main()
