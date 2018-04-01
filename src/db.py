import log;
import sqlite3 as sqlite;

DB_FILE_NAME = "db/database.db";

db_con = None;

def connect_db():
    global db_con;
    db_con = sqlite.connect(DB_FILE_NAME);

"""
project should be dict on format:
{"name": project_name, "stars": 1234, "url": "https://github.com/user_name/project_name"}
"""
def insert_project(project):
    name = project["name"];
    url = project["url"];
    star_count = str(project["stars"]);

    query = "INSERT INTO Project (name, url, stars) VALUES('{}','{}',{})";
    filled_query = query.format(name, url, star_count);
    log.log(filled_query);
    with db_con:
        db_cur = db_con.cursor();
        db_cur.execute(filled_query);
