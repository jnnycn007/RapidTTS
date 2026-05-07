# -*- encoding: utf-8 -*-
# @Author: SWHL
# @Contact: liekkaskono@163.com

import numpy as np
import onnxruntime as ort
from tokenizers import Tokenizer


class BertInfer:
    def __init__(
        self,
        model_root_dir,
        onnx_providers: list,
        session_opts=None,
        tokenizer: Tokenizer = None,
    ):
        bert_lml_model_path = model_root_dir / "bert_lml_model.onnx"
        self.bert_session = ort.InferenceSession(
            str(bert_lml_model_path),
            sess_options=session_opts,
            providers=onnx_providers,
        )
        self.tokenizer = tokenizer

    def get_bert_feature(self, text, word2ph):
        inputs = self.tokenizer.encode(text, add_special_tokens=True)
        res = self.bert_session.run(
            None,
            {
                "input_ids": np.array([inputs.ids]),
                "token_type_ids": np.array([inputs.type_ids]),
                "attention_mask": np.array([inputs.attention_mask]),
            },
        )[0][0]
        phone_level_feature = []
        for i in range(len(word2ph)):
            repeat_feature = np.repeat(np.array([res[i]]), word2ph[i], axis=0)
            phone_level_feature.append(repeat_feature)

        phone_level_feature = np.concatenate(phone_level_feature, axis=0)
        return phone_level_feature.T
