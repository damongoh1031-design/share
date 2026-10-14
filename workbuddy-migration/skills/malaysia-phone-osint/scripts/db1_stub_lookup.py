# -*- coding: utf-8 -*-
"""DB1 CallerID 桩件（stub）—— 用于在没有真实接口的情况下端到端测试 db1_batch.py 的控制流。

通过环境变量切换行为：
  STUB_MODE=healthy  (默认)  号码以 0 结尾 → 无名字；其余 → "Name-<后4位>"
  STUB_MODE=blocked          所有查询 → {"status": -5}
  STUB_MODE=flaky            前 STUB_OK_COUNT 次正常，之后全部 → {"status": -5}
  STUB_MODE=raise            所有查询抛异常（测 error 分支）

调用计数写在 STUB_COUNTER 指定的文件里（默认 <temp>/stub_counter.txt），
用来验证「被封后是否真的停止发请求」。
"""
import json
import os

_MODE = os.environ.get("STUB_MODE", "healthy")
_OK_COUNT = int(os.environ.get("STUB_OK_COUNT", "8"))
_COUNTER = os.environ.get("STUB_COUNTER", "stub_counter.txt")


def _bump():
    n = 0
    if os.path.exists(_COUNTER):
        try:
            n = int(open(_COUNTER).read().strip() or 0)
        except ValueError:
            n = 0
    n += 1
    open(_COUNTER, "w").write(str(n))
    return n


class CallerID:
    def start_callerid_check(self, phone, more=False):
        n = _bump()
        if _MODE == "raise":
            raise RuntimeError("stub: simulated network failure")
        if _MODE == "blocked" or (_MODE == "flaky" and n > _OK_COUNT):
            print('DataBase 1 Information: {"status": -5}')
            return
        if str(phone).endswith("0"):
            print("DataBase 1 Information: {}")
            return
        print("DataBase 1 Information: " + json.dumps(
            {"name": "Name-" + str(phone)[-4:], "belong_area": "Malaysia",
             "type_label": "", "report_count": ""}))
