from modules.ping_and_become import ping_and_become
from playbooks._playbooks import Play


def play() -> Play:
    steps = []
    for _ in range(3):
        steps.append(ping_and_become)
    return Play(
        name="ping_and_become",
        steps=steps,
        results={},
    )
