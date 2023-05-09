from typing import Union, Dict, Any
from pathlib import Path
from paramiko import SSHClient, SSHException
from scp import SCPClient
from armarx_control import console


armar6_ssh_config = {
    'hostname': '10.6.2.100',
    'port': 22,
    'username': "armar-user",
    'timeout': 5
}


def copy_file_to_robot(
        filename: Path,
        target_folder_on_robot: str = "",
        ssh_config: Dict[str, Any] = None,
):
    if not target_folder_on_robot:
        target_folder_on_robot = "/home/armar-user/armar6_motion/kinesthetic_teaching"
    if ssh_config is None:
        ssh_config = armar6_ssh_config

    with SSHClient() as ssh:
        ssh.load_system_host_keys()
        try:
            ssh.connect(**ssh_config)
        except SSHException as ex:
            console.print(f"[bold red]{ex}")
            console.log(f"[bold red]Cannot connect to {ssh_config}")
            return None
        try:
            with SCPClient(ssh.get_transport()) as scp:
                if filename.is_file():
                    scp.put(str(filename), target_folder_on_robot, recursive=True)
                    console.rule("control config sent to robot")
                    return Path(target_folder_on_robot) / filename.name
                else:
                    console.log(f"[bold red]{filename} doesn't exist")
                    return None
        except RuntimeError:
            console.log(f"ssh copy failed")
