from pathlib import Path
from modules.ping_and_become import ping_and_become
from modules.system_update import ensure_system_is_up_to_date
from modules._modules import Module_function_result
from utils.gather_facts import gather_facts
from utils.inventory import Inventory, load_inventory


def main():
    current_path = Path(__file__).resolve().parent
    inventory_path = current_path.joinpath("secrets/inventory.yml")
    inventory: Inventory = load_inventory(inventory_path)

    for failing_host in ("ubuntu_guest_1", "ubuntu_guest_4", "mikrotik_router"):
        if failing_host in inventory:
            inventory.pop("ubuntu_guest_1")

    tasks = (gather_facts, ping_and_become, ping_and_become, ensure_system_is_up_to_date)
    longest_task_name_length = max([len(task.__name__) for task in tasks])

    print(" "*longest_task_name_length+"  "+", ".join(inventory.keys()))
    failed_hosts = set()
    for task in tasks:
        print(task.__name__.rjust(longest_task_name_length)+": ", end="")
        for host_name, host in inventory.items():
            column_distance = len(host_name)+2
            if host_name in failed_hosts:
                print("X".ljust(column_distance), end="")
                continue
            if task.__name__ == "gather_facts":
                try:
                    inventory[host_name] = task(host)
                except:
                    failed_hosts = host_name
                result = Module_function_result(
                    changed=False,
                    return_value=None,
                )
            else:
                try:
                    result = task(host)
                except:
                    failed_hosts = host_name
            if host_name in failed_hosts:
                print("X".ljust(column_distance), end="")
                continue
            print(
                ("0" if not result.changed else "1").ljust(column_distance)
                , end=""
            )
        print()


if __name__ == "__main__":
    main()
