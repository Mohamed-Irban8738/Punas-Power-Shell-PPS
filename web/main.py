from contextlib import redirect_stdout
from io import StringIO

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from src.shell import PunasShell


# ==========================================
# FASTAPI APPLICATION
# ==========================================

app = FastAPI(
    title="Punas Power Shell",
    version="1.0.0"
)


# ==========================================
# CORS
# ==========================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==========================================
# SHELL INSTANCE
# ==========================================

shell = PunasShell()


# ==========================================
# REQUEST MODEL
# ==========================================

class CommandRequest(BaseModel):
    command: str


# ==========================================
# ROOT
# ==========================================

@app.get("/")
def root():
    return {
        "name": "Punas Power Shell",
        "version": shell.VERSION,
        "status": "running"
    }


# ==========================================
# EXECUTE COMMAND
# ==========================================

@app.post("/api/execute")
def execute_command(request: CommandRequest):

    command = request.command.strip()

    # Empty command
    if not command:
        return {
            "success": True,
            "command": "",
            "output": "",
            "prompt": shell.get_prompt(),
            "cwd": shell.file_manager.pwd()
        }

    # ======================================
    # CLEAR TERMINAL
    # ======================================
    #
    # clear is handled by the frontend.
    # The backend simply confirms the command.
    #

    if command.lower() == "clear":
        return {
            "success": True,
            "command": command,
            "output": "",
            "prompt": shell.get_prompt(),
            "cwd": shell.file_manager.pwd()
        }

    # ======================================
    # NORMAL COMMAND EXECUTION
    # ======================================

    output = StringIO()

    try:

        with redirect_stdout(output):
            shell.process_input(command)

        return {
            "success": True,
            "command": command,
            "output": output.getvalue(),
            "prompt": shell.get_prompt(),
            "cwd": shell.file_manager.pwd()
        }

    except Exception as error:

        return {
            "success": False,
            "command": command,
            "output": str(error),
            "prompt": shell.get_prompt(),
            "cwd": shell.file_manager.pwd()
        }


# ==========================================
# COMMAND HISTORY
# ==========================================

@app.get("/api/history")
def get_history():

    return {
        "history": [
            {
                "command": entry.command,
                "timestamp": entry.timestamp.isoformat(),
                "success": entry.success
            }
            for entry in shell.history.get_all()
        ]
    }


# ==========================================
# AVAILABLE COMMANDS
# ==========================================

@app.get("/api/commands")
def get_commands():

    return {
        "commands": shell.dispatcher.get_commands()
    }


# ==========================================
# FILESYSTEM
# ==========================================

@app.get("/api/files")
def get_files():

    try:

        items = shell.file_manager.ls()

        return {
            "success": True,
            "path": shell.file_manager.pwd(),
            "items": [
                {
                    "name": name,
                    "type": item_type
                }
                for name, item_type in items
            ]
        }

    except Exception as error:

        return {
            "success": False,
            "path": "/",
            "items": [],
            "error": str(error)
        }