const API_URL = "http://127.0.0.1:8000";

const commandInput = document.getElementById("commandInput");
const terminalOutput = document.getElementById("terminalOutput");
const prompt = document.getElementById("prompt");


// Execute command
async function executeCommand() {
    const command = commandInput.value.trim();

    if (!command) {
        return;
    }

    // Clear command box
    commandInput.value = "";

    // Display entered command
    addCommand(command);

    // Clear screen
    if (command === "clear") {
        terminalOutput.innerHTML = "";
        return;
    }

    try {
        const response = await fetch(`${API_URL}/execute`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                command: command
            })
        });

        const data = await response.json();

        // Display command output
        if (data.output) {
            addOutput(data.output);
        }

        // Display error
        if (data.error) {
            addError(data.error);
        }

        // Display SmartTerminal suggestion
        if (data.suggestion) {
            addSuggestion(data.suggestion);
        }

        // Update current directory
        if (data.current_directory) {
            updatePrompt(data.current_directory);
        }

    } catch (error) {
        addError(
            "Unable to connect to backend.\n" +
            "Make sure FastAPI server is running."
        );
    }

    // Scroll to bottom
    terminalOutput.scrollTop = terminalOutput.scrollHeight;
}


// Add command to terminal
function addCommand(command) {
    const line = document.createElement("div");

    line.className = "command-line";

    line.innerHTML = `
        <span class="prompt-text">${getPromptText()}</span>
        <span class="command-text">${escapeHTML(command)}</span>
    `;

    terminalOutput.appendChild(line);
}


// Add normal output
function addOutput(output) {
    const element = document.createElement("div");

    element.className = "output";
    element.textContent = output;

    terminalOutput.appendChild(element);
}


// Add error output
function addError(error) {
    const element = document.createElement("div");

    element.className = "error";
    element.textContent = error;

    terminalOutput.appendChild(element);
}


// Add SmartTerminal suggestion
function addSuggestion(suggestion) {
    const element = document.createElement("div");

    element.className = "suggestion";

    element.innerHTML = `
        <strong>SmartTerminal Suggestion:</strong>
        ${escapeHTML(suggestion)}
    `;

    terminalOutput.appendChild(element);
}


// Quick command buttons
function quickCommand(command) {
    commandInput.value = command;
    commandInput.focus();

    executeCommand();
}


// Update terminal prompt
function updatePrompt(directory) {
    let displayPath = directory;

    const home = "/home/hansarya";

    if (directory === home) {
        displayPath = "~";
    } else if (directory.startsWith(home + "/")) {
        displayPath = "~" + directory.substring(home.length);
    }

    prompt.textContent = `hansarya@SmartTerminal:${displayPath}$`;
}


// Get current prompt
function getPromptText() {
    return prompt.textContent + " ";
}


// Allow Enter key to execute
commandInput.addEventListener("keydown", function(event) {
    if (event.key === "Enter") {
        executeCommand();
    }
});


// Prevent HTML injection
function escapeHTML(text) {
    const div = document.createElement("div");
    div.textContent = text;
    return div.innerHTML;
}


// Focus command box automatically
commandInput.focus();
