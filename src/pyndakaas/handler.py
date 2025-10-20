from .front_matter_parsers import json_parser

from abc import ABC, abstractmethod
from fnmatch import fnmatch
from typing import Any, Callable
from pathlib import Path

import jinja2


class Handler(ABC):
    accept_missing_front_matter = True
    front_matter_parser: Callable[[str], tuple[dict[str, Any], str]] | None = json_parser
    template: str | None = None
    extension: str | None = '.html'

    input_root: Path
    rel_input_path: Path
    output_root: Path

    root: 'Globber'
    folder: 'Globber'

    template_env: jinja2.Environment | None

    front_matter: dict[str, Any] | None = None
    parameters: dict[str, Any] = {}

    def __init__(self, input_root: Path, rel_input_path: Path, output_root: Path,
                 template_env: jinja2.Environment | None, root: 'Globber', folder: 'Globber') -> None:
        self.input_root = input_root
        self.rel_input_path = rel_input_path
        self.output_root = output_root

        self.root = root
        self.folder = folder

        self.template_env = template_env

    @staticmethod
    @abstractmethod
    def should_handle(input_path: Path) -> bool:
        pass

    def handle(self):
        self.read_source()
        self.parse_front_matter()
        self.transform()
        self.initialize_parameters()
        self.set_output_path()
        self.render_output()
        self.write_output()

    def read_source(self):
        self.source = self.read_from_file(self.rel_input_path)

    def read_from_file(self, rel_path: Path) -> str:
        with open(self.input_root / rel_path) as f:
            return f.read()

    def parse_front_matter(self):
        if self.front_matter_parser is None:
            return

        try:
            self.front_matter, self.source = self.front_matter_parser.__func__(self.source)
        except Exception:
            if not self.accept_missing_front_matter:
                raise

    def transform(self) -> None:
        self.body: str | None = self.source

    def initialize_parameters(self):
        self.parameters['front_matter'] = self.front_matter
        self.parameters['body'] = self.body
        self.parameters['root'] = self.root
        self.parameters['folder'] = self.folder

    def set_output_path(self):
        self.rel_output_path = self.get_rel_output_path()

    def render_output(self):
        template_name = self.template
        if self.front_matter is not None and 'template' in self.front_matter:
            template_name = self.front_matter['template']

        template = None
        if template_name is not None:
            assert self.template_env is not None
            template = self.template_env.get_template(template_name + '.jinja')

        if template is not None:
            self.output = template.render(**self.parameters)
        else:
            self.output = self.body

    def write_output(self):
        if self.output is not None:
            output_path = self.output_root / self.rel_output_path
            assert not output_path.exists()
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, 'w') as f:
                f.write(self.output)

    def get_rel_output_path(self):
        return self.rel_input_path.with_suffix(self.extension or '')


class Globber:
    def __init__(self, handlers: dict[Path, Handler], root=None):
        self.handlers = handlers
        self.prefix = root or ''

    def glob(self, pat):
        return [h for p, h in self.handlers.items() if fnmatch(str(self.prefix / p), pat)]


handlers: list[Any] = []


def handler():
    def decorator(handler):
        handlers.append(handler)
        return handler
    return decorator
