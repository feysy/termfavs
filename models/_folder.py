from typing import List
from . import Command
from ._named_node import NamedNode


class Folder(NamedNode):
    def __init__(
        self,
        name: str,
        commands: List[Command],
        folders,
    ) -> None:
        super().__init__(name)
        self.commands = commands
        self.folders = folders
        self.isFolder = True
