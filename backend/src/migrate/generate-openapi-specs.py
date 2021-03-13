import json
import sys
from pathlib import Path

# Standalone boilerplate before relative imports
if __package__ is None:
    DIR = Path(__file__).resolve().parent
    sys.path.insert(0, str(DIR.parent))
    __package__ = DIR.name

from .main import app

# write openapi.json spec to file
with open("./openapi.json", "w") as outfile:
    print("Create API docs", app.openapi())
    json.dump(app.openapi(), outfile)
