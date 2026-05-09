# -*- encoding: utf-8 -*-
# @Author: SWHL
# @Contact: liekkaskono@163.com
from rapidtts import RapidTTS, SynthesisRequest, TTSModel

tts = RapidTTS(model=TTSModel.MELO_ONNX)

text = "2026年5月8日，京A86F29 车主在 302 房间使用手机号 13800138000 输入验证码 123456、支付 110 元，圆周率取值 3.14 并拨打 110 报警电话。"
result = tts.synthesize(SynthesisRequest(text=text))

save_path = "melo_onnx_result.wav"
result.save(save_path)
print(save_path)
