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
            inventory.pop(failing_host)

    tasks = [
        ping_and_become,
        gather_facts,
        ping_and_become,
        ping_and_become,
        ensure_system_is_up_to_date,
    ]

    state = [{host_name: None for host_name in inventory.keys()} for _ in tasks]
    _print_state(state, tasks)
    failed_hosts = set()
    for i, task in enumerate(tasks):
        for host_name, host in inventory.items():
            if host_name in failed_hosts:
                state[i][host_name] = "-"
                _print_state(state, tasks)
                continue
            if task.__name__.endswith("_facts"):
                try:
                    inventory[host_name] = task(host)
                except Exception as e:
                    print(e)
                    failed_hosts.add(host_name)
                result = Module_function_result(
                    changed=False,
                    return_value=None,
                )
            else:
                try:
                    result = task(host)
                except Exception as e:
                    print(e)
                    failed_hosts.add(host_name)
            if host_name in failed_hosts:
                state[i][host_name] = "X"
                _print_state(state, tasks)
                continue
            state[i][host_name] = "0" if not result.changed else "1"
            _print_state(state, tasks)


def _print_state(state, tasks):
    hosts = state[0].keys()
    for _ in range(20):
        print()
    longest_task_name_length = max([len(task.__name__) for task in tasks])
    print(" " * longest_task_name_length + "  " + ", ".join(hosts))
    for task_index, task in enumerate(tasks):
        print(task.__name__.rjust(longest_task_name_length) + ": ", end="")
        for host_index, host_name in enumerate(hosts):
            column_distance = len(host_name)
            if host_index < len(hosts) - 1:
                column_distance += 2
            symbol = (
                state[task_index][host_name]
                if state[task_index][host_name] is not None
                else ""
            )
            print(symbol.ljust(column_distance), end="")
        print()


if __name__ == "__main__":
    main()
