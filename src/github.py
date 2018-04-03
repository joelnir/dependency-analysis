import requests;
import log;
import npm;

MIN_STARS = 1000;

def get_repos():
    base_query = 'https://api.github.com/search/repositories?q=language:javascript+stars:>' + str(MIN_STARS) + "&per_page=100";
    repos = [];


    total_count = 101; # Total repos found through query (unknown until first query)
    page_i = 1;

    while (total_count//100) >= page_i:
        log.log("Getting repos from page " + str(page_i));
        query = base_query + "&page="+str(page_i);

        response = requests.get(query);
        json_data = response.json();

        if(page_i == 1):
            #Update total total_count
            total_count = json_data["total_count"];
            log.log(str(total_count) + " total results from search");

        json_repos = json_data["items"];

        for json_repo in json_repos:
            repo_obj = {"name": json_repo["name"], "url": json_repo["full_name"], "stars":json_repo["stargazers_count"]};
            repos.append(repo_obj);
            log.log(str(repo_obj));

        page_i += 1;

    return repos;

"""

"""
def get_project_dependencies(url):
    base_url = "https://raw.githubusercontent.com/{}/master/package.json"
    filled_url = base_url.format(url);

    response = requests.get(filled_url);

    if(response.status_code == 404):
        # package.json file not found
        return False

    json_data = response.json();

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
