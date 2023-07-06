from pathlib import Path
from typing import Union, List
import inquirer


def ask_list(message: str, choices: list) -> Union[str, Path]:
    question = [inquirer.List("question", message=message, choices=choices)]
    return inquirer.prompt(question)["question"]


def ask_checkbox(message: str, choices: list) -> Union[List[str], List[Path]]:
    question = [inquirer.Checkbox("question", message=message, choices=choices)]
    return inquirer.prompt(question)["question"]