import sys
# add uplink directory to path
sys.path.insert(0, '../../')
from uplink import *

import json
import os

from datetime import datetime, timedelta
from flask import Flask, request, jsonify

app = Flask(__name__)

BASE_URL = 'https://api.github.com'
CLIENT_ID = os.environ['CLIENT_ID']
CLIENT_SECRET = os.environ['CLIENT_SECRET']

@headers({'Accept': 'application/vnd.github.v3+json'})
class Github(Consumer):

  @get('/search/repositories?q={keyword} in:name,description,readme')
  def repos_for_keyword(self, keyword, client_id: Query = CLIENT_ID,
    client_secret: Query = CLIENT_SECRET):
    """ Get a list of repositories which have a given keyword in the name, description or readme """
    pass

  @get('/repos/{user}/{repo_name}/commits')
  def commits_for_repo(self, user, repo_name, since: Query, client_id: Query = CLIENT_ID,
    client_secret: Query = CLIENT_SECRET):
    """ Get a list of commits in a repo since some start date """
    pass

github = Github(BASE_URL)

# Helpers

def _repos_for_keyword(keyword):
  """ Get repos which match the keyword search """

  r = github.repos_for_keyword(keyword)
  return [item['full_name'] for item in r.json()['items']]

def _users_for_repo(user, repo_name, oldest_age=55):
  """ Returns users that have commited in a repo in the last N weeks """

  since = (datetime.now() - timedelta(weeks=oldest_age)).isoformat()
  r = github.commits_for_repo(user, repo_name, since=since)
  r_json = r.json()
  users = set()
  for commit in r_json:
    if 'author' in commit and commit['author'] is not None:
      user = (commit['author']['login'], commit['commit']['author']['email'],
              commit['commit']['author']['name'])
      users.add(user)
  return list(users)

# Flask routes

@app.route('/repos', methods=['GET'])
def repos_for_keyword():
  """
  /repos?keyword=<keyword>

  Finds all repos which contain the given keyword in the name, readme, or description """
  if 'keyword' not in request.args:
    return '', 400

  keyword = request.args['keyword']
  return jsonify(_repos_for_keyword(keyword))

@app.route('/users/<user>/repo/<repo_name>', methods=['GET'])
def users_for_repo(user, repo_name):
  """
  /users/<user>/repo/<repo_name>[?oldest-age=<age in weeks>]

  Returns list of users who have commited in the resource user/repo in the last given amount of
  weeks """

  oldest_age = 55 if 'oldest-age' not in request.args else request.args['oldest-age']
  users = _users_for_repo(user, repo_name, oldest_age=oldest_age)
  return jsonify(users)

@app.route('/users', methods=['GET'])
def users_for_keyword():
  """
  /users?keyword=<keyword>[?oldest-age=<age in weeks>]

  Find the top users who have commited in repositories matching the keyword in the last month """
  if 'keyword' not in request.args:
    return '', 400

  keyword = request.args['keyword']
  oldest_age = 55 if 'oldest-age' not in request.args else request.args['oldest-age']
  repos = _repos_for_keyword(keyword)
  users = set()
  for repo in repos:
    user, repo_name = repo.split('/')
    users_list = _users_for_repo(user, repo_name, oldest_age=oldest_age)
    for user in users_list:
      users.add(tuple(user))
  return jsonify(list(users))

app.run('0.0.0.0', debug=True)
