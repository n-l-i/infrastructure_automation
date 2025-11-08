from pathlib import Path
from time import sleep as _sleep
from playbooks.ping_and_become import play as _ping_and_become_play
from playbooks.system_update import play as _system_update_play
from modules._modules import State
from modules.gather_facts import gather_facts as _gather_facts
from modules.ping import ping as _ping
from playbooks._playbooks import Facts_gathering, Play
from utils.inventory import Inventory, load_inventory as _load_inventory
from threading import Thread


def main():
    current_path = Path(__file__).resolve().parent
    inventory_path = current_path.joinpath("secrets/inventory.yml")
    inventory: Inventory = _load_inventory(inventory_path)

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
            steps=[_ping],
            results={},
        ),
        Facts_gathering(name="gather_facts", step=_gather_facts, results={}),
        _ping_and_become_play(),
        _system_update_play(),
    ]

    threads = {
        host_id: {"pending": [], "started": []} for host_id in inventory.keys()
    }
    state = [{host_id: [] for host_id in inventory.keys()} for _ in tasks]
    _print_state(state, tasks, host_names)
    for task_index, task in enumerate(tasks):
        for host_id, host in inventory.items():
            threads[host_id]["pending"].append(
                {
                    "task_index": task_index,
                    "thread": Thread(target=task.run, args=(host,)),
                }
            )
    while threads:
        _sleep(1)
        _print_state(state, tasks, host_names)
        for host_id, host in inventory.items():
            if host_id not in threads:
                continue
            if threads[host_id]["started"]:
                started_task_index = threads[host_id]["started"][0][
                    "task_index"
                ]
                task = tasks[started_task_index]
                if threads[host_id]["started"][0]["thread"].is_alive():
                    if isinstance(task, Play):
                        state[started_task_index][host_id] = [
                            result.state for result in task.results[host_id]
                        ]
                    continue
                if isinstance(task, Facts_gathering):
                    if task.results[host_id].state == State.UNCHANGED:
                        inventory[host_id] = task.results[host_id].return_value
                        for pending_thread_index in range(
                            len(threads[host_id]["pending"])
                        ):
                            pending_task_index = threads[host_id]["pending"][
                                pending_thread_index
                            ]["task_index"]
                            threads[host_id]["pending"][pending_thread_index][
                                "thread"
                            ] = Thread(
                                target=tasks[pending_task_index].run,
                                args=(inventory[host_id],),
                            )
                    state[started_task_index][host_id] = [
                        task.results[host_id].state
                    ]
                else:
                    state[started_task_index][host_id] = [
                        result.state for result in task.results[host_id]
                    ]
                threads[host_id]["started"].pop(0)
                continue
            if not threads[host_id]["pending"]:
                threads.pop(host_id)
                continue
            threads[host_id]["started"].append(
                threads[host_id]["pending"].pop(0)
            )
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
                task_index = threads[host_id]["started"][0]["task_index"]
                state[task_index][host_id] = [State.SKIPPED]
                threads[host_id]["started"].pop(0)
                continue
            threads[host_id]["started"][0]["thread"].start()
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
