import datetime;

FILE_NAME = "dependency.log";
log_file = 0;

def init_log():
    global log_file;
    log_file = open(FILE_NAME, "a");
    log("Reopened log");

def log(msg):
    now = datetime.datetime.now();
    log_msg = str(now) + ": " + msg;

    log_file.write(log_msg + "\n");
    print(log_msg);

def close_log():
    log("Closing log");
    log_file.close();
