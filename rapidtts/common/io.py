# -*- encoding: utf-8 -*-
# @Author: SWHL
# @Contact: liekkaskono@163.com
import json
from pathlib import Path
from typing import List, Union


def load_json(file_path: Union[str, Path]) -> dict:
    if not Path(file_path).exists():
        raise FileNotFoundError(f'Can not found the file "{file_path}"')

    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)


def read_txt(txt_path: Union[Path, str]) -> List[str]:
    with open(txt_path, "r", encoding="utf-8") as f:
        data = [v.rstrip("\n") for v in f]
    return data
