"""robots 网络恢复的离线回归测试；所有请求和等待均使用 mock。"""

import json
import socket
import ssl
import unittest
import urllib.error
from unittest.mock import MagicMock, call, mock_open, patch

import scrape_malaysiayp as scraper
import supervise


class RobotsNetworkRecoveryTests(unittest.TestCase):
    def setUp(self):
        self.urlopen = self.enterContext(patch.object(scraper.urllib.request, "urlopen"))
        self.sleep = self.enterContext(patch.object(scraper.time, "sleep"))
        self.uniform = self.enterContext(patch.object(scraper.random, "uniform", return_value=0.25))
        self.warning = self.enterContext(patch.object(scraper.log, "warning"))

    def response(self, payload=b"User-agent: *\nAllow: /\n"):
        response = MagicMock()
        response.__enter__.return_value.read.return_value = payload
        return response

    def assert_closed_once(self):
        allowed, detail, raw = scraper.check_robots()
        self.assertIsNone(allowed)
        self.assertEqual(raw, "")
        self.assertFalse(detail.startswith("[transient-network]"))
        self.urlopen.assert_called_once()
        self.sleep.assert_not_called()
        self.uniform.assert_not_called()
        self.warning.assert_not_called()

    def test_dns_failure_then_success(self):
        self.urlopen.side_effect = [
            urllib.error.URLError(socket.gaierror(11001, "DNS 临时失败")),
            self.response(),
        ]
        allowed, detail, raw = scraper.check_robots(ua="RegressionBot", timeout=9)
        self.assertTrue(allowed)
        self.assertIn("Allow: /", raw)
        self.assertEqual(self.urlopen.call_count, 2)
        for args, kwargs in self.urlopen.call_args_list:
            self.assertEqual(args[0].get_header("User-agent"), "RegressionBot")
            self.assertEqual(kwargs, {"timeout": 9})
        self.sleep.assert_called_once_with(2.25)
        self.uniform.assert_called_once_with(0.0, 0.5)

    def test_continuous_dns_failure_at_most_three_requests(self):
        self.urlopen.side_effect = urllib.error.URLError(socket.gaierror(11001, "DNS 临时失败"))
        allowed, detail, raw = scraper.check_robots()
        self.assertIsNone(allowed)
        self.assertEqual(raw, "")
        self.assertTrue(detail.startswith("[transient-network]"))
        self.assertEqual(self.urlopen.call_count, 3)
        self.assertEqual(self.sleep.call_args_list, [call(2.25), call(4.25)])
        self.assertEqual(self.uniform.call_count, 2)

    def test_explicit_denial_is_not_retried(self):
        self.urlopen.return_value = self.response(b"User-agent: *\nDisallow: /\n")
        allowed, detail, raw = scraper.check_robots()
        self.assertFalse(allowed)
        self.assertIn("DISALLOW", detail)
        self.assertIn("Disallow: /", raw)
        self.urlopen.assert_called_once()
        self.sleep.assert_not_called()

    def test_http_403_is_not_retried(self):
        self.urlopen.side_effect = urllib.error.HTTPError(
            scraper.BASE + "/robots.txt", 403, "Forbidden", {}, None)
        self.assert_closed_once()

    def test_invalid_content_is_not_retried(self):
        for payload in (b"", b"<html>User-agent: *</html>", b"User-agent: *\n\xff",
                        b"User-agent: *\n" + b"x" * (1024 * 1024)):
            with self.subTest(payload_size=len(payload)):
                self.urlopen.reset_mock()
                self.urlopen.return_value = self.response(payload)
                self.assert_closed_once()

    def test_certificate_error_is_not_retried(self):
        self.urlopen.side_effect = urllib.error.URLError(
            ssl.SSLCertVerificationError(1, "证书校验失败"))
        self.assert_closed_once()

    def test_timeout_and_connection_errors_recover(self):
        for reason in (TimeoutError("连接超时"), ConnectionError("连接暂时失败")):
            with self.subTest(reason=type(reason).__name__):
                self.urlopen.reset_mock()
                self.sleep.reset_mock()
                self.urlopen.side_effect = [urllib.error.URLError(reason), self.response()]
                self.assertTrue(scraper.check_robots()[0])
                self.assertEqual(self.urlopen.call_count, 2)
                self.sleep.assert_called_once_with(2.25)

    def test_unclassified_url_error_is_not_retried(self):
        self.urlopen.side_effect = urllib.error.URLError("非临时错误")
        self.assert_closed_once()


    def test_direct_read_network_errors_recover(self):
        for reason in (TimeoutError("读取超时"), ConnectionError("读取连接断开")):
            with self.subTest(reason=type(reason).__name__):
                self.urlopen.reset_mock()
                self.sleep.reset_mock()
                response = self.response()
                response.__enter__.return_value.read.side_effect = reason
                self.urlopen.side_effect = [response, self.response()]
                self.assertTrue(scraper.check_robots()[0])
                self.assertEqual(self.urlopen.call_count, 2)
                self.sleep.assert_called_once_with(2.25)

    def test_direct_read_network_errors_are_bounded_and_logged(self):
        for reason in (TimeoutError("读取超时"), ConnectionError("读取连接断开")):
            with self.subTest(reason=type(reason).__name__):
                self.urlopen.reset_mock()
                self.sleep.reset_mock()
                self.warning.reset_mock()
                response = self.response()
                response.__enter__.return_value.read.side_effect = reason
                self.urlopen.return_value = response
                allowed, detail, raw = scraper.check_robots()
                self.assertIsNone(allowed)
                self.assertEqual(raw, "")
                self.assertTrue(detail.startswith("[transient-network]"))
                self.assertEqual(self.urlopen.call_count, 3)
                self.assertEqual(self.sleep.call_args_list, [call(2.25), call(4.25)])
                self.assertEqual(self.warning.call_count, 2)
                for attempt, entry in enumerate(self.warning.call_args_list, 1):
                    template, actual_attempt, error, wait = entry.args
                    self.assertIn("attempt=%d/3", template)
                    self.assertEqual(actual_attempt, attempt)
                    self.assertIs(error, reason)
                    self.assertEqual(wait, 2 ** attempt + 0.25)

    def test_direct_read_certificate_error_is_not_retried(self):
        response = self.response()
        response.__enter__.return_value.read.side_effect = ssl.SSLCertVerificationError(
            1, "证书校验失败")
        self.urlopen.return_value = response
        self.assert_closed_once()


