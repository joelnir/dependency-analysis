import requests;
import log;
import npm;

"""
Get list of repos from github with star amount between min_stars and max_stars

returns list of dicts with keys:
name, url and stars
"""
def get_repos(min_stars, max_stars):
    base_query = "https://api.github.com/search/repositories?q=language:javascript+stars:{}..{}&per_page=100";
    filled_query = base_query.format(str(min_stars), str(max_stars));

    repos = [];

    total_count = 101; # Total repos found through query (unknown until first query)
    page_i = 1;

    # Only 10 pages are available from github api
    while ((total_count//100) + 1) >= page_i and page_i <= 10:
        log.log("Getting repos from page " + str(page_i));
        query = filled_query + "&page="+str(page_i);

        response = requests.get(query);
        json_data = response.json();

        if(page_i == 1):
            #Update total total_count
            total_count = json_data["total_count"];
            log.log(str(total_count) + " total results from search " + query);

        json_repos = json_data["items"];

        for json_repo in json_repos:
            repo_obj = {"name": json_repo["name"], "url": json_repo["full_name"], "stars":json_repo["stargazers_count"]};
            repos.append(repo_obj);

        page_i += 1;

    return repos;

"""
Get info about dependencies from github package.json file
url should be on format username/projectname

returns dict with keys dependencies and dev_dependencies
These entries contain list of
dependencies (on format from npm.decode_dependencies)
"""
def get_project_dependencies(url):
    base_url = "https://raw.githubusercontent.com/{}/master/package.json"
    filled_url = base_url.format(url);

    response = requests.get(filled_url);

    if(response.status_code == 404):
        # package.json file not found
        log.log("No package.json file found for " + url);
        return False

    try:
        json_data = response.json();
    except:
        log.log("Failed to read json for " + url, True);
        return False

    if("dependencies" in json_data):
        deps = json_data["dependencies"];
        decoded_deps = npm.decode_dependencies(deps);
    else:
        # No dependencies
        decoded_deps = {"invalid": 0, "dependencies": []};

    if("devDependencies" in json_data):
        dev_deps = json_data["devDependencies"];
        decoded_dev_deps = npm.decode_dependencies(dev_deps);
    else:
        # No dev-dependencies
        decoded_dev_deps = {"invalid": 0, "dependencies": []};

    dep_info = {
        "dependencies": decoded_deps,
        "dev_dependencies": decoded_dev_deps
    }

    return dep_info;
