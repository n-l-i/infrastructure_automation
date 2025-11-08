from time import sleep
from modules.ping_and_become import ping_and_become
from playbooks._playbooks import Play


def ping_and_become_play() -> Play:
    steps = []
    for _ in range(3):
        steps.append(pp)
    return Play(
        name="ping_and_become",
        steps=steps,
        results={},
    )


def pp(host):
    # sleep(2)
    return ping_and_become(host)
