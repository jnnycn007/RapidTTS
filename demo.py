# -*- encoding: utf-8 -*-
# @Author: SWHL
# @Contact: liekkaskono@163.com
from rapidtts import RapidTTS, SynthesisRequest, TTSModel

tts = RapidTTS(model=TTSModel.MELO_ONNX)

text = "我最近在学习machine learning，希望能够在未来的artificial intelligence领域有所建树。"
result = tts.synthesize(SynthesisRequest(text=text))

save_path = "outputs/melo_onnx_result.wav"
result.save(save_path)
print(save_path)
