from dataclasses import dataclass
from modules._modules import Module_function_result, State
from utils.inventory import Host


@dataclass
class Play:
    name: str
    steps: list[function]
    results: dict[str : list[Module_function_result]]

    def run(this, host: Host):
        if host.host_id not in this.results:
            this.results[host.host_id] = []
        failed = False
        for step in this.steps:
            if failed:
                this.results[host.host_id].append(
                    Module_function_result(
                        state=State.SKIPPED,
                        return_value=None,
                    )
                )
                continue
            try:
                this.results[host.host_id].append(step(host))
            except Exception as error:
                print(error)
                failed = True
                this.results[host.host_id].append(
                    Module_function_result(
                        state=State.FAILED,
                        return_value=error,
                    )
                )
                raise error


@dataclass
class Facts_gathering:
    name: str
    step: function
    results: dict[str : Module_function_result[Host, Exception, None]]

    def run(this, host: Host):
        if host.host_id not in this.results:
            this.results[host.host_id] = None
        try:
            this.results[host.host_id] = this.step(host)
        except Exception as error:
            print(error)
            this.results[host.host_id] = Module_function_result(
                state=State.FAILED,
                return_value=error,
            )
