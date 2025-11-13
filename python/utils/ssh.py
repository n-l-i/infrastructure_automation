from time import sleep as _sleep
from dataclasses import dataclass
import paramiko
from utils.inventory import Host


@dataclass
class Ssh_command_output:
    stdout: str
    stderr: str
    exit_code: int


def run_ssh_command(
    host: Host,
    command: str,
    with_pty=False,
    verbose=False,
) -> Ssh_command_output:
    private_key = paramiko.Ed25519Key(filename=host.ssh_key_path)

    # Connect to host
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(
        hostname=host.ip_address,
        port=host.ssh_port,
        username=host.username,
        pkey=private_key,
        timeout=3,
    )

    stdin, stdout, stderr = ssh.exec_command(command, get_pty=with_pty)

    output = ""
    _sleep(0.1)
    while not stdout.channel.exit_status_ready():
        outp = stdout.channel.recv(1024).decode("utf-8")
        if outp:
            if verbose:
                print(outp, end="")
            output += outp

    # Read any remaining output after the command completes
    outp = stdout.read().decode("utf-8")
    if outp:
        if verbose:
            print(outp)
        output += outp

    result = Ssh_command_output(
        output.strip(),
        stderr.read().decode().strip(),
        stdout.channel.recv_exit_status(),
    )
    ssh.close()

    if result.exit_code != 0:
        raise Exception(result, command)
    return result
