# -*- encoding: utf-8 -*-
# @Author: SWHL
# @Contact: liekkaskono@163.com
from abc import ABC, abstractmethod
from typing import Any

from .request import SynthesisRequest
from .response import SynthesisResponse


class BaseTTSBackend(ABC):
    @abstractmethod
    def preprocess(self, request: SynthesisRequest) -> Any:
        pass

    @abstractmethod
    def infer(self, *args, **kwargs) -> Any:
        pass

    @abstractmethod
    def postprocess(self, *args, **kwargs) -> SynthesisResponse:
        pass

    def synthesize(self, request: SynthesisRequest) -> SynthesisResponse:
        model_input = self.preprocess(request)
        model_output = self.infer(model_input)
        return self.postprocess(model_output, request.sample_rate, request.speed)
