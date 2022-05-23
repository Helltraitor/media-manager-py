from importlib import import_module
from pathlib import Path
from typing import Type

from media_manager.application.api import ModuleLoader
from media_manager.application.constants import APPLICATION_MODULE_API_VERSION

from .module import Module


class ImportLocations:
    from sys import path as import_locations

    def __init__(self, *locations: str):
        self.import_locations = {
            location: location in ImportLocations.import_locations for location in locations
        }

    def __enter__(self):
        for location, appended in self.import_locations.items():
            if not appended:
                ImportLocations.import_locations.append(location)

    def __exit__(self, exc_type, exc_val, exc_tb):
        for location, appended in self.import_locations.items():
            if not appended:
                ImportLocations.import_locations.remove(location)


class Loader:
    def __init__(self, app_location: Path):
        self.app_location = app_location
        self.modules_locations: list[Path] = []
        self.modules_loaders: list[Type[ModuleLoader]] = []
        self.modules_objects: dict[str, list[Module]] = {
            "SUCCESS": [],
            "FAILURE": []
        }

    def add_modules_location(self, location: Path):
        if not location.is_dir():
            print(f'Warning: Indicated location is not a directory: "{location}"')
            return
        self.modules_locations.append(location)

    def find_all(self):
        with ImportLocations(str(self.app_location), *(str(location) for location in self.modules_locations)):
            for location in self.modules_locations:
                # Find all modules names in indicated import locations
                modules_names = (path.parts[-1] for path in location.iterdir() if path.is_dir())
                # Import these modules
                modules_objects = (module for module in map(import_module, modules_names))
                # Get public api class or default None singleton
                modules_loaders = (getattr(module, "PublicModuleLoader", object) for module in modules_objects)
                # Filter loaders by subclass check (all loaders must be subclass of ModuleLoader)
                modules_loaders = tuple(loader for loader in modules_loaders if issubclass(loader, ModuleLoader))
                self.modules_loaders.extend(modules_loaders)

    def load_all(self):
        modules = [Module(loader()) for loader in self.modules_loaders]
        for module in sorted(modules, key=lambda mod: mod.loading_priority or 1):
            if module.module_meta is None or not module.module_meta.is_supported_api(APPLICATION_MODULE_API_VERSION):
                self.modules_objects["FAILURE"].append(module)
            else:
                self.modules_objects["SUCCESS"].append(module)

    def fetch_failure(self) -> list[Module]:
        return self.modules_objects["FAILURE"]

    def fetch_success(self) -> list[Module]:
        return self.modules_objects["SUCCESS"]
