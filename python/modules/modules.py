from dataclasses import dataclass
from typing import Any


@dataclass
class Module_function_result[T]():
    changed: bool
    return_value: T
