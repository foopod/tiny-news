import unittest
import sys
import os
from unittest.mock import patch, Mock

import requests

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import http_utils
from http_utils import get_cached_rss, get_cached_json, _request_within_budget, REQUEST_BUDGET, MAX_CACHE_AGE
from rss import getRSS, NewsType
from util import get_weather

RSS_URL = "https://example.com/rss"
JSON_URL = "https://example.com/data"
WEATHER_URL = "https://api.open-meteo.com/v1/forecast"


def rss_response(title):
    response = Mock(status_code=200)
    response.content = f"<rss><channel><item><title>{title}</title><description>d</description></item></channel></rss>".encode()
    response.raise_for_status.return_value = None
    return response


def json_response(data):
    response = Mock(status_code=200)
    response.json.return_value = data
    response.raise_for_status.return_value = None
    return response


class FakeClock:
    """Stands in for http_utils._now and time.sleep so tests control time."""

    def __init__(self):
        self.now = 1000.0

    def __call__(self):
        return self.now

    def sleep(self, seconds):
        self.now += seconds


class CachingTestCase(unittest.TestCase):

    def setUp(self):
        http_utils._cache.clear()
        self.clock = FakeClock()
        patches = [
            patch('http_utils._now', self.clock),
            patch('http_utils.time.sleep', side_effect=self.clock.sleep),
            patch('http_utils.requests.get'),
        ]
        mocks = [p.start() for p in patches]
        self.mock_sleep, self.mock_get = mocks[1], mocks[2]
        for p in patches:
            self.addCleanup(p.stop)


class TestLiveFirstFetching(CachingTestCase):

    def test_success_returns_live_data(self):
        self.mock_get.return_value = rss_response("Live")
        result = get_cached_rss(RSS_URL)
        self.assertEqual(result["rss"]["channel"]["item"]["title"], "Live")

    def test_always_fetches_live_even_with_fresh_cache(self):
        self.mock_get.return_value = rss_response("First")
        get_cached_rss(RSS_URL)

        self.clock.now += 60
        self.mock_get.return_value = rss_response("Second")
        result = get_cached_rss(RSS_URL)

        self.assertEqual(self.mock_get.call_count, 2)
        self.assertEqual(result["rss"]["channel"]["item"]["title"], "Second")

    def test_failure_with_recent_cache_uses_cache(self):
        self.mock_get.return_value = rss_response("Cached")
        get_cached_rss(RSS_URL)

        self.clock.now += 30 * 60
        self.mock_get.side_effect = requests.exceptions.ConnectionError("down")
        result = get_cached_rss(RSS_URL)

        self.assertEqual(result["rss"]["channel"]["item"]["title"], "Cached")

    def test_failure_with_cache_at_max_age_uses_cache(self):
        self.mock_get.return_value = json_response({"value": 1})
        get_cached_json(JSON_URL)

        self.clock.now += MAX_CACHE_AGE
        self.mock_get.side_effect = requests.exceptions.ConnectionError("down")
        # the failed attempts and backoff take time too, so stop the clock moving on sleep
        self.mock_sleep.side_effect = None
        self.assertEqual(get_cached_json(JSON_URL), {"value": 1})

    def test_failure_with_old_cache_returns_placeholder(self):
        self.mock_get.return_value = rss_response("Too old")
        get_cached_rss(RSS_URL)

        self.clock.now += 3 * 60 * 60
        self.mock_get.side_effect = requests.exceptions.ConnectionError("down")
        result = get_cached_rss(RSS_URL)

        self.assertEqual(result["rss"]["channel"]["item"][0]["title"], "Failed to fetch news")
        self.assertIn("down", result["rss"]["channel"]["item"][0]["description"])

    def test_failure_with_no_cache_returns_placeholder(self):
        self.mock_get.side_effect = Exception("Network error")
        result = get_cached_rss(RSS_URL)
        self.assertEqual(result["rss"]["channel"]["item"][0]["title"], "Failed to fetch news")

    def test_failures_are_not_cached(self):
        self.mock_get.side_effect = requests.exceptions.ConnectionError("down")
        get_cached_rss(RSS_URL)
        self.assertEqual(http_utils._cache, {})

        self.mock_get.side_effect = None
        self.mock_get.return_value = rss_response("Recovered")
        result = get_cached_rss(RSS_URL)
        self.assertEqual(result["rss"]["channel"]["item"]["title"], "Recovered")

    def test_bad_response_body_falls_back_to_cache(self):
        self.mock_get.return_value = rss_response("Good")
        get_cached_rss(RSS_URL)

        broken = Mock(status_code=200, content=b"<rss><not-closed>")
        broken.raise_for_status.return_value = None
        self.mock_get.return_value = broken
        result = get_cached_rss(RSS_URL)
        self.assertEqual(result["rss"]["channel"]["item"]["title"], "Good")

    def test_client_error_is_not_retried(self):
        response = Mock(status_code=404)
        response.raise_for_status.side_effect = requests.exceptions.HTTPError("404")
        self.mock_get.return_value = response

        result = get_cached_json(JSON_URL)

        self.assertEqual(self.mock_get.call_count, 1)
        self.assertIn("error", result)

    def test_cache_is_keyed_by_params(self):
        self.mock_get.return_value = json_response({"city": "a"})
        get_cached_json(WEATHER_URL, {"latitude": 1})
        self.mock_get.return_value = json_response({"city": "b"})
        get_cached_json(WEATHER_URL, {"latitude": 2})

        self.mock_get.side_effect = requests.exceptions.ConnectionError("down")
        self.assertEqual(get_cached_json(WEATHER_URL, {"latitude": 1}), {"city": "a"})
        self.assertEqual(get_cached_json(WEATHER_URL, {"latitude": 2}), {"city": "b"})

    def test_params_are_sent_with_the_request(self):
        self.mock_get.return_value = json_response({})
        get_cached_json(WEATHER_URL, {"latitude": 1})
        self.assertEqual(self.mock_get.call_args.kwargs["params"], {"latitude": 1})

    def test_weather_failure_without_cache_returns_weather_fallback(self):
        self.mock_get.side_effect = requests.exceptions.ConnectionError("down")
        result = get_cached_json(WEATHER_URL, {"latitude": 1})
        self.assertEqual(result["daily"]["temperature_2m_max"], ["--"])

    def test_callers_cannot_modify_cached_data(self):
        self.mock_get.return_value = json_response({"daily": {"temps": [1, 2]}})
        first = get_cached_json(JSON_URL)
        first["daily"]["temps"] = ["changed"]

        self.mock_get.side_effect = requests.exceptions.ConnectionError("down")
        second = get_cached_json(JSON_URL)
        second["daily"]["temps"].append(3)
        third = get_cached_json(JSON_URL)

        self.assertEqual(third["daily"]["temps"], [1, 2])


