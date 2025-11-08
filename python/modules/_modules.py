from dataclasses import dataclass
from enum import Enum, auto


class State(Enum):
    UNCHANGED = auto()
    CHANGED = auto()
    FAILED = auto()
    SKIPPED = auto()


@dataclass
class Module_function_result[T]():
    state: State
    return_value: T
