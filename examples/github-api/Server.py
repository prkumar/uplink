import sys

# add uplink directory to path
sys.path.insert(0, "../../")
import uplink
from uplink import *

import asyncio
import json
import os

from datetime import datetime, timedelta
from flask import Flask, request, jsonify

app = Flask(__name__)

BASE_URL = "https://api.github.com"
CLIENT_ID = os.environ["CLIENT_ID"]
CLIENT_SECRET = os.environ["CLIENT_SECRET"]


@headers({"Accept": "application/vnd.github.v3+json"})
class Github(Consumer):
    @get("/search/repositories?q={keyword} in:name,description,readme")
    def repos_for_keyword(
        self,
        keyword,
        client_id: Query = CLIENT_ID,
        client_secret: Query = CLIENT_SECRET,
    ):
        """ Get a list of repositories which have a given keyword in the name, description or readme """
        pass

    @get("/repos/{user}/{repo_name}/commits")
    def commits_for_repo(
        self,
        user,
        repo_name,
        since: Query,
        client_id: Query = CLIENT_ID,
        client_secret: Query = CLIENT_SECRET,
    ):
        """ Get a list of commits in a repo since some start date """
        pass


github = Github(BASE_URL, client=uplink.AiohttpClient())
loop = asyncio.get_event_loop()

# Helpers


async def _repos_for_keyword(keyword):
    """ Get repos which match the keyword search """
    r = await github.repos_for_keyword(keyword)
    r_json = await r.json()
    return [item["full_name"] for item in r_json["items"]]


async def _users_for_repo(user, repo_name, oldest_age=55):
    """ Returns users that have commited in a repo in the last N weeks """

    since = (datetime.now() - timedelta(weeks=oldest_age)).isoformat()
    r = await github.commits_for_repo(user, repo_name, since=since)
    r_json = await r.json()
    users = set()
    for commit in r_json:
        if "author" in commit and commit["author"] is not None:
            user = (
                commit["author"]["login"],
                commit["commit"]["author"]["email"],
                commit["commit"]["author"]["name"],
            )
            users.add(user)
    return list(users)


# Flask routes


@app.route("/repos", methods=["GET"])
def repos_for_keyword():
    """
  /repos?keyword=<keyword>

  Finds all repos which contain the given keyword in the name, readme, or description """
    if "keyword" not in request.args:
        return "", 400

    keyword = request.args["keyword"]
    future = _repos_for_keyword(keyword)
    repos = loop.run_until_complete(future)
    return jsonify(repos)


@app.route("/users/<user>/repo/<repo_name>", methods=["GET"])
def users_for_repo(user, repo_name):
    """
  /users/<user>/repo/<repo_name>[?oldest-age=<age in weeks>]

  Returns list of users who have commited in the resource user/repo in the last given amount of
  weeks """

    oldest_age = (
        55 if "oldest-age" not in request.args else request.args["oldest-age"]
    )
    future = _users_for_repo(user, repo_name, oldest_age=oldest_age)
    users = loop.run_until_complete(future)
    return jsonify(users)


@app.route("/users", methods=["GET"])
def users_for_keyword():
    """
  /users?keyword=<keyword>[?oldest-age=<age in weeks>]

  Find the top users who have commited in repositories matching the keyword in the last month """
    if "keyword" not in request.args:
        return "", 400

    keyword = request.args["keyword"]
    oldest_age = (
        55 if "oldest-age" not in request.args else request.args["oldest-age"]
    )

    repos_future = _repos_for_keyword(keyword)
    repos = loop.run_until_complete(repos_future)

    # gather futures for getting users from each repo
    users_futures = []
    users = set()
    for repo in repos:
        user, repo_name = repo.split("/")
        users_futures.append(
            _users_for_repo(user, repo_name, oldest_age=oldest_age)
        )

    # barrier on all the users futures
    users_results = loop.run_until_complete(asyncio.wait(users_futures))

    # gather the results
    for users_result in users_results:
        for task in users_result:
            if task.result():
                users.update(set(task.result()))

    return jsonify(list(users))


app.run("0.0.0.0")
