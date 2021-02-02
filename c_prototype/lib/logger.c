#include <stdio.h>
#include <stdarg.h>
#include "logger.h"

char shouldLogToFile = 0;
int currentLogLevel = DEBUG;
char logFileName[] = "logs.log";

void helloWorld(const char* version) {
    printf("\033[1;35m            _______    _______________  __\n");
    printf("           / ____/ |  / / ____/ ____/ |/ /\n");
    printf("          / __/  | | / / __/ / __/  |   /\n");
    printf("         / /___  | |/ / /___/ /___ /   |\n");
    printf("        /_____/  |___/_____/_____//_/|_|\n");
    printf("          ___  ___  / __/ _ \\/ ___/ _ |\n");
    printf("         / _ \\/ _ \\/ _// ___/ (_ / __ |\n");
    printf("         \\___/_//_/_/ /_/   \\___/_/ |_|\n\n");
    printf("\033[0;36m32-bit RISC-V Open Source video compression program\n");
    printf("                version \033[0;31m%s\033[0m\n\n", version);
    printf("─────────────────────\033[1;37m LOGS \033[0m────────────────────────\n");
}

// TODO : fixer la sauvegarde dans un fichier
void logToFile(const char *fmt, ...) {
    if (shouldLogToFile) {
        va_list args;
        va_start(args, fmt);
        FILE *pF = fopen(logFileName, "a");
        fprintf(pF, fmt, args);
        fclose(pF);
        va_end(args);
    }
}

void logDebug(const char *fmt, ...) {
    char buffer[4096];
    va_list args;

    va_start(args, fmt);
    vsprintf(buffer, fmt, args);
    va_end(args);

    if (currentLogLevel <= DEBUG)
        printf("[\033[1;35m*\033[0m] \033[0;35mDEBUG\033[0m : %s", buffer);
    logToFile("[*] DEBUG : %s", buffer);
}

void logInfo(const char *fmt, ...) {
    char buffer[4096];
    va_list args;

    va_start(args, fmt);
    vsprintf(buffer, fmt, args);
    va_end(args);

    if (currentLogLevel <= INFO)
        printf("[\033[1;34m+\033[0m] \033[0;34mINFO\033[0m  : %s", buffer);
    logToFile("[+] INFO  : %s", buffer);
}

void logWarn(const char *fmt, ...) {
    char buffer[4096];
    va_list args;

    va_start(args, fmt);
    vsprintf(buffer, fmt, args);
    va_end(args);

    if (currentLogLevel <= WARN)
        printf("[\033[1;33m-\033[0m] \033[0;33mWARN\033[0m  : %s", buffer);
    logToFile("[-] WARN  : %s", buffer);
}

void logError(const char *fmt, ...) {
    char buffer[4096];
    va_list args;

    va_start(args, fmt);
    vsprintf(buffer, fmt, args);
    va_end(args);

    if (currentLogLevel <= ERROR)
        printf("[\033[1;31m-\033[0m] \033[0;31mERROR\033[0m : %s", buffer);
    logToFile("[-] ERROR : %s", buffer);
}

void testLog() {
    logDebug("This is a debug log\n");
    logInfo("This is an info log\n");
    logWarn("This is a warning log\n");
    logError("This is an error log\n");
}