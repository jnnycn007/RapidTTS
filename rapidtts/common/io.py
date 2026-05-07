# -*- encoding: utf-8 -*-
# @Author: SWHL
# @Contact: liekkaskono@163.com
import json
from pathlib import Path
from typing import Union


def load_json(file_path: Union[str, Path]) -> dict:
    if not Path(file_path).exists():
        raise FileNotFoundError(f'Can not found the file "{file_path}"')

    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)