class TestRequestBudget(CachingTestCase):

    def test_retries_with_backoff_then_succeeds(self):
        ok = Mock(status_code=200)
        self.mock_get.side_effect = [
            requests.exceptions.ConnectionError("Connection error"),
            requests.exceptions.Timeout("Timeout"),
            ok,
        ]

        result = _request_within_budget(JSON_URL)

        self.assertEqual(result, ok)
        self.assertEqual(self.mock_get.call_count, 3)
        self.assertEqual([c.args[0] for c in self.mock_sleep.call_args_list], [1, 2])

    def test_server_errors_are_retried(self):
        ok = Mock(status_code=200)
        self.mock_get.side_effect = [Mock(status_code=503), ok]
        self.assertEqual(_request_within_budget(JSON_URL), ok)

    def test_gives_up_after_max_retries(self):
        self.mock_get.side_effect = requests.exceptions.ConnectionError("Persistent error")

        with self.assertRaises(requests.exceptions.ConnectionError):
            _request_within_budget(JSON_URL)

        self.assertEqual(self.mock_get.call_count, 3)
        self.assertEqual(self.mock_sleep.call_count, 2)

    def test_attempt_timeout_is_the_time_left(self):
        def slow_failure(*args, **kwargs):
            self.clock.now += 10
            raise requests.exceptions.Timeout("slow")

        self.mock_get.side_effect = slow_failure

        with self.assertRaises(requests.exceptions.Timeout):
            _request_within_budget(JSON_URL)

        timeouts = [c.kwargs["timeout"] for c in self.mock_get.call_args_list]
        self.assertEqual(timeouts[0], REQUEST_BUDGET)
        self.assertTrue(all(t <= REQUEST_BUDGET for t in timeouts))
        # 10s first attempt + 1s backoff leaves 4s, so a second attempt but no third
        self.assertEqual(timeouts, [REQUEST_BUDGET, REQUEST_BUDGET - 11])

    def test_slow_network_falls_back_to_cache_within_budget(self):
        self.mock_get.return_value = rss_response("Cached")
        get_cached_rss(RSS_URL)

        def hangs_until_timeout(*args, **kwargs):
            self.clock.now += kwargs["timeout"]
            raise requests.exceptions.Timeout("timed out")

        self.mock_get.side_effect = hangs_until_timeout
        start = self.clock.now
        result = get_cached_rss(RSS_URL)

        self.assertEqual(result["rss"]["channel"]["item"]["title"], "Cached")
        self.assertLessEqual(self.clock.now - start, REQUEST_BUDGET)


class TestCallers(unittest.TestCase):

    @patch('util.get_cached_json')
    def test_weather_uses_get_cached_json_with_params(self, mock_cached_json):
        mock_cached_json.return_value = {"daily": {}}
        get_weather()
        url, params = mock_cached_json.call_args.args
        self.assertIn("open-meteo", url)
        self.assertEqual(params["timezone"], "Pacific/Auckland")

    @patch('rss.get_cached_rss')
    def test_rss_integration_via_getrss(self, mock_get_cached_rss):
        mock_get_cached_rss.return_value = {"rss": {}}
        getRSS(NewsType.NewsMap['Local'])
        mock_get_cached_rss.assert_called_once_with(NewsType.NewsMap['Local'])


if __name__ == '__main__':
    unittest.main()
