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

