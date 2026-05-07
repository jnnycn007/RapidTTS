# -*- encoding: utf-8 -*-
# @Author: SWHL
# @Contact: liekkaskono@163.com
class AbstractKernel:
    def __init__(self, *args, **kwargs):
        pass

    def g2p(self, text, **kwargs):
        raise NotImplementedError()

    def text_normalize(self, text):
        raise NotImplementedError()
