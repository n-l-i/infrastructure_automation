from dataclasses import dataclass, asdict
import yaml
from pathlib import Path


@dataclass
class Host:
    host_name: str
    username: str
    ip_address: str
    ssh_port: int
    ssh_key_path: Path
    groups: list[str]


@dataclass
class Inventory:
    hosts: dict[str, Host]


def _get_global_vars(inventory, inventory_data, attributes, current_path):
    for host_group_name, host_group_data in inventory_data.items():
        for host_name, host_inventory_data in host_group_data.get(
            "hosts", {}
        ).items():
            # Extract host and connection data
            global_vars = inventory_data.get("vars", {})

            host_data = (
                asdict(inventory[host_name]) if host_name in inventory else {}
            )

            host_data["host_name"] = host_name
            if "groups" not in host_data:
                host_data["groups"] = []
            if host_group_name not in host_data["groups"]:
                host_data["groups"].append(host_group_name)
            for attribute_name, attribute_inventory_name in attributes.items():
                if global_vars and attribute_inventory_name in global_vars:
                    host_data[attribute_name] = global_vars[
                        attribute_inventory_name
                    ]
            inventory[host_name] = Host(
                host_data.get("host_name", None),
                host_data.get("username", None),
                host_data.get("ip_address", None),
                host_data.get("ssh_port", None),
                (
                    current_path.joinpath(host_data["ssh_key_path"])
                    if "ssh_key_path" in host_data and host_data["ssh_key_path"]
                    else None
                ),
                host_data.get("groups", None),
            )
    return inventory


def _get_group_vars(inventory, inventory_data, attributes, current_path):
    for host_group_name, host_group_data in inventory_data.items():
        for host_name, host_inventory_data in host_group_data.get(
            "hosts", {}
        ).items():
            # Extract host and connection data
            global_vars = host_group_data.get("vars", {})

            host_data = (
                asdict(inventory[host_name]) if host_name in inventory else {}
            )

            host_data["host_name"] = host_name
            if "groups" not in host_data:
                host_data["groups"] = []
            if host_group_name not in host_data["groups"]:
                host_data["groups"].append(host_group_name)
            for attribute_name, attribute_inventory_name in attributes.items():
                if global_vars and attribute_inventory_name in global_vars:
                    host_data[attribute_name] = global_vars[
                        attribute_inventory_name
                    ]
            inventory[host_name] = Host(
                host_data["host_name"],
                host_data["username"],
                host_data["ip_address"],
                host_data["ssh_port"],
                current_path.joinpath(host_data["ssh_key_path"]),
                host_data["groups"],
            )
    return inventory


def _get_host_vars(inventory, inventory_data, attributes, current_path):
    for host_group_name, host_group_data in inventory_data.items():
        for host_name, host_inventory_data in host_group_data.get(
            "hosts", {}
        ).items():
            # Extract host and connection data
            global_vars = host_group_data.get("vars", {})

            host_data = (
                asdict(inventory[host_name]) if host_name in inventory else {}
            )

            host_data["host_name"] = host_name
            if "groups" not in host_data:
                host_data["groups"] = []
            if host_group_name not in host_data["groups"]:
                host_data["groups"].append(host_group_name)
            for attribute_name, attribute_inventory_name in attributes.items():
                if (
                    host_inventory_data
                    and attribute_inventory_name in host_inventory_data
                ):
                    host_data[attribute_name] = host_inventory_data[
                        attribute_inventory_name
                    ]
            inventory[host_name] = Host(
                host_data["host_name"],
                host_data["username"],
                host_data["ip_address"],
                host_data["ssh_port"],
                current_path.joinpath(host_data["ssh_key_path"]),
                host_data["groups"],
            )
    return inventory


def load_inventory(path: Path) -> Inventory:
    current_path = Path(__file__).resolve().parent.parent

    # Load the inventory
    with open(current_path.joinpath(path), "r") as f:
        inventory_data = yaml.safe_load(f)

    attributes = {
        "username": "ansible_user",
        "ip_address": "ansible_host",
        "ssh_port": "ansible_ssh_port",
        "ssh_key_path": "ansible_private_key_file",
    }
    inventory = {}

    inventory = _get_global_vars(
        inventory, inventory_data, attributes, current_path
    )
    inventory = _get_group_vars(
        inventory, inventory_data, attributes, current_path
    )
    inventory = _get_host_vars(
        inventory, inventory_data, attributes, current_path
    )

    # for inventory_item in inventory.values():
    #    inventory_item.ssh_key_path = str(inventory_item.ssh_key_path)
    #    print(json.dumps(asdict(inventory_item), indent=4))
    return inventory
