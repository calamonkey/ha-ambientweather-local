"""Constants for AmbientWeather Local."""

DOMAIN = "ambientweather_local"

CONF_SCAN_INTERVAL = "scan_interval"
DEFAULT_SCAN_INTERVAL = 33  # station page refreshes every ~16 s; two cycles + 1
MIN_SCAN_INTERVAL = 15
UNITS_REFRESH_EVERY = 20  # re-read station.htm every N polls
MAX_TOLERATED_FAILURES = 3  # consecutive failed polls before entities go unavailable

# Sunlight luminous efficacy used to estimate lux from W/m² (same as Ecowitt/WU).
LUX_PER_WM2 = 126.7

# station.htm <select> name -> {option value: unit}. None = unsupported by HA.
WIND_UNITS = {"0": "m/s", "1": "km/h", "2": "ft/s", "3": None, "4": "mph", "5": "kn"}
RAIN_UNITS = {"0": "mm", "1": "in"}
PRESSURE_UNITS = {"0": "hPa", "1": "inHg", "2": "mmHg"}
TEMP_UNITS = {"0": "°C", "1": "°F"}
SOLAR_UNITS = {"0": "lx", "1": "W/m²", "2": "fc"}

FC_TO_LUX = 10.7639

DEFAULT_UNIT_CODES = {
    "unit_Wind": "1",
    "u_Rainfall": "0",
    "unit_Pressure": "0",
    "u_Temperature": "0",
    "unit_Solar": "1",
}
