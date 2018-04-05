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

"""
Returns dict with (at least) fields:
id, indirect_dep, dep_depth
"""
def get_package_info(name, version):
    pkg_db = db.get_package(name, version);

    if(pkg_db):
        # Return dicitonary (note that this contains some unneeded fields)
        return pkg_db

    log.log("Not found in db: " + name + " " + version);

    # New package-version, need to analyse
    pkg_info = {
        "name": name,
        "version": version
    };

    dependency_info = npm.get_dependencies(name, version);

    npm_dependencies = dependency_info["dependencies"];
    invalid_c = dependency_info["invalid"]; # TODO Store invalid amount

    package_depencies = [get_package_info(pkg["name"], pkg["version"]) for pkg in npm_dependencies];

    indirect_dep = 0;
    dep_depth = 0;

    if(package_depencies):
        # Has dependencies
        for dep in package_depencies:
            if(dep["dep_depth"] > dep_depth):
                dep_depth = dep["dep_depth"];

            indirect_dep += dep["indirect_dep"] + 1; # +1 for this package

        dep_depth += 1; # Add 1 for this level

    pkg_info["indirect_dep"] = indirect_dep;
    pkg_info["dep_depth"] = dep_depth;

    # Database insertions
    pkg_id = db.insert_package(pkg_info);
    pkg_info["id"] = pkg_id;

    # Insert dependencies
    for dep in package_depencies:
        db.add_package_dependency(pkg_id, dep["id"]);

    return pkg_info;

def analyse_projects(start_index):
    pass

def main():
    log.init_log();
    db.connect_db();

    # Code here
    a = get_package_info("js-yaml", "3.11.0");
    print(a);

    log.close_log();

if __name__ == "__main__":
    main()
