-- File for setting up database

-- Table of all projects
CREATE TABLE Project (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name varchar(255) NOT NULL,
    url varchar(255),
    stars INTEGER
);

-- Table of all projects in sample set
CREATE TABLE SampleProject (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name varchar(255) NOT NULL,
    url varchar(255),
    stars INTEGER,
    indirect_dep INTEGER,
    dep_depth INTEGER,
    indirect_dep_dev INTEGER,
    dep_depth_dev INTEGER
);

-- Table of all known versions of npm packages
CREATE TABLE PackageVersion (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name varchar(255) NOT NULL,
    version varchar(255),
    indirect_dep INTEGER,
    dep_depth INTEGER,
    indirect_dep_dev INTEGER,
    dep_depth_dev INTEGER
);

-- Table of dependencies from project to npm package
CREATE TABLE ProjectDependency (
    project_id INTEGER,
    package_id INTEGER,
    PRIMARY KEY (project_id, package_id),
    FOREIGN KEY (project_id) REFERENCES SampleProject(id),
    FOREIGN KEY (package_id) REFERENCES PackageVersion(id)
);

-- Table of dev-dependencies from project to npm package
CREATE TABLE ProjectDevDependency (
    project_id INTEGER,
    package_id INTEGER,
    PRIMARY KEY (project_id, package_id),
    FOREIGN KEY (project_id) REFERENCES SampleProject(id),
    FOREIGN KEY (package_id) REFERENCES PackageVersion(id)
);

-- Table of dependencies from one npm package to another
CREATE TABLE PackageDependency (
    dependent_id INTEGER,
    dependency_id INTEGER,
    PRIMARY KEY (dependent_id, dependency_id),
    FOREIGN KEY (dependent_id) REFERENCES PackageVersion(id),
    FOREIGN KEY (dependency_id) REFERENCES PackageVersion(id)
);

-- Table of dev-dependencies from one npm package to another
CREATE TABLE PackageDevDependency (
    dependent_id INTEGER,
    dependency_id INTEGER,
    PRIMARY KEY (dependent_id, dependency_id),
    FOREIGN KEY (dependent_id) REFERENCES PackageVersion(id),
    FOREIGN KEY (dependency_id) REFERENCES PackageVersion(id)
);
