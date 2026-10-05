#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/wait.h>

#define MAX 1024
#define HISTORY "history.txt"

void save_history(const char *cmd) {
    FILE *f = fopen(HISTORY, "a");
    if (f) {
        fprintf(f, "%s\n", cmd);
        fclose(f);
    }
}

void show_history() {
    FILE *f = fopen(HISTORY, "r");
    char line[MAX];
    int n = 1;

    if (!f) {
        printf("No command history available.\n");
        return;
    }

    while (fgets(line, MAX, f))
        printf("%d. %s", n++, line);

    fclose(f);
}

int suggestion(const char *input, char *result) {
    FILE *f = fopen(HISTORY, "r");
    char line[MAX];
    size_t len = strlen(input);

    if (!f) return 0;

    while (fgets(line, MAX, f)) {
        line[strcspn(line, "\n")] = '\0';

        if (!strncmp(line, input, len) && strcmp(line, input)) {
            strcpy(result, line);
            fclose(f);
            return 1;
        }
    }

    fclose(f);
    return 0;
}

void run_command(char *cmd) {
    pid_t pid = fork();

    if (pid == 0) {
        execlp("sh", "sh", "-c", cmd, NULL);
        perror("exec failed");
        exit(1);
    }

    if (pid > 0)
        wait(NULL);
    else
        perror("fork failed");
}

void handle_cd(char *cmd) {
    char *home = getenv("HOME");
    char path[MAX];

    if (!home) return;

    if (!strcmp(cmd, "cd") || !strcmp(cmd, "cd ~")) {
        chdir(home);
    }
    else if (!strncmp(cmd, "cd ~/", 5)) {
        snprintf(path, MAX, "%s/%s", home, cmd + 5);
        if (chdir(path)) perror("cd");
    }
    else {
        if (chdir(cmd + 3)) perror("cd");
    }
}

int backend_mode(char *cmd) {
    if (!cmd || !strlen(cmd)) return 1;

    if (!strcmp(cmd, "history")) {
        show_history();
        return 0;
    }

    save_history(cmd);

    if (!strcmp(cmd, "cd") || !strncmp(cmd, "cd ", 3)) {
        handle_cd(cmd);
        return 0;
    }

    run_command(cmd);
    return 0;
}

int interactive_mode() {
    char cmd[MAX], sug[MAX], choice[10];

    printf("====================================\n");
    printf("   Intelligent Linux Terminal\n");
    printf("====================================\n");

    while (1) {
        printf("SmartTerminal> ");
        fflush(stdout);

        if (!fgets(cmd, MAX, stdin)) break;
        cmd[strcspn(cmd, "\n")] = '\0';

        if (!strlen(cmd)) continue;

        if (!strcmp(cmd, "exit")) {
            printf("Goodbye!\n");
            break;
        }

        if (!strcmp(cmd, "history")) {
            show_history();
            continue;
        }

        if (!strcmp(cmd, "cd") || !strncmp(cmd, "cd ", 3)) {
            save_history(cmd);
            handle_cd(cmd);
            continue;
        }

        if (suggestion(cmd, sug)) {
            printf("Suggestion: %s\n", sug);
            printf("Use this command? (y/n): ");

            if (fgets(choice, 10, stdin)) {
                if (choice[0] == 'y' || choice[0] == 'Y')
                    strcpy(cmd, sug);
            }
        }

        save_history(cmd);
        run_command(cmd);
    }

    return 0;
}

int main(int argc, char *argv[]) {
    if (argc >= 3 && !strcmp(argv[1], "--backend"))
        return backend_mode(argv[2]);

    return interactive_mode();
}

