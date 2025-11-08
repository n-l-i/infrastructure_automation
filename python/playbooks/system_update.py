from modules.system_update import ensure_system_is_up_to_date
from playbooks._playbooks import Play


def system_update_play() -> Play:
    return Play(
        name="ensure_system_is_up_to_date",
        steps=[ensure_system_is_up_to_date],
        results={},
    )
