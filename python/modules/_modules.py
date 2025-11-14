from dataclasses import dataclass
from enum import Enum, auto
from typing import Any, Callable, Protocol
from copy import deepcopy

from utils.inventory import Host


type Module = Callable[..., list[Module_function_result]]

type Module_results = list[Module_function_result]


class State(Enum):
    UNCHANGED = auto()
    CHANGED = auto()
    FAILED = auto()
    SKIPPED = auto()


@dataclass
class Module_function_result[T]():
    state: State
    return_value: T
