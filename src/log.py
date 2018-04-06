import datetime;

FILE_NAME = "dependency.log";
log_file = None;

"""
Open the log file for writing
"""
def init_log():
    global log_file;
    log_file = open(FILE_NAME, "a");
    log("Reopened log");

"""
Write to the log file
if do_print is True the message is also printed to stdout
"""
def log(msg, do_print = False):
    now = datetime.datetime.now();
    log_msg = str(now) + ": " + msg;

    log_file.write(log_msg + "\n");

    if(do_print):
        print(log_msg);

"""
Close the log file
"""
def close_log():
    log("Closing log");
    log_file.close();
