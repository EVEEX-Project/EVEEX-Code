#ifndef LOGGER_H
#define LOGGER_H

enum LogLevel {
    DEBUG, INFO, WARN, ERROR
};

extern char shouldLogToFile;
extern int currentLogLevel;
extern char logFileName[];

void helloWorld(const char *fmt);
void logDebug(const char *fmt, ...);
void logInfo(const char *fmt, ...);
void logWarn(const char *fmt, ...);
void logError(const char *fmt, ...);

void testLog();

#endif //LOGGER_H
