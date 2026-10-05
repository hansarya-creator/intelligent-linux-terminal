from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import subprocess
import os


app = FastAPI(title="Intelligent Linux Terminal API")


# Allow the frontend to communicate with the backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5500",
        "http://localhost:5500"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class CommandRequest(BaseModel):
    command: str


PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Absolute path of the C terminal executable
TERMINAL_PATH = os.path.join(PROJECT_DIR, "terminal")

# Current directory of the web terminal
current_dir = PROJECT_DIR


def get_suggestion(command):
    """
    Find a previous command from history that starts
    with the same text as the current command.
    """

    history_file = os.path.join(PROJECT_DIR, "history.txt")

    if not os.path.exists(history_file):
        return None

    command = command.strip()

    if not command:
        return None

    try:
        with open(history_file, "r") as file:
            for line in file:
                previous_command = line.strip()

                if (
                    previous_command
                    and previous_command != command
                    and previous_command.startswith(command)
                ):
                    return previous_command

    except Exception:
        return None

    return None


@app.get("/")
def home():
    return {
        "message": "Intelligent Linux Terminal Backend is running!"
    }


@app.post("/execute")
def execute_command(request: CommandRequest):
    global current_dir

    try:
        command = request.command.strip()

        if not command:
            return {
                "command": command,
                "output": "",
                "error": "Command cannot be empty.",
                "suggestion": None,
                "return_code": 1,
                "current_directory": current_dir
            }

        # -------------------------------------------------
        # HANDLE CLEAR
        # -------------------------------------------------
        if command == "clear":
            return {
                "command": command,
                "output": "",
                "error": "",
                "suggestion": None,
                "return_code": 0,
                "current_directory": current_dir
            }

        # -------------------------------------------------
        # HANDLE CD
        # -------------------------------------------------
        if command == "cd" or command.startswith("cd "):

            target = command[2:].strip()

            if target == "" or target == "~":
                new_dir = os.path.expanduser("~")

            elif target.startswith("~/"):
                new_dir = os.path.expanduser(target)

            else:
                if os.path.isabs(target):
                    new_dir = target
                else:
                    new_dir = os.path.join(current_dir, target)

            new_dir = os.path.abspath(new_dir)

            if os.path.isdir(new_dir):
                current_dir = new_dir

                return {
                    "command": command,
                    "output": "",
                    "error": "",
                    "suggestion": None,
                    "return_code": 0,
                    "current_directory": current_dir
                }

            return {
                "command": command,
                "output": "",
                "error": f"cd: no such directory: {target}",
                "suggestion": None,
                "return_code": 1,
                "current_directory": current_dir
            }

        # -------------------------------------------------
        # CHECK FOR INTELLIGENT SUGGESTION
        # -------------------------------------------------
        suggestion = get_suggestion(command)

        # -------------------------------------------------
        # EXECUTE COMMAND USING C SMART TERMINAL
        # -------------------------------------------------
        result = subprocess.run(
            [TERMINAL_PATH, "--backend", command],
            capture_output=True,
            text=True,
            cwd=current_dir
        )

        return {
            "command": command,
            "output": result.stdout,
            "error": result.stderr,
            "suggestion": suggestion,
            "return_code": result.returncode,
            "current_directory": current_dir
        }

    except Exception as e:
        return {
            "command": request.command,
            "output": "",
            "error": str(e),
            "suggestion": None,
            "return_code": 1,
            "current_directory": current_dir
        }
