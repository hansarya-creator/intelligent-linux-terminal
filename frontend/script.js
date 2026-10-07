const input = document.getElementById("commandInput");
const terminal = document.getElementById("terminal");
const executeBtn = document.getElementById("executeBtn");

let currentSuggestion = "";


/* =========================================================
   EXECUTE COMMAND
========================================================= */

async function executeCommand(command) {

    if (typeof command !== "string") {
        command = input.value.trim();
    }

    command = command.trim();

    if (!command) {
        return;
    }

    try {

        const response = await fetch(
            "http://127.0.0.1:8000/execute",
            {
                method: "POST",

                headers: {
                    "Content-Type": "application/json"
                },

                body: JSON.stringify({
                    command: command
                })
            }
        );

        const data = await response.json();


        /* CLEAR */

        if (command === "clear" || data.clear === true) {

            terminal.innerHTML = "";

            currentSuggestion = "";

            input.value = "";

            input.focus();

            return;
        }


        /* DISPLAY RESULT */

        displayResult(data, command);


        /* SUGGESTION */

        if (data.suggestion) {

            currentSuggestion = data.suggestion;

            input.value = data.suggestion;

        } else {

            currentSuggestion = "";

            input.value = "";
        }


    } catch (error) {

        terminal.innerHTML += `
            <div class="error">
                Backend connection error.
            </div>
        `;
    }


    terminal.scrollTop = terminal.scrollHeight;

    input.focus();
}


/* =========================================================
   DISPLAY RESULT
========================================================= */

function displayResult(data, command) {

    const block = document.createElement("div");

    block.className = "command-line";


    let html = `

        <div>

            <span class="prompt">
                SmartTerminal&gt;
            </span>

            <span class="command">
                ${escapeHtml(command)}
            </span>

        </div>

    `;


    if (data.suggestion) {

        html += `

            <div class="suggestion">

                💡 Suggestion:

                <span>
                    ${escapeHtml(data.suggestion)}
                </span>

                <br>

                <small>
                    Press ENTER to use this suggestion
                </small>

            </div>

        `;
    }


    if (data.output) {

        html += `

            <div class="output">

                ${escapeHtml(data.output)}

            </div>

        `;
    }


    if (data.error) {

        html += `

            <div class="error">

                ${escapeHtml(data.error)}

            </div>

        `;
    }


    block.innerHTML = html;

    terminal.appendChild(block);
}


/* =========================================================
   ESCAPE HTML
========================================================= */

function escapeHtml(text) {

    const div = document.createElement("div");

    div.textContent = text;

    return div.innerHTML;
}


/* =========================================================
   EXECUTE BUTTON
========================================================= */

if (executeBtn) {

    executeBtn.addEventListener(
        "click",
        function () {

            executeCommand();

        }
    );
}


/* =========================================================
   ENTER KEY
========================================================= */

if (input) {

    input.addEventListener(
        "keydown",
        function (event) {

            if (event.key === "Enter") {

                event.preventDefault();

                if (currentSuggestion) {

                    const suggestion =
                        currentSuggestion;

                    currentSuggestion = "";

                    executeCommand(suggestion);

                } else {

                    executeCommand();

                }
            }
        }
    );
}


/* =========================================================
   QUICK COMMANDS
========================================================= */

function quickCommand(command) {

    input.value = command;

    executeCommand(command);
}


/* =========================================================
   THEME BUTTONS
========================================================= */

function enableLightMode() {

    document.body.classList.add("light-mode");

    localStorage.setItem(
        "terminalTheme",
        "light"
    );
}


function enableDarkMode() {

    document.body.classList.remove("light-mode");

    localStorage.setItem(
        "terminalTheme",
        "dark"
    );
}


/* =========================================================
   SETTINGS
========================================================= */

function openSettings() {

    alert(
        "Intelligent Linux Terminal\n\n" +
        "Backend: Connected\n" +
        "Shell: Linux\n" +
        "Command Suggestions: Enabled"
    );
}


/* =========================================================
   CONNECT HEADER BUTTONS
========================================================= */

const buttons =
    document.querySelectorAll("button");

buttons.forEach(function(button) {

    const title =
        button.getAttribute("title");

    if (title === "Light Mode") {

        button.addEventListener(
            "click",
            enableLightMode
        );

    }

    if (title === "Dark Mode") {

        button.addEventListener(
            "click",
            enableDarkMode
        );

    }

    if (title === "Settings") {

        button.addEventListener(
            "click",
            openSettings
        );

    }

});


/* =========================================================
   LOAD SAVED THEME
========================================================= */

const savedTheme =
    localStorage.getItem("terminalTheme");

if (savedTheme === "light") {

    enableLightMode();

}