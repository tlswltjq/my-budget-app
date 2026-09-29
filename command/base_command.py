import argparse
from abc import ABC, abstractmethod


class BaseCommand(ABC):
    @classmethod
    @abstractmethod
    def configure_parser(cls, parser: argparse.ArgumentParser) -> None:
        ...

    @abstractmethod
    def execute(self, args: argparse.Namespace) -> int:
        ...
