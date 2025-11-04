from dataclasses import asdict
import json
from modules.system_update.__index__ import (
    ensure_system_is_up_to_date,
)
from utils.inventory import Host


def play(host: Host):
    result: list[str] = ensure_system_is_up_to_date(host)
    print(json.dumps(asdict(result), indent=4))
