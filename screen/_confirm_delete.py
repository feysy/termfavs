from textual.app import ComposeResult
from textual.screen import ModalScreen
from textual.widgets import Label, Button
from textual.containers import Vertical, Horizontal


class ConfirmDeleteScreen(ModalScreen[bool]):
    """A modal screen for confirming deletion."""

    DEFAULT_CSS = """
    ConfirmDeleteScreen {
        align: center middle;
    }
    """

    def compose(self) -> ComposeResult:
        yield Vertical(
            Label("Are you sure you want to delete this item?"),
            Horizontal(
                Button("Delete", variant="error", id="delete"),
                Button("Cancel", variant="default", id="cancel"),
                classes="modal_buttons",
            ),
            id="confirm_modal",
        )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "cancel":
            self.dismiss(False)
        else:
            self.dismiss(True)
