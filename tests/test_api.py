import asyncio
import pytest


def test_livedata_values(api, livedata_html):
    d = api.parse_livedata(livedata_html)
    assert float(d["outTemp"]) == 3.9
    assert d["outHumi"] == "81"
    assert float(d["rainofyearly"]) > 0
    assert d["outBattSta1"] == "Normal"


def test_missing_sensors_are_none(api, livedata_html):
    d = api.parse_livedata(livedata_html)
    for key in ("inTemp", "inHumi", "AbsPress", "RelPress", "pm25in", "pm25out", "IndoorID"):
        assert d[key] is None, key


def test_rejects_non_weather_page(api):
    with pytest.raises(api.CannotConnect):
        api.parse_livedata("<html><body>nothing</body></html>")


def test_units(api, station_html):
    u = api.parse_units(station_html)
    assert u["unit_Wind"] == "1"      # km/h
    assert u["u_Rainfall"] == "0"     # mm
    assert u["unit_Pressure"] == "0"  # hPa
    assert u["u_Temperature"] == "0"  # degC
    assert u["unit_Solar"] == "1"     # W/m2


def test_parse_mac_only_reads_mac_field(api):
    snippet = '<input name="mac_addr" disabled="disabled" type="text" value="00:00:00:00:00:00" />'
    assert api.parse_mac(snippet) == "00:00:00:00:00:00"
    assert api.parse_mac("<input name=\"stationPW\" value=\"x\">") is None



@pytest.mark.skipif(not hasattr(asyncio, "timeout"), reason="needs Python 3.11+")
def test_get_retries_once_then_succeeds(api):
    calls = []

    class Resp:
        def raise_for_status(self): pass
        async def text(self, errors=None): return "ok"
        async def __aenter__(self): return self
        async def __aexit__(self, *a): return False

    class Session:
        def get(self, url, headers=None):
            calls.append(headers)
            if len(calls) == 1:
                raise api.aiohttp.ServerDisconnectedError()
            return Resp()

    api.RETRY_DELAY = 0
    client = api.AmbientLocalClient(Session(), "192.0.2.1")
    assert asyncio.run(client._get("livedata.htm")) == "ok"
    assert len(calls) == 2 and calls[0] == {"Connection": "close"}


@pytest.mark.skipif(not hasattr(asyncio, "timeout"), reason="needs Python 3.11+")
def test_get_error_message_names_exception(api):
    class Session:
        def get(self, url, headers=None):
            raise api.aiohttp.ServerDisconnectedError()

    api.RETRY_DELAY = 0
    client = api.AmbientLocalClient(Session(), "192.0.2.1")
    with pytest.raises(api.CannotConnect, match="ServerDisconnectedError"):
        asyncio.run(client._get("livedata.htm"))
