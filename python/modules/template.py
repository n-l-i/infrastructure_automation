from typing import Any
from jinja2 import Template
from modules._modules import Module, Module_function_result, State, Module_step
from modules.file import file as _file
from utils.inventory import Host


def template() -> Module:
    return Module(name="Template", steps=_steps)


def _steps(host: Host, play_values: dict[str:Any]) -> list[Module_step]:
    return [_render_template, _file]


def _render_template(
    host: Host,
    module_values: dict[str:Any],
) -> Module_function_result[None]:
    assert (
        "template_file_path" in module_values.keys()
        or "template_text" in module_values.keys()
    ), 'Module value "template_file_path" or "template_text" is required'
    assert (
        "template_file_path" in module_values.keys()
        and "template_text" in module_values.keys()
    ), 'Module values "template_file_path" and "template_text" cannot both be specified'
    assert (
        "dest_file_path" in module_values.keys()
    ), 'Module value "dest_file_path" is required'
    if "template_text" in module_values.keys():
        jinja_template_text = module_values["template_text"].strip()
    else:
        with open(module_values["template_file_path"], "r") as file_obj:
            jinja_template_text = file_obj.read()
    jinja_template = Template(jinja_template_text)
    rendered_template = jinja_template.render(module_values)

    module_values["src_text"] = rendered_template
    return Module_function_result(
        state=State.UNCHANGED, return_value=None, module_values=module_values
    )
