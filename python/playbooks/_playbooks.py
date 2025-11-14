from dataclasses import dataclass
from typing import Callable, Self
from modules._modules import Module, Module_function_result, State
from utils.inventory import Host


type Facts_gathering_function = Callable[..., Host]

type Play_function = Callable[[Self, Host], None]


@dataclass
class Play:
    name: str
    run: Play_function
    results: dict[str : list[Module_function_result]]
