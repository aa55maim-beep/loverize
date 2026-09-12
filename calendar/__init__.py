import importlib.util
import sys
import sysconfig
from pathlib import Path


_stdlib_calendar_path = Path(sysconfig.get_path("stdlib")) / "calendar.py"
_stdlib_spec = importlib.util.spec_from_file_location("_stdlib_calendar", _stdlib_calendar_path)
_stdlib_calendar = importlib.util.module_from_spec(_stdlib_spec)
sys.modules["_stdlib_calendar"] = _stdlib_calendar
_stdlib_spec.loader.exec_module(_stdlib_calendar)

for _name in dir(_stdlib_calendar):
	if not _name.startswith("__"):
		globals()[_name] = getattr(_stdlib_calendar, _name)
