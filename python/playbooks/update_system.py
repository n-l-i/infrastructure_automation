from dataclasses import asdict
import json
from modules.package_manager.index import (
    get_installed_packages,
    update_installed_packages,
)
from utils.inventory import Host


def play(host: Host):
    result: list[str] = update_installed_packages(host)
    print(json.dumps(result, indent=4))
