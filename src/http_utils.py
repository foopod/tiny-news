"""Live-first HTTP fetching with a short-lived fallback cache.

Every call goes to the network first, in a background thread:
  - a response within FAST_RESPONSE seconds is used as is
  - if it's slower and a recent cached copy exists, the cached copy is used
    (the request carries on in the background and refreshes the cache)
  - if it's slower and nothing recent is cached, we keep waiting for it, up to
    REQUEST_BUDGET seconds including retries
A failed request also falls back to a recent cached copy. Cached copies are
only used while no older than MAX_CACHE_AGE. Failures are never cached, and
the cache lives in memory only.
"""
import copy
import json
import time
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutureTimeout
from datetime import datetime
from typing import Any, Callable, Dict, Optional

import requests
import xmltodict

# how long to wait for a live response before using a cached copy
FAST_RESPONSE = 2
# total time allowed for one fetch, including retries
REQUEST_BUDGET = 15
# oldest cached response we're willing to fall back to
MAX_CACHE_AGE = 2 * 60 * 60
MAX_RETRIES = 3

# (url, params) -> (time fetched, data)
_cache: Dict[tuple, tuple] = {}

_executor = ThreadPoolExecutor(max_workers=4, thread_name_prefix="fetch")


def _now() -> float:
    return time.monotonic()


def _cache_key(url: str, params: Optional[Dict] = None) -> tuple:
    return (url, json.dumps(params, sort_keys=True) if params else "")


def _request_within_budget(
    url: str, params: Optional[Dict] = None, budget: float = REQUEST_BUDGET
) -> requests.Response:
    """GET with exponential backoff retries, giving up once the budget is spent.

    Each attempt's timeout is the time left in the budget. requests applies that
    to connecting and to each read rather than the whole download, so a server
    that trickles data very slowly can still overrun the budget.
    """
    deadline = _now() + budget
    last_exception = None

    for attempt in range(MAX_RETRIES):
        remaining = deadline - _now()
        if remaining <= 0:
            break
        try:
            response = requests.get(url, params=params, timeout=remaining)

            # Check for server errors that should trigger retry
            if response.status_code >= 500:
                raise requests.exceptions.HTTPError(
                    f"Server error: {response.status_code}"
                )

            return response

        except requests.exceptions.RequestException as e:
            last_exception = e
            sleep_time = 2**attempt  # 1s, 2s
            is_last_attempt = attempt == MAX_RETRIES - 1
            if is_last_attempt or _now() + sleep_time >= deadline:
                break
            time.sleep(sleep_time)

    raise last_exception or requests.exceptions.Timeout(
        f"No response within {budget}s"
    )


def _fresh_cached(key: tuple) -> Optional[tuple]:
    """Return (age in seconds, copy of data) if a recent enough copy is cached."""
    cached = _cache.get(key)
    if cached and _now() - cached[0] <= MAX_CACHE_AGE:
        # callers modify what they get back (e.g. print_weather), so hand out copies
        return _now() - cached[0], copy.deepcopy(cached[1])
    return None


def _fetch_and_store(key: tuple, fetch: Callable[[], Any]) -> Any:
    data = fetch()
    _cache[key] = (_now(), copy.deepcopy(data))
    return data


def _fetch(key: tuple, fetch: Callable[[], Any]) -> Any:
    """Fetch live data, using a recent cached copy if the fetch is slow or fails."""
    future = _executor.submit(_fetch_and_store, key, fetch)
    try:
        return future.result(timeout=FAST_RESPONSE)
    except FutureTimeout:
        cached = _fresh_cached(key)
        if cached:
            print(f"Slow response from {key[0]}, using cached copy from {int(cached[0] / 60)} min ago")
            return cached[1]
        # nothing recent to fall back on, so wait for the live response
        try:
            return future.result()
        except Exception as e:
            return _cached_or_raise(key, e)
    except Exception as e:
        return _cached_or_raise(key, e)


def _cached_or_raise(key: tuple, error: Exception) -> Any:
    cached = _fresh_cached(key)
    if cached:
        print(f"Fetch failed for {key[0]} ({error}), using cached copy from {int(cached[0] / 60)} min ago")
        return cached[1]
    raise error


def get_cached_rss(url: str) -> Dict[str, Any]:
    """Get an RSS feed, live if possible, else a recent cached copy, else a placeholder."""

    def fetch():
        response = _request_within_budget(url)
        response.raise_for_status()
        return xmltodict.parse(response.content)

    try:
        return _fetch(_cache_key(url), fetch)
    except Exception as e:
        return {
            "rss": {
                "channel": {
                    "item": [
                        {
                            "title": "Failed to fetch news",
                            "description": f"Unable to retrieve news from source: {str(e)}",
                        }
                    ]
                }
            }
        }


def get_cached_json(url: str, params: Optional[Dict] = None) -> Dict[str, Any]:
    """Get JSON, live if possible, else a recent cached copy, else fallback data."""

    def fetch():
        response = _request_within_budget(url, params)
        response.raise_for_status()
        return response.json()

    try:
        return _fetch(_cache_key(url, params), fetch)
    except Exception as e:
        return get_fallback_json_data(url, str(e))


def get_fallback_json_data(url: str, error_message: str) -> Dict[str, Any]:
    """Return fallback data based on URL type."""
    if "open-meteo" in url or "weather" in url:
        # Weather API fallback
        return {
            "daily": {
                "time": [datetime.now().strftime("%Y-%m-%d")],
                "temperature_2m_max": ["--"],
                "temperature_2m_min": ["--"],
                "precipitation_sum": [0],
                "weather_code": [0],
            },
            "daily_units": {
                "temperature_2m_max": "°C",
                "temperature_2m_min": "°C",
                "precipitation_sum": "mm",
            },
        }
    elif "puzzle" in url or "shadify" in url:
        # Puzzle API fallback
        return {"task": "Failed to fetch puzzle", "error": error_message}
    else:
        # Generic fallback
        return {"error": f"Failed to fetch data: {error_message}"}
