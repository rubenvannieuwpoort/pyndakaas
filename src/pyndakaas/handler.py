from abc import ABC, abstractmethod
from fnmatch import fnmatch
from typing import Any, Callable
from pathlib import Path

import jinja2

from .front_matter_parsers import json_parser


class Handler(ABC):
    front_matter_parser: Callable[[str], tuple[dict[str, Any], str]] | None = json_parser

    input_root: Path
    output_root: Path
    path: Path

    template_env: jinja2.Environment | None

    source: str
    front_matter: dict[str, Any] | None

    def __init__(self, input_root: Path, output_root: Path, rel_path: Path, template_env: jinja2.Environment | None) -> None:
        path = input_root / rel_path
        assert path.exists()

        self.input_root = input_root
        self.output_root = output_root
        self.path = path

        self.template_env = template_env

        with open(path) as f:
            input = f.read()

        if self.front_matter_parser is not None:
            self.front_matter, self.source = self.front_matter_parser.__func__(input)
        else:
            self.front_matter = None
            self.source = self.source

    @staticmethod
    @abstractmethod
    def should_handle(input_path: Path) -> bool:
        pass

    def handle(self, front_matter) -> None:  # TODO: types
        template_name = self.template()
        assert template_name is None or self.template_env is not None

        template = None
        if template_name is not None:
            assert self.template_env is not None
            template = self.template_env.get_template(template_name + '.jinja')

        body = self.body()

        folder_glob = lambda pat: [fm for p, fm in front_matter if fnmatch(str(p), str(self.input_root / pat))]
        root_glob = lambda pat: [fm for p, fm in front_matter if fnmatch(str(p), pat)]
        output = template.render(self.front_matter, body=body, folder={'glob': folder_glob}, root={'glob': root_glob}) if template is not None else body

        output_path = self.output_path()
        assert not output_path.exists()

        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w') as f:
            f.write(output)

    def output_path(self) -> Path:
        return self.output_root / self.path.relative_to(self.input_root).with_suffix(self.suffix() or '')

    def suffix(self) -> str:
        return '.html'

    def template(self) -> str | None:
        return None

    def body(self) -> str:
        return self.source


handlers: list[Any] = []

def handler():
    def decorator(handler):
        handlers.append(handler)
        return handler
    return decorator
