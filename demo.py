# -*- encoding: utf-8 -*-
# @Author: SWHL
# @Contact: liekkaskono@163.com
from rapidtts import RapidTTS, SynthesisRequest, TextNormalizerType, TTSModel

text_normalizer_type = TextNormalizerType.LEGACY
tts = RapidTTS(model=TTSModel.MELO_ONNX, text_normalizer_type=text_normalizer_type)

text = "2026 年 5 月 8 日，京 A86F29 车主在 302 房间使用手机号 13800138000 输入验证码 123456、支付 110 元，圆周率取值 3.14 并拨打 110 报警电话。"
result = tts.synthesize(SynthesisRequest(text=text))

save_path = f"outputs/melo_onnx_result_{text_normalizer_type.value}.wav"
result.save(save_path)
print(save_path)
