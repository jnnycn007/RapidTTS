# -*- encoding: utf-8 -*-
# @Author: SWHL
# @Contact: liekkaskono@163.com
from pathlib import Path
from typing import Any, Union

from ..backends.melo_onnx.backend import MeloONNXBackend
from ..common.logger import set_logger_enabled
from .config import get_backend_init_defaults, get_backend_request_defaults, load_config
from .model_assets import ensure_model_assets
from .request import SynthesisRequest
from .response import SynthesisResponse
from .typings import TTSModel


class RapidTTS:
    def __init__(
        self,
        model: TTSModel,
        config_path: Union[str, Path, None] = None,
        enable_log: bool = True,
        **kwargs: Any,
    ) -> None:
        set_logger_enabled(enable_log)
        self.cfg = load_config(config_path)

        backend_name = model.value
        init_defaults = get_backend_init_defaults(self.cfg, backend_name)
        request_defaults = get_backend_request_defaults(self.cfg, backend_name)

        init_kwargs = {
            **init_defaults,
            **kwargs,
            "request_defaults": request_defaults,
        }
        if "model_root_dir" not in kwargs:
            init_kwargs["model_root_dir"] = ensure_model_assets(backend_name)

        self.backend = self.create_backend(model, **init_kwargs)

    def create_backend(self, model: TTSModel, **kwargs: Any) -> Any:
        if model == TTSModel.MELO_ONNX:
            return MeloONNXBackend(**kwargs)
        raise ValueError(f"Unsupported model: {model}")

    def synthesize(self, request: SynthesisRequest) -> SynthesisResponse:
        return self.backend.synthesize(request)
