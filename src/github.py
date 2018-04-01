import requests;
import log;

MIN_STARS = 1000;
SAMPLE_SIZE = 1000;

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
            repo_obj = {"name": json_repo["name"], "url": json_repo["html_url"], "stars":json_repo["stargazers_count"]};
            repos.append(repo_obj);
            log.log(str(repo_obj));

        page_i += 1;

    return repos;
