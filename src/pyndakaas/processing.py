from .handler import Handler, handlers, Globber

import jinja2

from typing import Type
import shutil
from pathlib import Path


def process_dir(input_dir: Path, output_dir: Path, templates_path: Path = Path('templates')):
    template_env = jinja2.Environment(loader=jinja2.FileSystemLoader(templates_path))

    handlers: dict[Path, Handler] = {}
    process_dir_helper(input_dir, output_dir, Path('.'), template_env, handlers)

    for _, handler in handlers.items():
        handler.handle()


def process_dir_helper(input_root: Path, output_root: Path, rel_path: Path, template_env: jinja2.Environment,
                       handlers: dict[Path, Handler]) -> None:
    for input_path in (input_root / rel_path).iterdir():
        relative_input_path = input_path.relative_to(input_root)
        handler_class = get_handler_class(input_root / relative_input_path)

        if handler_class is not None:
            handler = handler_class(input_root, relative_input_path, output_root, template_env,
                                    Globber(handlers), Globber(handlers, relative_input_path))
            handlers[relative_input_path] = handler
            continue

        if input_path.is_dir():
            process_dir_helper(input_root, output_root, relative_input_path, template_env, handlers)
        else:
            output_path = output_root / relative_input_path
            output_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy(input_path, output_path)


def get_handler_class(source_path: Path) -> Type[Handler] | None:
    for handler in reversed(handlers):
        if handler.should_handle(source_path):
            return handler

    return None
