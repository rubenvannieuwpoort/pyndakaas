from abc import ABC, abstractmethod
from fnmatch import fnmatch
from typing import Any, Callable
from pathlib import Path

import jinja2

from .front_matter_parsers import json_parser


class Handler(ABC):
    front_matter_parser: Callable[[str], tuple[dict[str, Any], str]] | None = json_parser

    input_root: Path
    rel_input_path: Path
    output_root: Path
    rel_output_path: Path

    template_env: jinja2.Environment | None

    source: str | None
    front_matter: dict[str, Any] | None

    def __init__(self, input_root: Path, output_root: Path, rel_input_path: Path,
                 template_env: jinja2.Environment | None) -> None:
        self.input_root = input_root
        self.rel_input_path = rel_input_path
        self.output_root = output_root
        self.rel_output_path = self.output_path()

        self.template_env = template_env
        self.preprocess()

    # set front_matter and source
    def preprocess(self) -> None:
        input_path = self.input_root / self.rel_input_path

        input = None
        if input_path.exists() and input_path.is_file():
            with open(input_path) as f:
                input = f.read()

        if input is not None and self.front_matter_parser is not None:
            # see https://github.com/python/mypy/issues/14123
            self.front_matter, self.source = self.front_matter_parser.__func__(input)  # type: ignore[attr-defined]
        else:
            self.front_matter = None
            self.source = input

    @staticmethod
    @abstractmethod
    def should_handle(input_path: Path) -> bool:
        pass

    def handle(self, metadata) -> None:  # TODO: types
        template_name = self.template()

        if self.front_matter is not None and 'template' in self.front_matter:
            template_name = self.front_matter['template']

        assert template_name is None or self.template_env is not None

        template = None
        if template_name is not None:
            assert self.template_env is not None
            template = self.template_env.get_template(template_name + '.jinja')

        body = self.body()

        output: str | None
        if template is not None:
            root = Globber(metadata)
            folder = Globber(metadata, self.rel_input_path)
            output = template.render(front_matter=self.front_matter, body=body, folder=folder, root=root)
        else:
            output = body

        output_path = self.output_root / self.rel_output_path
        assert not output_path.exists()

        if output is not None:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, 'w') as f:
                f.write(output)

    def output_path(self) -> Path:
        return self.rel_input_path.with_suffix(self.suffix() or '')

    def suffix(self) -> str:
        return '.html'

    def template(self) -> str | None:
        return None

    def body(self) -> str | None:
        return self.source


class Metadata:
    input_path: Path
    output_path: Path
    front_matter: dict[str, Any]

    def __init__(self, input_path: Path, output_path: Path, front_matter) -> None:
        self.input_path = input_path
        self.output_path = output_path
        self.front_matter = front_matter


class Globber:
    def __init__(self, metadata, root=None):
        self.metadata = metadata
        self.prefix = root or ''

    def glob(self, pat):
        return [md for md in self.metadata if fnmatch(str(self.prefix / md.input_path), pat)]


handlers: list[Any] = []


def handler():
    def decorator(handler):
        handlers.append(handler)
        return handler
    return decorator
