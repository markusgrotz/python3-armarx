from rich.console import Console
from rich import pretty
from icecream import install, ic


console = Console()
install()
ic.configureOutput(includeContext=True)
pretty.install()
