from textual.app import App, ComposeResult
from textual.widgets import Label
from textual.containers import Middle
from screen import MainScreen
import util as util

import logging

logging.basicConfig(filename="textual.log", level="NOTSET")


class Main(App):
    CSS_PATH = "screen/main.tcss"

    def on_mount(self) -> None:
        path = util.find_commands_location()
        saved_commands = util.load_saved_commands(path)
        self.push_screen(
            MainScreen(
                name=" Favc ",
                id="main_screen",
                commands=saved_commands,
                update_command=self.update_command,
                commands_path=path,
            )
        )
        self.command = ""

    def compose(self) -> ComposeResult:
        yield Middle(
            Label("Fixes", id="app_name_label", classes="transparent"),
            Label("welcome!", id="welcome_label", classes="transparent"),
            classes="transparent fullsize",
        )

    def update_command(self, command: str) -> None:
        self.command = command

    def close(self) -> None:
        self.exit()


def start():
    try:
        app = Main()
        app.run()
        if app.command:
            util.write_command_to_terminal(app.command)
    except Exception as e:
        logging.error(format(e))


if __name__ == "__main__":
    start()
