import log;
import github;
import db;

log.init_log();
db.connect_db();

db.sample_projects();

log.close_log();
