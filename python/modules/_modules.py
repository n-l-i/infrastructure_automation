from dataclasses import dataclass
from enum import Enum, auto
from typing import Any, Protocol
from copy import deepcopy

from utils.inventory import Host


class State(Enum):
    UNCHANGED = auto()
    CHANGED = auto()
    FAILED = auto()
    SKIPPED = auto()


@dataclass
class Module_function_result[T]():
    state: State
    return_value: T
    module_values: dict[str:Any]


class Module_step(Protocol):
    def __call__(
        self,
        host: Host,
        module_values: dict[str:Any],
    ) -> Module_function_result: ...


class Steps_function(Protocol):
    def __call__(
        self,
        host: Host,
        play_values: dict[str:Any],
    ) -> list[Module_step]: ...


@dataclass
class Module:
    name: str
    steps: Steps_function
    play_values: dict[str:Any]

    def run(this, host: Host) -> list[Module_function_result]:
        module_values = deepcopy(this.play_values)
        results = []
        failed = False
        steps = this.steps(host, this.play_values)
        for step in steps:
            if failed:
                results.append(
                    Module_function_result(
                        state=State.SKIPPED,
                        return_value=None,
                        module_values=module_values,
                    )
                )
                continue
            try:
                result = step(host, module_values)
            except Exception as error:
                print(error)
                failed = True
                results.append(
                    Module_function_result(
                        state=State.FAILED,
                        return_value=error,
                        module_values=module_values,
                    )
                )
                raise error
                continue
            results.append(result)
            module_values = result.module_values
        return results
