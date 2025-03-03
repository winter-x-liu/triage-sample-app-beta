"""Screen routers. `ROUTERS` collects every module's `router`, so main.py lists none."""

import importlib
import pkgutil

ROUTERS = [
    importlib.import_module(f"{__name__}.{module.name}").router
    for module in pkgutil.iter_modules(__path__)
]