class SupervisorNetworkClassificationTests(unittest.TestCase):
    def classify(self, job, rc=3):
        with patch("builtins.open", mock_open(read_data=json.dumps(job))) as opened:
            result = supervise.transient_robots_failure(rc)
        if rc == 3:
            opened.assert_called_once_with(supervise.JOB, encoding="utf-8")
        else:
            opened.assert_not_called()
        return result

    def test_transient_prefix_is_recognized(self):
        self.assertTrue(self.classify({"phase": "environment_error", "exit_code": 3,
                                       "last_error": "robots: [transient-network] DNS失败"}))

    def test_database_error_is_not_transient(self):
        self.assertFalse(self.classify({"phase": "environment_error", "exit_code": 3,
                                        "last_error": "database is locked"}))

    def test_robots_denial_is_not_transient(self):
        self.assertFalse(self.classify({"phase": "environment_error", "exit_code": 3,
                                        "last_error": "robots: 命中 DISALLOW: /"}))

    def test_non_three_exit_code_is_not_transient(self):
        job = {"phase": "environment_error", "exit_code": 3,
               "last_error": "[transient-network] DNS失败"}
        self.assertFalse(self.classify(job, rc=4))
        job["exit_code"] = 4
        self.assertFalse(self.classify(job))

    def test_corrupt_json_is_not_transient(self):
        with patch("builtins.open", mock_open(read_data="{损坏JSON")):
            self.assertFalse(supervise.transient_robots_failure(3))

    def test_wrong_phase_is_not_transient(self):
        self.assertFalse(self.classify({"phase": "fatal", "exit_code": 3,
                                        "last_error": "[transient-network] DNS失败"}))


