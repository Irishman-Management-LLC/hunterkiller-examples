"""Read only Hunter Killer tools. No orders, credentials or model calls."""
import json
import re
import urllib.request
import urllib.error

BASE_URL = "https://hunterkiller.io"
DESCRIPTION = (
    "Read liquidation walls, nearest levels, snapshot age and the public record. "
    "Free data is 2 hours behind on six coins. Return the source fields unchanged. "
    "Descriptive measurements, not trading advice."
)


class HunterKillerError(RuntimeError):
    def __init__(self, status, body):
        self.status, self.body = status, body
        super().__init__(f"Hunter Killer HTTP {status}")


class _NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, request, fp, code, message, headers, new_url):
        # A remote redirect must not carry an application's API key elsewhere.
        return None


def _open(request, *, timeout):
    return urllib.request.build_opener(_NoRedirect()).open(request, timeout=timeout)


def get_levels(symbol: str, *, key=None, probe=False):
    """One HTTP call. An omitted key stays omitted; errors never become data."""
    symbol = str(symbol).strip().upper()
    if not re.fullmatch(r"[A-Z0-9]{2,20}", symbol):
        raise ValueError("Use a pair such as BTCUSDT")
    headers = {"Accept": "application/json", "User-Agent": "hunterkiller-agent-tools/0.1.0"}
    if key:
        headers["Authorization"] = "Bearer " + key
    if probe:
        headers["X-HK-Probe"] = "1"
    request = urllib.request.Request(BASE_URL + "/api/v1/levels/" + symbol, headers=headers)
    try:
        with _open(request, timeout=15) as response:
            data = json.load(response)
    except urllib.error.HTTPError as exc:
        try:
            body = json.loads(exc.read())
        except (ValueError, UnicodeError):
            body = {"error": "non_json_response"}
        raise HunterKillerError(exc.code, body) from None
    if not isinstance(data, dict) or data.get("ok") is not True:
        raise HunterKillerError(200, {"error": "invalid_levels_response"})
    return data


def create_levels_tool(*, key=None):
    """Create a LangChain StructuredTool without putting a key in its schema."""
    from langchain_core.tools import tool

    @tool("hunterkiller_levels", description=DESCRIPTION)
    def hunterkiller_levels(symbol: str) -> dict:
        return get_levels(symbol, key=key)

    return hunterkiller_levels
