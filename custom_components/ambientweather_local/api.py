"""Client for the local web UI of older AmbientWeather Wi-Fi modules.

These modules only expose HTML pages (``livedata.htm``, ``station.htm``,
``weather.htm``). Values live in ``<input name=... value=...>`` fields and the
display units are the selected ``<option>`` of ``<select>`` elements.

Only GET requests are ever issued. ``weather.htm`` is read once (for the MAC
address) and its content is never logged because it contains cloud credentials.
"""

from __future__ import annotations

import asyncio
import re
from html.parser import HTMLParser

import aiohttp

REQUEST_TIMEOUT = 10
MISSING_RE = re.compile(r"^[-\s.]*$|^0x-+$")
MAC_RE = re.compile(
    r'name="mac_addr"[^>]*?value="([0-9A-Fa-f]{2}(?::[0-9A-Fa-f]{2}){5})"'
)


class AmbientLocalError(Exception):
    """Base error."""


class CannotConnect(AmbientLocalError):
    """Station unreachable or returned an unusable response."""


class _FormParser(HTMLParser):
    """Collect input values and the selected option of each select."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.inputs: dict[str, str] = {}
        self.selected: dict[str, str] = {}
        self._select: str | None = None

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        a = {k: (v if v is not None else "") for k, v in attrs}
        if tag == "input" and "name" in a:
            self.inputs[a["name"]] = a.get("value", "").strip()
        elif tag == "select":
            self._select = a.get("name")
        elif tag == "option" and self._select and "selected" in a:
            self.selected[self._select] = a.get("value", "")

    def handle_endtag(self, tag: str) -> None:
        if tag == "select":
            self._select = None


def parse_livedata(html: str) -> dict[str, str | None]:
    """Return field -> value, with placeholder values mapped to None."""
    parser = _FormParser()
    parser.feed(html)
    data = {
        key: (None if MISSING_RE.match(val) else val)
        for key, val in parser.inputs.items()
    }
    if "outTemp" not in data and "inTemp" not in data:
        raise CannotConnect("livedata.htm did not contain weather fields")
    return data


def parse_units(html: str) -> dict[str, str]:
    """Return unit select name -> selected option value (as a string)."""
    parser = _FormParser()
    parser.feed(html)
    return parser.selected


def parse_mac(html: str) -> str | None:
    """Extract the station MAC from weather.htm without touching other fields."""
    match = MAC_RE.search(html)
    return match.group(1).upper() if match else None


class AmbientLocalClient:
    """Fetch and parse the station's pages."""

    def __init__(self, session: aiohttp.ClientSession, host: str) -> None:
        self._session = session
        self.host = host

    async def _get(self, path: str) -> str:
        url = f"http://{self.host}/{path}"
        try:
            async with asyncio.timeout(REQUEST_TIMEOUT):
                async with self._session.get(url) as resp:
                    resp.raise_for_status()
                    return await resp.text(errors="replace")
        except (aiohttp.ClientError, TimeoutError) as err:
            raise CannotConnect(f"Error fetching {path}: {err}") from err

    async def async_get_livedata(self) -> dict[str, str | None]:
        return parse_livedata(await self._get("livedata.htm"))

    async def async_get_units(self) -> dict[str, str]:
        return parse_units(await self._get("station.htm"))

    async def async_get_mac(self) -> str | None:
        return parse_mac(await self._get("weather.htm"))
