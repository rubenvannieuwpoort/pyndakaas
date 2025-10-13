import json
from typing import Any


def json_parser(input: str) -> tuple[dict[str, Any], str]:
    front_matter, idx = json.JSONDecoder().raw_decode(input)
    source = input[idx:].lstrip('\n')

    return front_matter, source
