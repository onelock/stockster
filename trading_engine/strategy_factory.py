import pkgutil
import inspect
import importlib
from typing import Dict, Type

from trading_engine.strategies.base import Strategy


class StrategyFactory:
    """
    Auto-discovers and loads all Strategy subclasses inside the strategies package.
    """

    _registry: Dict[str, Type[Strategy]] = {}

    @classmethod
    def load_strategies(cls):
        """
        Dynamically import all modules in the strategies package and register Strategy subclasses.
        """
        from trading_engine import strategies  # root package

        for module_info in pkgutil.iter_modules(strategies.__path__):
            module_name = module_info.name
            # Skip base module
            if module_name == "base":
                continue

            module = importlib.import_module(f"trading_engine.strategies.{module_name}")

            # Inspect module for Strategy subclasses
            for _, obj in inspect.getmembers(module, inspect.isclass):
                if issubclass(obj, Strategy) and obj is not Strategy:
                    instance = obj()
                    cls._registry[instance.name] = obj

    @classmethod
    def get(cls, name: str) -> Strategy:
        """
        Instantiate a strategy by name.
        """
        if not cls._registry:
            cls.load_strategies()

        if name not in cls._registry:
            raise ValueError(f"Strategy '{name}' not found in registry")

        return cls._registry[name]()

    @classmethod
    def all(cls) -> Dict[str, Type[Strategy]]:
        """
        Return all registered strategies.
        """
        if not cls._registry:
            cls.load_strategies()
        return cls._registry
