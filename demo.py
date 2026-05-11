# -*- encoding: utf-8 -*-
# @Author: SWHL
# @Contact: liekkaskono@163.com
from rapidtts import RapidTTS, SynthesisRequest

tts = RapidTTS()

text = "今天是2026-05-08，猪肉价格是￥13.5，增长6.3%。车牌号码：京A86F29。"
result = tts.synthesize(SynthesisRequest(text=text, voice="zm_010"))

save_path = "rapidtts_result.wav"
result.save(save_path)
print(save_path)
