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

# Keep track of packages currently under analysis
# (all other under analysis is somehow dependencies to this)
# This is to avoid getting stuck on circular dependencies
under_analysis = [];

"""
Returns dict with (at least) fields:
id, indirect_dep, dep_depth
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
    base_info = pkg_info.copy();

    # Index of depth level analysis is currently on
    level_index = len(under_analysis);

    # Add to list of packets currently under analysis
    under_analysis.append(base_info);

    dependency_info = npm.get_dependencies(name, version);

    npm_dependencies = dependency_info["dependencies"];
    db.add_invalid(dependency_info["invalid"]);


    package_depencies = [];

    # Do not save package info in database until on level
    # -1 means save everything, no circular dependency found
    pkg_info["save_level"] = -1;

    for pkg in npm_dependencies:
        if(pkg in under_analysis):
            # Ignore packages that are part of circular dependencies (uninteresting)
            log.log("Circular dependency to package " + pkg["name"] + " " + pkg["version"]);

            circ_index = under_analysis.index(pkg);

            # Only update if no circular dependency found yet or cycle goes higher up in analysis stack
            if((pkg_info["save_level"] == -1) or (circ_index < pkg_info["save_level"])):
                pkg_info["save_level"] = circ_index;
                log.log("No saving until on index: " + str(circ_index));
                log.log("under_analysis looks like: " + str(under_analysis));
        else:
            package_depencies.append(get_package_info(pkg["name"], pkg["version"]));

    indirect_dep = 0;
    dep_depth = 0;

    if(package_depencies):
        # Has dependencies
        for dep in package_depencies:
            if(dep["dep_depth"] > dep_depth):
                dep_depth = dep["dep_depth"];

            indirect_dep += dep["indirect_dep"] + 1; # +1 for this package

            # Control if a circular dependency has been encountered deeper
            if(("save_level" in dep) and # does not have key if entry from db
                (dep["save_level"] != -1) and
                (dep["save_level"] < level_index) and
                ((pkg_info["save_level"] == -1) or
                    (dep["save_level"] < pkg_info["save_level"]))
            ):
                # Propagate the top level that shouldn't be saved upwards
                pkg_info["save_level"] = dep["save_level"];
                log.log("Updating save_level to: " + str(dep["save_level"]) + " from package " + str(dep["name"]));
                log.log("under_analysis looks like: " + str(under_analysis));

        dep_depth += 1; # Add 1 for this level

    pkg_info["indirect_dep"] = indirect_dep;
    pkg_info["dep_depth"] = dep_depth;

    # Database insertions (if should be saved)
    if(pkg_info["save_level"] == -1 or
        pkg_info["save_level"] >= level_index):
        log.log("Inserting into db: " + name + " " + version);
        pkg_id = db.insert_package(pkg_info);
        pkg_info["id"] = pkg_id;

        # Insert dependencies
        for dep in package_depencies:
            # Reserve for unsaved packages (part of circular dependencies)
            if("id" in dep):
                db.add_package_dependency(pkg_id, dep["id"]);
            else:
                log.log("Not saving dependency from " + name + " to " + dep["name"]);

    # Remove from list of packages under analysis
    under_analysis.pop();

    return pkg_info;

def analyse_single_project(id):
    project = db.get_project(id);

    project_dep = github.get_project_dependencies(project["url"]);
    dependency_info = project_dep["dependencies"];
    dependency_info_dev = project_dep["dev_dependencies"];

    # Update invalid versions
    db.add_invalid(dependency_info["invalid"] + dependency_info_dev["invalid"]);

    complete_dependencies = {};

    # Analyse normal dependencies
    dep_depth = 0;
    indirect_dep = 0;

    if(dependency_info["dependencies"]):
        # Has dependencies
        for dep in dependency_info["dependencies"]:
            pkg_info = get_package_info(dep["name"], dep["version"]);

            # Add dependency to db
            db.add_project_dependency(id, pkg_info["id"]);

            if(pkg_info["dep_depth"] > dep_depth):
                dep_depth = pkg_info["dep_depth"];

            indirect_dep += pkg_info["indirect_dep"] + 1; # +1 for this package

        dep_depth += 1; # +1 for this level

    complete_dependencies["dep_depth"] = dep_depth;
    complete_dependencies["indirect_dep"] = indirect_dep;

    # Analyse dev dependencies
    dep_depth_dev = 0;
    indirect_dep_dev = 0;

    if(dependency_info_dev["dependencies"]):
        # Has dependencies
        for dep in dependency_info_dev["dependencies"]:
            pkg_info = get_package_info(dep["name"], dep["version"]);

            # Add dependency to db
            db.add_project_dependency(id, pkg_info["id"], True);

            if(pkg_info["dep_depth"] > dep_depth_dev):
                dep_depth_dev = pkg_info["dep_depth"];

            indirect_dep_dev += pkg_info["indirect_dep"] + 1; # +1 for this package

        dep_depth += 1; # +1 for this level

    complete_dependencies["dep_depth_dev"] = dep_depth_dev;
    complete_dependencies["indirect_dep_dev"] = indirect_dep_dev;

    # Update db
    db.update_project_dependencies(id, complete_dependencies);

def analyse_projects(start_index):
    pass

def main():
    log.init_log();
    db.connect_db();

    # Code here
    analyse_single_project(1);

    log.close_log();

if __name__ == "__main__":
    main()
