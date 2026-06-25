from fastapi import FastAPI, HTTPException
from dotenv import load_dotenv
import paramiko
import socket
import subprocess
import ipaddress
import os

load_dotenv(".env")
load_dotenv(".env.local", override=True)

docs_enabled = os.environ.get("DOCS_ENABLED", "false").lower() == "true"

app = FastAPI(docs_url="/docs" if docs_enabled else None, redoc_url=None)


def resolve_host(host: str) -> str:
    try:
        ip = ipaddress.IPv4Address(host)
        return str(ip)
    except ValueError:
        pass

    try:
        result = socket.getaddrinfo(host, None, socket.AF_INET)
        return result[0][4][0]
    except socket.gaierror:
        raise HTTPException(status_code=400, detail=f"No se pudo resolver el host: {host}")


@app.get("/home-dirs")
def get_home_dirs(host: str):
    ip = resolve_host(host)

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    ssh.connect(
        hostname=ip,
        username=os.environ["SSH_USER"],
        password=os.environ["SSH_PASSWORD"]
    )

    stdin, stdout, stderr = ssh.exec_command(
        "ls -d /home/*/"
    )

    dirs = stdout.read().decode().split()
    lrn_dirs = [d.strip("/").split("/")[-1] for d in dirs if d.split("/")[-2].startswith("lrn")]

    return {"directories": lrn_dirs}


@app.get("/host-status")
def get_host_status(host: str):
    ip = resolve_host(host)

    ping = subprocess.run(
        ["ping", "-c", "1", "-W", "1", ip],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(1)
    port_open = sock.connect_ex((ip, 22)) == 0
    sock.close()

    return {
        "ping": ping.returncode == 0,
        "ssh": port_open
    }
