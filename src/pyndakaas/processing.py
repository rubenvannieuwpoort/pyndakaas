from .handler import Handler, handlers

import jinja2

from typing import Type
import shutil
from pathlib import Path


def process_dir(input_dir: Path, output_dir: Path, templates_path: Path = Path('templates')):
    template_env = jinja2.Environment(loader=jinja2.FileSystemLoader(templates_path))
    process_dir_helper(input_dir, output_dir, Path('.'), template_env)


def process_dir_helper(input_root: Path, output_root: Path, rel_path: Path, template_env: jinja2.Environment) -> None:
    handlers: list[tuple[Path, Handler]] = []
    for input_path in (input_root / rel_path).iterdir():
        path = input_path.relative_to(input_root)
        handler_class = get_handler_class(path)

        if handler_class is not None:
            handlers.append((path, handler_class(input_root, output_root, path, template_env)))
            continue

        if input_path.is_dir():
            process_dir_helper(input_root, output_root, path, template_env)
        else:
            output_path = output_root / path
            output_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy(input_path, output_path)

    front_matter = { p: h.front_matter for p, h in handlers }

    for path, handler in handlers:
        handler.handle(front_matter)


def get_handler_class(source_path: Path) -> Type[Handler] | None:
    for handler in reversed(handlers):
        if handler.should_handle(source_path):
            return handler

    return None
