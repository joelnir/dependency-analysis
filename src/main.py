import log;
import github;
import db;
import npm;

# Functions to use if imported as module

"""
Download repos to the Projects table.
The repos are taken from javascript repos between min and max stars

NOTE: the search only returns the first 1000 repos
"""
def download_repos(min_stars, max_stars):
    log.init_log();
    db.connect_db();

    log.log("Getting repos from github api");
    repos = github.get_repos(min_stars, max_stars);

    log.log("Saving repos in database");
    # Save repos in db
    for repo in repos:
        db.insert_project(repo);

    log.log("Repos saved in database");

    log.close_log();

def main():
    log.init_log();
    db.connect_db();

    # Code here

    log.close_log();

if __name__ == "__main__":
    main()
