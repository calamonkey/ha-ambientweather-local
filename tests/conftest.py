import importlib.util
from pathlib import Path

import pytest

ROOT = Path(__file__).parent
API_PATH = ROOT.parent / "custom_components" / "ambientweather_local" / "api.py"


@pytest.fixture(scope="session")
def api():
    """Load api.py directly so tests do not need Home Assistant installed."""
    spec = importlib.util.spec_from_file_location("aw_api", API_PATH)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture
def livedata_html():
    return (ROOT / "fixtures" / "livedata.htm").read_text(encoding="utf-8")


@pytest.fixture
def station_html():
    return (ROOT / "fixtures" / "station.htm").read_text(encoding="utf-8")
