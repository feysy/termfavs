from ._named_node import NamedNode


class Command(NamedNode):
    def __init__(self, name: str, description: str, command: str) -> None:
        super().__init__(name)
        self.description = description
        self.command = command
