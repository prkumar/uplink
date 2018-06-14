import requests
import pprint


def test_repo():
    r = requests.get(
        "http://localhost:5000/repos?keyword=natural+language+processing"
    )
    pprint.pprint(r.json())


def test_users_for_repos():
    r = requests.get(
        "http://localhost:5000/users/JustFollowUs/repo/Natural-Language-Processing"
    )
    pprint.pprint(r.json())


def test_users_for_keyword():
    r = requests.get("http://localhost:5000/users?keyword=lstm")
    pprint.pprint(r.json())


test_repo()
test_users_for_repos()
test_users_for_keyword()
