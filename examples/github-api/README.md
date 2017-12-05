This is an example of using the uplink client. This is an API written in flask that gets the top
users who have commited in repositories matching a given keyword (in the name, readme, or description
in the last month.

To try this out, first fill out keys.sh with your github api client id and client secret so that
you can use the API.

Then run
```
source keys.sh
python3 Server.py
```

These are the endpoints I've written:
```
Get a list of users who have committed in repos matching the keyword since oldest-age weeks ago
/users?keyword=<keyword>[?oldest-age=<age in weeks>]

Get a list of users who have committed in the given repo since oldest-age weeks ago
/users/<user>/repo/<repo_name>[?oldest-age=<age in weeks>]

Get a list of repos matching the keyword
/repos?keyword=<keyword>
```

I've written a quick test script to try out all the endpoints:
```
python3 Tests.py
```
