import log;
import github;
import db;
import npm;
import signal;
import time;
import datetime;

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

"""
Returns dict with (at least) fields:
id, dep_depth
"""
def get_package_info(name, version):
    global under_analysis;

    pkg_db = db.get_package(name, version);

    if(pkg_db):
        # Return dicitonary (note that this contains some unneeded fields)
        log.log("Found in db: " + name + " " + version);
        return pkg_db

    log.log("Not found in db: " + name + " " + version);

    # New package-version, need to analyse
    pkg_info = {
        "name": name,
        "version": version,
    };

    # Database insertion
    log.log("Inserting into db: " + name + " " + version);
    pkg_id = db.add_package(pkg_info);
    pkg_info["id"] = pkg_id;

    dependency_info = npm.get_dependencies(name, version);

    npm_dependencies = dependency_info["dependencies"];
    db.add_invalid(dependency_info["invalid"]);

    package_depencies = [get_package_info(pkg["name"], pkg["version"]) for pkg in npm_dependencies];

    dep_depth = 0;

    if(package_depencies):
        # Has dependencies
        for dep in package_depencies:
            if(dep["dep_depth"] == None):
                # Depth not found, signals circular dependency to this package
                # Ignore packages that are part of circular dependencies (uninteresting)
                log.log("Circular dependency to package " + dep["name"] + " " + dep["version"]);
            else:
                if(dep["dep_depth"] > dep_depth):
                    dep_depth = dep["dep_depth"];

        dep_depth += 1; # Add 1 for this level


    # Update db with dependency depth
    db.update_package_depth(pkg_id, dep_depth);
    pkg_info["dep_depth"] = dep_depth;

    # Insert dependencies
    for dep in package_depencies:
        db.add_package_dependency(pkg_id, dep["id"]);

    return pkg_info;

"""
Run complete analysis of project at id and update database
"""
def analyse_single_project(id):
    project = db.get_project(id);

    log.log("Analysing project: " + project["name"], True);

    project_dep = github.get_project_dependencies(project["url"]);

    if(not project_dep):
        # No project.json file found
        return; # TODO Note this

    dependency_info = project_dep["dependencies"];
    dependency_info_dev = project_dep["dev_dependencies"];

    # Update invalid versions
    db.add_invalid(dependency_info["invalid"] + dependency_info_dev["invalid"]);

    complete_dependencies = {};

    # Analyse normal dependencies
    dep_depth = 0;
    direct_dep = len(dependency_info["dependencies"]);

    if(dependency_info["dependencies"]):
        # Has dependencies
        for dep in dependency_info["dependencies"]:
            pkg_info = get_package_info(dep["name"], dep["version"]);

            # Add dependency to db
            db.add_project_dependency(id, pkg_info["id"], False);

            if(pkg_info["dep_depth"] > dep_depth):
                dep_depth = pkg_info["dep_depth"];

        dep_depth += 1; # +1 for this level

    complete_dependencies["dep_depth"] = dep_depth;

    # Analyse dev dependencies
    dep_depth_dev = 0;
    direct_dep_dev = len(dependency_info_dev["dependencies"]);

    if(dependency_info_dev["dependencies"]):
        # Has dev-dependencies
        for dep in dependency_info_dev["dependencies"]:
            pkg_info = get_package_info(dep["name"], dep["version"]);

            # Add dependency to db
            db.add_project_dependency(id, pkg_info["id"], True);

            if(pkg_info["dep_depth"] > dep_depth_dev):
                dep_depth_dev = pkg_info["dep_depth"];

        dep_depth += 1; # +1 for this level

    complete_dependencies["dep_depth_dev"] = dep_depth_dev;

    # Set direct dependencies
    complete_dependencies["direct_dep"] = direct_dep;
    complete_dependencies["direct_dep_dev"] = direct_dep_dev;

    # Set indirect dependencies
    complete_dependencies["indirect_dep"] = db.reachable_nodes(id, False);
    complete_dependencies["indirect_dep_dev"] = db.reachable_nodes(id, True);

    # Update db
    db.update_project_dependencies(id, complete_dependencies);

# Decides if shoudl keep running
run = True;

def catch_int(signal, frame):
    global run;

    log.log("Keyboard interrupt recieved", True);
    run = False;

def analyse_projects(start_index):
    global run;

    signal.signal(signal.SIGINT, catch_int);
    sample_size = db.get_project_count();

    i = start_index;

    start_time = 0;
    end_time = 0;

    while(run and (i <= sample_size + 13)):
        log.log("Project " + str(i) + "/" + str(sample_size), True);

        start_time = time.time();
        analyse_single_project(i);
        end_time = time.time();

        human_uptime = str(datetime.timedelta(seconds=int(end_time-start_time)));
        log.log("Analysis took " + human_uptime, True);

        i += 1;

    if(not run):
        log.log("Exiting from keyboard interrupt after index " + str(i-1), True);

    return;

def main():
    log.init_log();
    db.connect_db();

    # Code here
    analyse_projects(1);

    log.close_log();

if __name__ == "__main__":
    main()
