import unittest
import sys
import os
from unittest.mock import patch, Mock, MagicMock
import time

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from http_utils import get_cached_rss, get_cached_json, _cached_rss_request, _cached_json_request
from rss import getRSS, NewsType
from util import get_weather


class TestCachingFunctionality(unittest.TestCase):

    def setUp(self):
        # Clear LRU cache before each test
        _cached_rss_request.cache_clear()
        _cached_json_request.cache_clear()

    @patch('http_utils._cached_rss_request')
    def test_rss_caching_success(self, mock_cached_rss):
        # Mock successful RSS response
        mock_cached_rss.return_value = {
            "success": True,
            "data": {
                "rss": {
                    "channel": {
                        "item": [{
                            "title": "Test News Item",
                            "description": "Test description"
                        }]
                    }
                }
            }
        }

        # First call should use cached function
        result1 = get_cached_rss("https://example.com/rss")
        self.assertEqual(mock_cached_rss.call_count, 1)
        self.assertIn("rss", result1)
        self.assertEqual(result1["rss"]["channel"]["item"][0]["title"], "Test News Item")

        # Second call should use same cache key (same result)
        result2 = get_cached_rss("https://example.com/rss")
        self.assertEqual(result1, result2)

    @patch('http_utils.requests.get')
    def test_rss_caching_failure_fallback(self, mock_get):
        # Mock failed RSS response
        mock_get.side_effect = Exception("Network error")

        result = get_cached_rss("https://example.com/rss")

        # Should return fallback data
        self.assertIn("rss", result)
        self.assertEqual(result["rss"]["channel"]["item"][0]["title"], "Failed to fetch news")
        self.assertIn("Network error", result["rss"]["channel"]["item"][0]["description"])

    @patch('util.get_cached_json')
    def test_weather_api_caching(self, mock_cached_json):
        # Mock successful weather response
        mock_cached_json.return_value = {
            "daily": {
                "time": ["2025-09-17", "2025-09-18"],
                "temperature_2m_max": [20, 22],
                "temperature_2m_min": [10, 12],
                "precipitation_sum": [0, 5],
                "weather_code": [0, 61]
            },
            "daily_units": {
                "temperature_2m_max": "°C",
                "temperature_2m_min": "°C",
                "precipitation_sum": "mm"
            }
        }

        result = get_weather()

        self.assertEqual(len(result["daily"]["time"]), 2)
        self.assertEqual(result["daily"]["temperature_2m_max"][0], 20)
        self.assertEqual(mock_cached_json.call_count, 1)

    @patch('util.get_cached_json')
    def test_weather_api_failure_fallback(self, mock_cached_json):
        # Mock failed weather response with fallback data
        mock_cached_json.return_value = {
            "daily": {
                "time": ["2025-09-17"],
                "temperature_2m_max": ["--"],
                "temperature_2m_min": ["--"],
                "precipitation_sum": [0],
                "weather_code": [0]
            },
            "daily_units": {
                "temperature_2m_max": "°C",
                "temperature_2m_min": "°C",
                "precipitation_sum": "mm"
            }
        }

        result = get_weather()

        # Should return fallback weather data
        self.assertEqual(len(result["daily"]["time"]), 1)
        self.assertEqual(result["daily"]["temperature_2m_max"][0], "--")
        self.assertEqual(result["daily_units"]["temperature_2m_max"], "°C")

    @patch('rss.get_cached_rss')
    def test_rss_integration_via_getrss(self, mock_get_cached_rss):
        # Test RSS integration through the getRSS function
        mock_get_cached_rss.return_value = {
            "rss": {
                "channel": {
                    "item": [{
                        "title": "Local News",
                        "description": "Local news description"
                    }]
                }
            }
        }

        # Test with actual NewsType URL
        result = getRSS(NewsType.NewsMap['Local'])

        self.assertIn("rss", result)
        self.assertEqual(result["rss"]["channel"]["item"][0]["title"], "Local News")
        self.assertEqual(mock_get_cached_rss.call_count, 1)
        mock_get_cached_rss.assert_called_with(NewsType.NewsMap['Local'])

    def test_exponential_retry_logic(self):
        # Test the actual retry logic by calling the function directly
        with patch('http_utils.requests.get') as mock_get:
            with patch('http_utils.time.sleep') as mock_sleep:
                from http_utils import _exponential_retry_request
                import requests

                # Mock failing requests that eventually succeed
                mock_response = Mock()
                mock_response.raise_for_status.return_value = None
                mock_response.status_code = 200

                # Create exception instances that would be caught
                connection_error = requests.exceptions.ConnectionError("Connection error")
                timeout_error = requests.exceptions.Timeout("Timeout")

                # First two calls fail, third succeeds
                mock_get.side_effect = [
                    connection_error,
                    timeout_error,
                    mock_response
                ]

                result = _exponential_retry_request("https://example.com/test")

                # Should have made 3 attempts
                self.assertEqual(mock_get.call_count, 3)

                # Should have slept twice (1s, 2s)
                self.assertEqual(mock_sleep.call_count, 2)
                mock_sleep.assert_any_call(1)  # First retry delay
                mock_sleep.assert_any_call(2)  # Second retry delay

                # Should return successful response
                self.assertEqual(result, mock_response)

    def test_exponential_retry_max_attempts(self):
        # Test max attempts with all failures
        with patch('http_utils.requests.get') as mock_get:
            with patch('http_utils.time.sleep') as mock_sleep:
                from http_utils import _exponential_retry_request
                import requests

                # Mock all requests failing with proper exception type
                connection_error = requests.exceptions.ConnectionError("Persistent error")
                mock_get.side_effect = connection_error

                # Should raise exception after max attempts
                with self.assertRaises(requests.exceptions.ConnectionError):
                    _exponential_retry_request("https://example.com/test")

                # Should have made 3 attempts
                self.assertEqual(mock_get.call_count, 3)

                # Should have slept twice (1s, 2s) but not after final attempt
                self.assertEqual(mock_sleep.call_count, 2)

    def test_cache_hour_expiry_simulation(self):
        # Test that cache uses hour-based keys for expiry
        with patch('http_utils._cached_rss_request') as mock_cached_rss:
            # Mock different responses for different hours
            def side_effect(url, hour_key):
                if hour_key == "2025-09-17-10":
                    return {
                        "success": True,
                        "data": {"rss": {"channel": {"item": [{"title": "Hour 1"}]}}}
                    }
                else:
                    return {
                        "success": True,
                        "data": {"rss": {"channel": {"item": [{"title": "Hour 2"}]}}}
                    }

            mock_cached_rss.side_effect = side_effect

            with patch('http_utils._get_hour_key') as mock_hour_key:
                # Simulate first hour
                mock_hour_key.return_value = "2025-09-17-10"
                result1 = get_cached_rss("https://example.com/rss")

                # Same hour - should use same cache key
                result2 = get_cached_rss("https://example.com/rss")

                # Simulate next hour - different cache key
                mock_hour_key.return_value = "2025-09-17-11"
                result3 = get_cached_rss("https://example.com/rss")

                # Verify different results for different hours
                self.assertEqual(result1["rss"]["channel"]["item"][0]["title"], "Hour 1")
                self.assertEqual(result3["rss"]["channel"]["item"][0]["title"], "Hour 2")

                # Should have been called with different hour keys
                expected_calls = [
                    unittest.mock.call("https://example.com/rss", "2025-09-17-10"),
                    unittest.mock.call("https://example.com/rss", "2025-09-17-10"),
                    unittest.mock.call("https://example.com/rss", "2025-09-17-11"),
                ]
                mock_cached_rss.assert_has_calls(expected_calls)


if __name__ == '__main__':
    unittest.main()