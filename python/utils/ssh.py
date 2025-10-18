from dataclasses import dataclass
import paramiko
from utils.inventory import Host


@dataclass
class Ssh_command_output:
    stdout: str
    stderr: str
    exit_code: int


def run_ssh_command(host: Host, command: str) -> Ssh_command_output:
    private_key = paramiko.Ed25519Key(filename=host.ssh_key_path)

    # Connect to host
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(
        hostname=host.ip_address,
        port=host.ssh_port,
        username=host.username,
        pkey=private_key,
    )

    stdin, stdout, stderr = ssh.exec_command(command)

    result = Ssh_command_output(
        stdout.read().decode().strip(),
        stderr.read().decode().strip(),
        stdout.channel.recv_exit_status(),
    )
    ssh.close()

    return result
