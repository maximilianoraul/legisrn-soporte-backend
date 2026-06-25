from fastapi import FastAPI
from dotenv import load_dotenv
import paramiko
import os

load_dotenv(".env")
load_dotenv(".env.local", override=True)

docs_enabled = os.environ.get("DOCS_ENABLED", "false").lower() == "true"

app = FastAPI(docs_url="/docs" if docs_enabled else None, redoc_url=None)

@app.get("/home-dirs")
def get_home_dirs(host: str):

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    ssh.connect(
        hostname=host,
        username=os.environ["SSH_USER"],
        password=os.environ["SSH_PASSWORD"]
    )

    stdin, stdout, stderr = ssh.exec_command(
        "ls -d /home/*/"
    )

    dirs = stdout.read().decode().split()
    lrn_dirs = [d.strip("/").split("/")[-1] for d in dirs if d.split("/")[-2].startswith("lrn")]

    return {"directories": lrn_dirs}
