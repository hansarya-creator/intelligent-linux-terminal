from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import subprocess
import os


# =========================================================
# FASTAPI APPLICATION
# =========================================================

app = FastAPI(
    title="Intelligent Linux Terminal API"
)


# =========================================================
# CORS
# =========================================================

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


# =========================================================
# REQUEST MODEL
# =========================================================

class CommandRequest(BaseModel):
    command: str


# =========================================================
# PROJECT PATH
# =========================================================

PROJECT_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

TERMINAL_PATH = os.path.join(
    PROJECT_DIR,
    "terminal"
)


# Current directory used by the web terminal
current_dir = PROJECT_DIR


# =========================================================
# FIND COMMAND SUGGESTION
# =========================================================

def get_suggestion(command):

    history_file = os.path.join(
        PROJECT_DIR,
        "history.txt"
    )

    if not os.path.exists(history_file):
        return None

    command = command.strip()

    if not command:
        return None

    try:

        with open(
            history_file,
            "r"
        ) as file:

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


# =========================================================
# HOME / TEST API
# =========================================================

@app.get("/")
def home():

    return {
        "message":
        "Intelligent Linux Terminal Backend is running!"
    }


# =========================================================
# EXECUTE COMMAND
# =========================================================

@app.post("/execute")
def execute_command(
    request: CommandRequest
):

    global current_dir

    try:

        command = request.command.strip()


        # -------------------------------------------------
        # EMPTY COMMAND
        # -------------------------------------------------

        if not command:

            return {
                "command": "",
                "output": "",
                "error": "",
                "suggestion": None,
                "return_code": 0,
                "current_directory": current_dir
            }


        # -------------------------------------------------
        # CLEAR
        # -------------------------------------------------

        if command == "clear":

            return {
                "command": command,
                "output": "",
                "error": "",
                "suggestion": None,
                "return_code": 0,
                "current_directory": current_dir,
                "clear": True
            }


        # -------------------------------------------------
        # CD COMMAND
        # -------------------------------------------------

        if command == "cd" or command.startswith("cd "):

            target = command[2:].strip()


            # cd
            if target == "":
                new_dir = os.path.expanduser("~")


            # cd ~
            elif target == "~":
                new_dir = os.path.expanduser("~")


            # cd ~/folder
            elif target.startswith("~/"):
                new_dir = os.path.expanduser(target)


            # absolute path
            elif os.path.isabs(target):
                new_dir = target


            # relative path
            else:
                new_dir = os.path.join(
                    current_dir,
                    target
                )


            new_dir = os.path.abspath(
                new_dir
            )


            if os.path.isdir(new_dir):

                current_dir = new_dir

                return {
                    "command": command,
                    "output":
                        f"Changed directory to {current_dir}",
                    "error": "",
                    "suggestion": None,
                    "return_code": 0,
                    "current_directory":
                        current_dir
                }


            else:

                return {
                    "command": command,
                    "output": "",
                    "error":
                        f"cd: no such directory: {target}",
                    "suggestion": None,
                    "return_code": 1,
                    "current_directory":
                        current_dir
                }


        # -------------------------------------------------
        # CHECK FOR SUGGESTION
        # -------------------------------------------------

        suggestion = get_suggestion(command)


        # IMPORTANT:
        # If a suggestion exists, DO NOT execute
        # the incomplete command.
        #
        # Example:
        #
        # git
        #
        # suggestion:
        # git status
        #
        # The command "git" will NOT be executed.
        # Only the suggestion will be shown.

        if suggestion:

            return {
                "command": command,
                "output": "",
                "error": "",
                "suggestion": suggestion,
                "return_code": 0,
                "current_directory":
                    current_dir
            }


        # -------------------------------------------------
        # EXECUTE COMMAND
        # -------------------------------------------------

        result = subprocess.run(

            [
                TERMINAL_PATH,
                "--backend",
                command
            ],

            capture_output=True,

            text=True,

            cwd=current_dir
        )


        # -------------------------------------------------
        # RETURN RESULT
        # -------------------------------------------------

        return {

            "command": command,

            "output":
                result.stdout,

            "error":
                result.stderr,

            "suggestion":
                None,

            "return_code":
                result.returncode,

            "current_directory":
                current_dir
        }


    # =====================================================
    # ERROR HANDLING
    # =====================================================

    except Exception as e:

        return {

            "command":
                request.command,

            "output": "",

            "error":
                str(e),

            "suggestion":
                None,

            "return_code":
                1,

            "current_directory":
                current_dir
        }
