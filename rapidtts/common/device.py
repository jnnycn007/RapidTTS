# -*- encoding: utf-8 -*-
# @Author: SWHL
# @Contact: liekkaskono@163.com
from typing import Optional


def normalize_execution_provider(device: Optional[str]) -> str:
    if not device:
        return "CPUExecutionProvider"

    device = device.strip()

    if device.endswith("ExecutionProvider"):
        return device

    mapping = {
        "cpu": "CPUExecutionProvider",
        "cuda": "CUDAExecutionProvider",
        "gpu": "CUDAExecutionProvider",
    }

    key = device.lower()
    if key in mapping:
        return mapping[key]

    return f"{device.upper()}ExecutionProvider"
