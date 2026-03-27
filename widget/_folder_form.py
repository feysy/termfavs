from typing import Optional

from textual import on
from textual.widget import Widget
from textual.widgets import Input, Label
from textual.containers import Horizontal
from textual.app import ComposeResult
from models import Folder


class FolderForm(Horizontal):
    def __init__(
        self,
            *children: Widget,
            folder: Folder,
            name: Optional[str] = None,
            id: Optional[str] = None,
            classes: Optional[str] = None,
            disabled: bool = False,
    ) -> None:
        super().__init__(
            *children, name=name, id=id, classes=classes, disabled=disabled
        )
        self._folder = folder

    def compose(self) -> ComposeResult:
        yield Horizontal(
            Label("Folder Name:", id="lbl_folder_name", classes="edit_label"),
            Input(
                value=self._folder.name,
                id="text_folder_name",
                classes="edit_text",
            ),
            id="folder_grid",
            classes="edit_grid",
        )

    @on(Input.Changed)
    def update_model(self, event: Input.Changed) -> None:
        if event.input.id == "text_folder_name":
            self._folder.name = event.value
