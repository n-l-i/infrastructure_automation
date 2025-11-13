from dataclasses import dataclass
from modules._modules import Module, Module_function_result, State
from utils.inventory import Host


@dataclass
class Play:
    name: str
    modules: list[Module]
    results: dict[str : list[Module_function_result]]

    def run(this, host: Host):
        play_values = {}
        if host.host_id not in this.results:
            this.results[host.host_id] = []
        failed = False
        for module in this.modules:
            if failed:
                this.results[host.host_id].append(
                    Module_function_result(
                        state=State.SKIPPED,
                        return_value=None,
                        module_values={},
                    )
                )
                continue
            try:
                module_results = module.run(host)
            except Exception as error:
                print(error)
                failed = True
                this.results[host.host_id].append(
                    Module_function_result(
                        state=State.FAILED,
                        return_value=error,
                        module_values={},
                    )
                )
                raise error
            this.results[host.host_id] += module_results


@dataclass
class Facts_gathering:
    name: str
    module: Module
    results: dict[str : Module_function_result[Host | Exception | None]]

    def run(this, host: Host):
        if host.host_id not in this.results:
            this.results[host.host_id] = None
        try:
            this.results[host.host_id] = this.module.run(host)[0]
        except Exception as error:
            print(error)
            this.results[host.host_id] = Module_function_result(
                state=State.FAILED,
                return_value=error,
                module_values={},
            )
