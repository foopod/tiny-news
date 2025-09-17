import requests
import time
import hashlib
from datetime import datetime
from functools import lru_cache
from typing import Optional, Dict, Any
import xmltodict
import json


def _get_hour_key() -> str:
    """Get current hour as cache key for 1-hour expiry."""
    return datetime.now().strftime("%Y-%m-%d-%H")


def _hash_params(params: Optional[Dict] = None) -> str:
    """Create hash of parameters for cache key."""
    if not params:
        return ""
    return hashlib.md5(str(sorted(params.items())).encode()).hexdigest()


def _exponential_retry_request(
    url: str, params: Optional[Dict] = None, max_retries: int = 3
) -> requests.Response:
    """Make HTTP request with exponential backoff retry."""
    last_exception = None

    for attempt in range(max_retries):
        try:
            if params:
                response = requests.get(url, params=params, timeout=10)
            else:
                response = requests.get(url, timeout=10)

            # Check for server errors that should trigger retry
            if response.status_code >= 500:
                raise requests.exceptions.HTTPError(
                    f"Server error: {response.status_code}"
                )

            return response

        except (
            requests.exceptions.RequestException,
            requests.exceptions.HTTPError,
        ) as e:
            last_exception = e
            if attempt < max_retries - 1:  # Don't sleep on the last attempt
                sleep_time = 2**attempt  # 1s, 2s, 4s
                time.sleep(sleep_time)

    # All retries failed, raise the last exception
    raise last_exception


@lru_cache(maxsize=128)
def _cached_rss_request(url: str, hour_key: str) -> Dict[str, Any]:
    """Cached RSS request with 1-hour expiry."""
    try:
        response = _exponential_retry_request(url)
        response.raise_for_status()
        return {"success": True, "data": xmltodict.parse(response.content)}
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "data": {
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
            },
        }


@lru_cache(maxsize=128)
def _cached_json_request(url: str, params_hash: str, hour_key: str) -> Dict[str, Any]:
    """Cached JSON request with 1-hour expiry."""
    try:
        # Reconstruct params from hash for actual request (simplified approach)
        response = _exponential_retry_request(url)
        response.raise_for_status()
        return {"success": True, "data": response.json()}
    except Exception as e:
        return {"success": False, "error": str(e), "data": None}


def get_cached_rss(url: str) -> Dict[str, Any]:
    """Get RSS data with caching and retry logic."""
    hour_key = _get_hour_key()
    result = _cached_rss_request(url, hour_key)
    return result["data"]


def get_cached_json(url: str, params: Optional[Dict] = None) -> Dict[str, Any]:
    """Get JSON data with caching and retry logic."""
    hour_key = _get_hour_key()
    params_hash = _hash_params(params)

    # Store params in a way we can reconstruct them
    if params:
        # For now, we'll make the actual request with params
        # A more sophisticated approach would store params in the cache
        try:
            response = _exponential_retry_request(url, params)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return get_fallback_json_data(url, str(e))
    else:
        result = _cached_json_request(url, params_hash, hour_key)
        if result["success"]:
            return result["data"]
        else:
            return get_fallback_json_data(url, result["error"])


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
