#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/wait.h>

#define MAX_COMMAND 1024
#define HISTORY_FILE "history.txt"

void save_history(const char *command) {
    FILE *file = fopen(HISTORY_FILE, "a");

    if (file == NULL) {
        perror("Unable to open history file");
        return;
    }

    fprintf(file, "%s\n", command);
    fclose(file);
}

void show_history() {
    FILE *file = fopen(HISTORY_FILE, "r");
    char line[MAX_COMMAND];
    int count = 1;

    if (file == NULL) {
        printf("No command history available.\n");
        return;
    }

    while (fgets(line, sizeof(line), file) != NULL) {
        printf("%d. %s", count, line);
        count++;
    }

    fclose(file);
}

/* Find a command from history that starts with user input */
int find_suggestion(const char *input, char *suggestion) {
    FILE *file = fopen(HISTORY_FILE, "r");
    char line[MAX_COMMAND];
    size_t input_len = strlen(input);

    if (file == NULL) {
        return 0;
    }

    while (fgets(line, sizeof(line), file) != NULL) {
        line[strcspn(line, "\n")] = '\0';

        if (strncmp(line, input, input_len) == 0 &&
            strcmp(line, input) != 0) {

            strcpy(suggestion, line);
            fclose(file);
            return 1;
        }
    }

    fclose(file);
    return 0;
}

void execute_command(char *command) {
    pid_t pid = fork();

    if (pid < 0) {
        perror("fork failed");
    }
    else if (pid == 0) {
        execlp("sh", "sh", "-c", command, NULL);

        perror("Command execution failed");
        exit(1);
    }
    else {
        wait(NULL);
    }
}

int main() {
    char command[MAX_COMMAND];
    char suggestion[MAX_COMMAND];
    char choice[10];

    printf("====================================\n");
    printf("   Intelligent Linux Terminal\n");
    printf("====================================\n");

    while (1) {
        printf("SmartTerminal> ");

        if (fgets(command, sizeof(command), stdin) == NULL) {
            break;
        }

        command[strcspn(command, "\n")] = '\0';

        if (strlen(command) == 0) {
            continue;
        }

        /* Exit */
        if (strcmp(command, "exit") == 0) {
            printf("Goodbye!\n");
            break;
        }

        /* History */
        if (strcmp(command, "history") == 0) {
            show_history();
            continue;
        }

                        /* Handle cd */
        if (strcmp(command, "cd") == 0 || strncmp(command, "cd ", 3) == 0) {
            save_history(command);

            if (strcmp(command, "cd") == 0) {
                const char *home = getenv("HOME");

                if (home == NULL || chdir(home) != 0) {
                    perror("cd failed");
                }
            } else {
                if (chdir(command + 3) != 0) {
                    perror("cd failed");
                }
            }

            continue;
        }

        /* Search history for a suggestion */
        if (find_suggestion(command, suggestion)) {
            printf("Suggestion: %s\n", suggestion);
            printf("Use this command? (y/n): ");

            if (fgets(choice, sizeof(choice), stdin) != NULL) {
                choice[strcspn(choice, "\n")] = '\0';

                if (strcmp(choice, "y") == 0 ||
                    strcmp(choice, "Y") == 0) {

                    strcpy(command, suggestion);
                    printf("Executing: %s\n", command);
                }
            }
        }

        /* Save the final command */
        save_history(command);

        /* Execute command */
        execute_command(command);
    }

    return 0;
}
