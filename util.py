import logging
import re
import os
import shlex
import shutil
from typing import List
from models import Folder, Command
from textual.widgets.tree import TreeNode
import yaml


# This code replaces environment variables in a directory string with their
# values.Variables are specified by curly brackets, e.g. {$HOME} Matches are
# found using the regex pattern: \{(.*?)\} The matches are replaced with the
# values of the environment variables. Note that the environment variables are
# specified as a dictionary comprehension. This ensures that the code will run
# even if the environment variables are not set.


def replace_env_vars(directory: str) -> str:
    """
    Given a directory with environment variables as {$HOME},
    replace them with the actual values.
    """
    result = directory
    matches: List[str] = re.findall(r"\{\$(.*?)\}", directory)
    for match in matches:
        if match in os.environ:
            result = result.replace("{$" + match + "}", os.getenv(match))
    return result


def get_commands_file_from_non_standard_locations() -> str:
    global_path = "/etc/command_picker/commands.yaml"
    # copy global to local
    if os.path.exists(global_path):
        return global_path

    working_path = os.getcwd() + '/commands.yaml'
    if os.path.exists(working_path):
        return working_path

    working_path = os.path.dirname(os.path.realpath(__file__)) + '/commands.yaml'
    if os.path.exists(working_path):
        return working_path

    logging.getLogger().error("No commands.yaml file found. Exiting.")
    raise Exception("No commands.yaml file found. Exiting.")


def find_commands_location() -> str:
    local_path = replace_env_vars("{$HOME}/.config/termfavs/commands.yaml")
    if os.path.exists(local_path):
        return local_path

    other_path = get_commands_file_from_non_standard_locations()
    # copy global to local
    if os.path.exists(other_path):
        os.makedirs(os.path.dirname(local_path), exist_ok=True)
        shutil.copyfile(other_path, local_path)
        return local_path


def write_command_to_terminal(command: str) -> None:
    split_app_name = shlex.split(command)
    program_name = split_app_name[0]
    arguments = [*split_app_name]
    os.execvp(program_name, arguments)


def __build_command(data) -> Command:
    return Command(data["name"], data["description"], data["command"])


def __build_folder(data) -> Folder:
    if "commands" not in data or data["commands"] is None:
        data["commands"] = []
    if "folders" not in data or data["folders"] is None:
        data["folders"] = []
    commands = [__build_command(command) for command in data["commands"]]
    folders = [__build_folder(folder) for folder in data["folders"]]
    return Folder(data["name"], commands, folders)


def load_saved_commands(file: str) -> Folder:
    with open(file, "r") as stream:
        try:
            data = yaml.safe_load(stream)
            return __build_folder(data["root"])
        except KeyError as e:
            print(f"Wrong yaml format: {e}")
            exit(1)
        except yaml.YAMLError as exc:
            print(exc)


def create_tree_from_commands(tree: TreeNode, folder: Folder) -> None:
    for command in folder.commands:
        tree.add_leaf(command.name, command)
    for folder in folder.folders:
        new_tree = tree.add(folder.name, folder, expand=True)
        new_tree.collapse()
        create_tree_from_commands(new_tree, folder)
