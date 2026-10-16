# AmbientWeather Local (No API)

A Home Assistant integration for **older AmbientWeather stations that have no API support**. It reads an AmbientWeather station **directly over your LAN** instead of through the ambientweather.net cloud
(no Application Key / API Key, no internet dependency).

## Who this is for

Older AmbientWeather Wi-Fi modules (e.g. firmware "AmbientWeather 4.6.2", WS-1550-IP profile) that have
no JSON API, no custom-server upload and no GW1000 port 45000. The only local data they offer is the
built-in web UI, so this integration polls `http://<station>/livedata.htm` and parses the values
(plus `station.htm` for the units you selected on the device).

Newer consoles (WS-2000, WS-2902A+) can push to a custom server; those are better served by other tools.

## Install

HACS: add this repository as a custom repository (category *Integration*), install, restart Home Assistant.
Manual: copy `custom_components/ambientweather_local` into your HA `config/custom_components/`.

Then *Settings → Devices & services → Add integration → AmbientWeather Local (No API)* and enter the station's
IP address (e.g. `192.0.2.10`). Give the station a DHCP reservation so the address does not change.

## Options

Polling interval: default **33 s** (the station page itself refreshes about every 16 s), minimum 15 s.

## Entities

Outdoor/indoor temperature and humidity, absolute/relative pressure, wind speed/gust/max daily gust/direction,
solar radiation, UV index, PM2.5, hourly rain rate, event/daily/weekly/monthly/yearly rain, and
battery-low binary sensors. Sensors the station does not have (shown as `--` on its page) are not created.
Units follow the station's own settings and Home Assistant converts for display.

## Limitations

- HTML scraping: a firmware change could break parsing (fixtures in `tests/fixtures` guard this).
- Only read-only GET requests are made. The integration never POSTs (so cannot reset rain totals).
- `weather.htm` is fetched once while adding the integration, only to read the MAC address used as the
  unique ID; its contents are not stored or logged.

## Development

```
pip install pytest aiohttp
pytest
bash scripts/check_private.sh
```

Fixtures are sanitized captures (placeholder MAC and IP). Never commit captures of `weather.htm`: it
contains cloud upload credentials. Put personal strings to scan for in `scripts/private_strings.txt`
(git-ignored).
