import sqlite3 as sqlite

DB_FILE_NAME = "db/database.db"

db_con = None

"""
Connect to SQLite database
"""
def connect_db():
    global db_con
    db_con = sqlite.connect(DB_FILE_NAME)

"""
Insert new project into Project table

project should be dict on format:
{"name": project_name, "stars": 1234, "url": "user_name/project_name"}
"""
def insert_project(project):
    name = project["name"]
    url = project["url"]
    star_count = str(project["stars"])

    query = "INSERT INTO Project (name, url, stars) VALUES('{}','{}',{})"
    filled_query = query.format(name, url, star_count)

    with db_con:
        db_cur = db_con.cursor()
        db_cur.execute(filled_query)

        return db_cur.lastrowid

"""
Move n random rows from Project to SampleProject
"""
def sample_projects(n):
    rand_query = "INSERT INTO SampleProject (name, url, stars) SELECT name, url, stars FROM Project ORDER BY RANDOM() LIMIT " + str(n) + ""

    with db_con:
        db_cur = db_con.cursor()
        db_cur.execute(rand_query)

"""
Insert package into PackageVersion table
package should be a dict that contains fields:
name, version
"""
def add_package(package):
    base_query = "INSERT INTO PackageVersion (name, version) \
        VALUES('{}','{}')"

    filled_query = base_query.format(
        package["name"],
        package["version"],
    )

    with db_con:
        db_cur = db_con.cursor()
        db_cur.execute(filled_query)

        return db_cur.lastrowid

"""
Set the package depth for project with given id
"""
def update_package_depth(id, depth):
    query = "UPDATE PackageVersion \
        SET dep_depth = {} WHERE id = {}"
    filled_query = query.format(depth, id)

    with db_con:
        db_cur = db_con.cursor()
        db_cur.execute(filled_query)

"""
Add dependency from project to package
"""
def add_project_dependency(project_id, package_id, dev):
    if dev:
        table = "ProjectDevDependency"
    else:
        table = "ProjectDependency"

    query = "INSERT INTO {} (project_id, package_id) VALUES({}, {})"
    filled_query = query.format(table, project_id, package_id)

    with db_con:
        db_cur = db_con.cursor()
        db_cur.execute(filled_query)

"""
Add dependency from package to package
"""
def add_package_dependency(dependent_id, dependency_id):
    query = "INSERT INTO PackageDependency (dependent_id, dependency_id) VALUES({}, {})"
    filled_query = query.format(dependent_id, dependency_id)

    with db_con:
        db_cur = db_con.cursor()
        db_cur.execute(filled_query)

"""
Update the SampleProject table with info about the dependency statistics for a project

project_id is the id of the project row in the table

dependency_info is a dict with the fields:
direct_dep, indirect_dep, dep_depth, direct_dep_dev, indirect_dep_dev and dep_depth_dev
"""
def update_project_dependencies(project_id, dependency_info):
    query = "UPDATE SampleProject \
        SET indirect_dep = {}, dep_depth = {}, \
        indirect_dep_dev = {}, dep_depth_dev = {}, \
        direct_dep = {}, direct_dep_dev = {} \
        WHERE id = {}"
    filled_query = query.format(
        dependency_info["indirect_dep"],
        dependency_info["dep_depth"],
        dependency_info["indirect_dep_dev"],
        dependency_info["dep_depth_dev"],
        dependency_info["direct_dep"],
        dependency_info["direct_dep_dev"],
        project_id
    )

    with db_con:
        db_cur = db_con.cursor()
        db_cur.execute(filled_query)

"""
Get an info object about a specific version of a package if it exists
If no info exists return false
"""
def get_package(name, version):
    query = 'SELECT * FROM PackageVersion WHERE name="{}" AND version="{}"'
    filled_query = query.format(name, version)

    with db_con:
        db_cur = db_con.cursor()
        db_cur.execute(filled_query)

        res = db_cur.fetchone()

    if not res:
        # Package version not found
        return False

    # Create a proper package object
    pkg = {
        "id": res[0],
        "name": res[1],
        "version": res[2],
        "dep_depth": res[3],
    }

    return pkg

"""
Get amount of projects in sample
"""
def get_project_count():
    query = 'SELECT COUNT(*) FROM SampleProject'

    with db_con:
        db_cur = db_con.cursor()
        db_cur.execute(query)

        res = db_cur.fetchone()

    return res[0]

"""
Get info about a sampled project from it's id
"""
def get_project(project_id):
    query = 'SELECT * FROM SampleProject WHERE id={}'
    filled_query = query.format(project_id)

    with db_con:
        db_cur = db_con.cursor()
        db_cur.execute(filled_query)

        res = db_cur.fetchone()

    if not res:
        # Package version not found
        return False

    # Create a proper package object
    proj = {
        "id": res[0],
        "name": res[1],
        "url": res[2],
        "stars": res[3],
        "direct_dep": res[4],
        "indirect_dep": res[5],
        "dep_depth": res[6],
        "direct_dep_dev": res[7],
        "indirect_dep_dev": res[8],
        "dep_depth_dev": res[9]
    }

    return proj

"""
Add to invalid count in sql db
"""
def add_invalid(n):
    if(n <= 0):
        # No point in updating db
        return

    query = 'UPDATE Stats SET value = value + ' + str(n) + ' WHERE name = "invalid_versions"'

    with db_con:
        db_cur = db_con.cursor()
        db_cur.execute(query)

"""
Get count of reachable packages from project

If dev is true packages reachable from devDependencies are counted
else from dependencies.
"""
def reachable_nodes(project_id, dev):
    query = """
        WITH RECURSIVE
          reachable(id) AS (
            SELECT package_id FROM {} WHERE project_id={}
            UNION
            SELECT dependency_id FROM PackageDependency, reachable
            WHERE PackageDependency.dependent_id=reachable.id
          )
        SELECT COUNT(*) FROM reachable
    """

    if(dev):
        table_name = "ProjectDevDependency"
    else:
        table_name = "ProjectDependency"

    filled_query = query.format(table_name, project_id)

    with db_con:
        db_cur = db_con.cursor()
        db_cur.execute(filled_query)

        res = db_cur.fetchone()

    return res[0]

"""
Get all values from a specific field of SampleProject tables as a list
"""
def get_values(field):
    base_query = 'SELECT {} FROM SampleProject WHERE {} IS NOT NULL';
    filled_query = base_query.format(field, field);

    with db_con:
        db_cur = db_con.cursor()
        db_cur.execute(filled_query)

        res = db_cur.fetchall()

    res = [x[0] for x in res]
    return res
