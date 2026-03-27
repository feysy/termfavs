from typing import Callable
import util as util

from textual.app import ComposeResult, Binding
from textual.widget import Widget
from textual.containers import Horizontal, Vertical
from textual.screen import Screen
from textual.widgets import Tree, Label, Button, Footer
from models import Folder
from models import NamedNode
from widget import FolderForm, CommandForm, CommandTree

from textual import on
from ._confirm_delete import ConfirmDeleteScreen
from models import Command


class MainScreen(Screen):
    CSS_PATH = "main.tcss"
    BINDINGS = [
        Binding("q", "close_normal()", "Close", show=True),
        Binding("r", "close_with_run()", "Run Command", show=True),
        Binding("a", "add_command", "Add Command", show=True),
        Binding("f", "add_folder", "Add Folder", show=True),
        Binding("d", "delete", "Delete", show=True),
        Binding("ctrl+s", "save_commands", "Save", show=True),
    ]
    commands: Folder = None
    tree: Tree[dict] = None

    def __init__(
            self, commands: Folder, update_command: Callable[[str], None], commands_path: str, **kwargs
    ) -> None:
        kwargs.pop("commands", None)
        super().__init__(**kwargs)
        self.commands = commands
        self.update_command = update_command
        self.commands_path = commands_path
        self.active_form = None

    def compose(self) -> ComposeResult:
        self.tree: CommandTree[NamedNode] = CommandTree(
            "Root", id="tree", classes="fillparent"
        )
        util.create_tree_from_commands(self.tree.root, self.commands)
        self.tree.root.expand()
        yield Horizontal(
            Vertical(
                self.tree,
                id="left",
                classes="transparent fillparent",
            ),
            Vertical(
                Vertical(classes="form_placeholder"),
                Vertical(
                    Label("<--- select something", id="lbl_msg"),
                    id="form_area",
                ),
                Vertical(classes="form_placeholder"),
                id="right",
                classes="transparent",
            ),
            id="main",
            classes="transparent",
        )
        self.footer = Footer()
        yield Footer()

    @on(Tree.NodeHighlighted)
    async def selected_command_changed(
            self, event: Tree.NodeHighlighted[NamedNode]
    ) -> None:
        """When we highlight a node in the CommandTree, the main body
        of the home page updates
        to display a form specific to the highlighted command."""
        self.selected_node = event.node
        await self.delete_container_children()
        if event.node.data is None:
            self.active_form = Label("<--- select something", id="lbl_msg")
        elif event.node.data.isFolder:
            self.active_form = FolderForm(folder=event.node.data)
        else:
            self.active_form = CommandForm(
                id="command_form",
                command=event.node.data,
                on_run_command=self.action_close_with_run,
            )

        self.add_child_to_container(self.active_form)

    async def delete_container_children(self) -> None:
        await self.query_one("#form_area").remove_children()

    def add_child_to_container(self, child: Widget) -> None:
        self.query_one("#form_area").mount(child)

    def action_close_with_run(self) -> None:
        if isinstance(self.active_form, CommandForm):
            self.update_command(self.active_form.selected_command.command)
            self.parent.close()

    def action_close_normal(self) -> None:
        self.update_command(None)
        self.parent.close()

    def action_save_commands(self) -> None:
        util.save_commands(self.commands_path, self.commands)
        self.notify(f"Commands saved to {self.commands_path}")

    def action_add_command(self) -> None:
        new_command = Command("New Command", "Description", "ls")
        parent_node, parent_folder = self._get_parent_for_new_item()
        
        parent_folder.commands.append(new_command)
        parent_node.add_leaf(new_command.name, new_command)
        parent_node.expand()
        self.notify("Added new command")

    def action_add_folder(self) -> None:
        new_folder = Folder("New Folder", [], [])
        parent_node, parent_folder = self._get_parent_for_new_item()
        
        parent_folder.folders.append(new_folder)
        new_node = parent_node.add(new_folder.name, new_folder, expand=True)
        new_node.collapse()
        parent_node.expand()
        self.notify("Added new folder")

    async def action_delete(self) -> None:
        if not hasattr(self, "selected_node") or self.selected_node is None or self.selected_node == self.tree.root:
            self.notify("Cannot delete root", variant="error")
            return

        def check_confirmation(confirmed: bool) -> None:
            if confirmed:
                self._perform_delete()

        self.app.push_screen(ConfirmDeleteScreen(), check_confirmation)

    def _perform_delete(self) -> None:
        node = self.selected_node
        data = node.data
        parent_node = node.parent
        parent_folder = parent_node.data if parent_node.data else self.commands

        if isinstance(data, Command):
            parent_folder.commands.remove(data)
        else:
            parent_folder.folders.remove(data)
        
        node.remove()
        self.notify("Item deleted")

    def _get_parent_for_new_item(self):
        selected_node = self.tree.cursor_node
        if selected_node is None or selected_node == self.tree.root:
            return self.tree.root, self.commands
        
        data = selected_node.data
        if isinstance(data, Folder):
            return selected_node, data
        else:
            parent_node = selected_node.parent
            parent_folder = parent_node.data if parent_node.data else self.commands
            return parent_node, parent_folder
