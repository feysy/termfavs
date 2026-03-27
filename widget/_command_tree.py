from rich.text import Text
from textual.widgets import Tree
from models import NamedNode


class CommandTree(Tree[NamedNode]):
    def process_label(self, label) -> Text:
        if isinstance(label, str):
            text_label = Text.from_markup(label)
        elif isinstance(label, NamedNode):
            text_label = Text.from_markup(label.name)
        else:
            text_label = label
        first_line = text_label.split()[0]

        return first_line
