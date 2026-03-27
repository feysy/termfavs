from typing import Callable, Optional

from textual import on
from textual.widget import Widget
from textual.widgets import Input, Label, Button
from textual.containers import Horizontal, Vertical
from textual.app import ComposeResult
from models import Command


class CommandForm(Horizontal):

    def __init__(
            self,
            *children: Widget,
            command: Command,
            name: Optional[str] = None,
            id: Optional[str] = None,
            classes: Optional[str] = None,
            disabled: bool = False,
            on_run_command: Callable[[], None] = None,
    ) -> None:
        super().__init__(
            *children, name=name, id=id, classes=classes, disabled=disabled
        )
        self._command = command
        self.on_run_command = on_run_command

    @property
    def selected_command(self) -> Command:
        return self._command

    def compose(self) -> ComposeResult:
        yield Vertical(
            Horizontal(
                Label("Short Name:", id="lbl_name", classes="edit_label"),
                Input(
                    value=self._command.name,
                    id="text_command_name",
                    classes="edit_text",
                ),
            ),
            Horizontal(
                Label(
                    "Description:",
                    id="lbl_description",
                    classes="edit_label",
                ),
                Input(
                    value=self._command.description,
                    id="text_command_desc",
                    classes="edit_text",
                ),
                id="description_line",
            ),
            Horizontal(
                Label("Command:", id="lbl_command", classes="edit_label"),
                Input(
                    value=self._command.command,
                    id="text_command",
                    classes="edit_text",
                ),
            ),
            Horizontal(
                Button("Run Command (R)", id="bttn_run_command"),
                id="bttn_run_container",
            ),
            id="form_grid",
        )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "bttn_run_command" and self.on_run_command:
            self.on_run_command()

    @on(Input.Changed)
    def show_invalid_reasons(self, event: Input.Changed) -> None:
        if event.input.id == 'text_command':
            self._command.command = event.value
