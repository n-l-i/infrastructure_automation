from pathlib import Path
from time import sleep
from playbooks.ping_and_become import ping_and_become_play
from playbooks.system_update import system_update_play
from modules._modules import State
from modules.gather_facts import gather_facts
from modules.ping import ping
from playbooks._playbooks import Facts_gathering, Play
from utils.inventory import Inventory, load_inventory


def main():
    current_path = Path(__file__).resolve().parent
    inventory_path = current_path.joinpath("secrets/inventory.yml")
    inventory: Inventory = load_inventory(inventory_path)

    failing_host_ids = set()
    for failing_host_name in (
        "ubuntu_guest_1",
        "ubuntu_guest_4",
        "mikrotik_router",
    ):
        failing_host_id = None
        for host in inventory.values():
            if host.host_name != failing_host_name:
                continue
            failing_host_ids.add(host.host_id)
    for failing_host_id in failing_host_ids:
        inventory.pop(failing_host_id)

    host_names = tuple(
        [inventory[host_id].host_name for host_id in inventory.keys()]
    )
    tasks = [
        Play(
            name="ping",
            steps=[ping],
            results={},
        ),
        ping_and_become_play(),
        Facts_gathering(name="gather_facts", step=gather_facts, results={}),
        ping_and_become_play(),
        system_update_play(),
    ]

    state = [{host_id: [] for host_id in inventory.keys()} for _ in tasks]
    _print_state(state, tasks, host_names)
    for i, task in enumerate(tasks):
        for host_id, host in inventory.items():
            failed = any(
                [
                    result[host_id]
                    and any(
                        [
                            step_result == State.FAILED
                            for step_result in result[host_id]
                        ]
                    )
                    for result in state
                ]
            )
            if failed:
                state[i][host_id] = [State.SKIPPED]
            elif isinstance(task, Facts_gathering):
                task.run(host)
                while not task.results[host_id]:
                    sleep(0.1)
                if task.results[host_id].state == State.UNCHANGED:
                    inventory[host_id] = task.results[host_id].return_value
                state[i][host_id] = [task.results[host_id].state]
            else:
                task.run(host)
                while not task.results[host_id]:
                    sleep(0.1)
                state[i][host_id] = [
                    result.state for result in task.results[host_id]
                ]
            _print_state(state, tasks, host_names)


def _print_state(state, tasks: list[Play], host_names):
    symbols = {
        State.UNCHANGED: "0",
        State.CHANGED: "1",
        State.FAILED: "X",
        State.SKIPPED: "-",
        None: " ",
    }
    host_ids = tuple(state[0].keys())
    for _ in range(20):
        print()
    longest_task_name_length = max([len(task.name) for task in tasks])
    print(" " * longest_task_name_length + "  " + ", ".join(host_names))
    for task_index, task in enumerate(tasks):
        print(task.name.rjust(longest_task_name_length) + ": ", end="")
        for host_index, host_name in enumerate(host_names):
            column_distance = len(host_name)
            if host_index < len(host_names) - 1:
                column_distance += 2
            result_string = ""
            for result in state[task_index][host_ids[host_index]]:
                result_string += symbols[result]
            print(result_string.ljust(column_distance), end="")
        print()


if __name__ == "__main__":
    main()
