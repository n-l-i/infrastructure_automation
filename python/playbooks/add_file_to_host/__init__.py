from typing import Any
from playbooks._playbooks import Play
from modules._modules import Module, Module_function_result, State
from modules.file import file as _file
from utils.inventory import Host
from utils.ssh import Ssh_command_output, run_ssh_command as _run_ssh_command
from pathlib import Path


def play() -> Play:
    current_directory = Path(__file__).parent.resolve()
    return Play(
        name="Add file to host",
        modules=[
            _file({"src_text": "hello world", "dest_file_path": "~/hello.worlds"}),
        ],
        results={},
    )