class DaemonNetworkBudgetTests(unittest.TestCase):
    def setUp(self):
        self.state = {"delay": 3, "cooldown": 30}
        self.report = {"completion": False}
        self.enterContext(patch.object(supervise, "load_state", return_value=self.state))
        self.enterContext(patch.object(supervise, "process_alive", return_value={"alive": False}))
        self.enterContext(patch.object(supervise, "deferred_state", return_value={"ready": 1}))
        self.enterContext(patch.object(supervise, "build_report", return_value=self.report))
        self.enterContext(patch.object(supervise, "log"))
        self.enterContext(patch.object(supervise, "print_report"))
        self.heartbeat = self.enterContext(patch.object(supervise, "write_heartbeat"))
        self.alert = self.enterContext(patch.object(supervise, "raise_alert"))
        self.sleep = self.enterContext(patch.object(supervise.time, "sleep"))
        self.exists = self.enterContext(patch.object(supervise.os.path, "exists", return_value=False))
        self.run_chunk = self.enterContext(patch.object(
            supervise, "run_chunk", return_value=(3, {})))
        self.adapt = self.enterContext(patch.object(supervise, "adapt"))
        self.save_state = self.enterContext(patch.object(supervise, "save_state"))
        self.opened = self.enterContext(patch("builtins.open", mock_open()))

    def job(self, error):
        self.opened.return_value.read.return_value = json.dumps({
            "phase": "environment_error", "exit_code": 3, "last_error": error})

    def test_three_waits_then_fourth_failure_alerts(self):
        self.job("[transient-network] DNS失败")
        self.assertEqual(supervise.cmd_daemon(), 1)
        self.assertEqual(self.run_chunk.call_args_list, [call(self.state, daemon=True)] * 4)
        self.alert.assert_called_once()
        self.assertEqual(self.alert.call_args.args[1], 3)
        self.assertEqual(self.sleep.call_args_list, [call(5)] * 84)
        self.assertEqual(sum(item.args[0] for item in self.sleep.call_args_list), 60 + 120 + 240)
        self.assertEqual(sum(entry.kwargs.get("note") == "临时网络错误退避，等待重新检查 robots"
                             for entry in self.heartbeat.call_args_list), 84)
        self.adapt.assert_not_called()
        self.save_state.assert_not_called()

    def test_robots_denial_alerts_on_first_chunk(self):
        self.job("robots: 命中 DISALLOW: /")
        self.assertEqual(supervise.cmd_daemon(), 1)
        self.run_chunk.assert_called_once_with(self.state, daemon=True)
        self.alert.assert_called_once()
        self.sleep.assert_not_called()
        self.adapt.assert_not_called()
        self.save_state.assert_not_called()

    def test_database_error_alerts_on_first_chunk(self):
        self.job("database is locked")
        self.assertEqual(supervise.cmd_daemon(), 1)
        self.run_chunk.assert_called_once_with(self.state, daemon=True)
        self.alert.assert_called_once()
        self.sleep.assert_not_called()
        self.adapt.assert_not_called()
        self.save_state.assert_not_called()

    def test_stop_during_network_wait_exits_immediately(self):
        self.job("[transient-network] DNS失败")
        self.exists.side_effect = [False, False, True]
        self.assertEqual(supervise.cmd_daemon(), 0)
        self.run_chunk.assert_called_once_with(self.state, daemon=True)
        self.sleep.assert_called_once_with(5)
        self.alert.assert_not_called()
        self.assertEqual(self.exists.call_args_list, [call(supervise.STOP)] * 3)
        self.adapt.assert_not_called()
        self.save_state.assert_not_called()


if __name__ == "__main__":
    unittest.main()
