# This code sample uses the 'requests' library:
# http://docs.python-requests.org
import requests
from requests.auth import HTTPBasicAuth
import json

url = "https://sourabhmishra2708.atlassian.net/rest/api/3/users/search"

auth = HTTPBasicAuth("sourabhmishra2708@gmail.com", "ATATT3xFfGF0hV9ECWPbkFssZbjVSITi3ZTl8QXC8BKMQmE8jA7Vy3ciOzyccFqBa7Riek62fl_NVrbLxUUTJTGvd9kpLr0fNjiHhNnChz7yc3KwDeM6_CpxQc1tXP-Q4F1f68_rNMtG_0KrwY8JMzXLcZcbT_VXa51dbBQKNt8PP-b4Rgrj80k=205695E9")

headers = {
  "Accept": "application/json",
  "Content-Type": "application/json"
}

# Set the initial parameters for pagination (maxResults sets how many users to retrieve per request)
params = {
    "startAt": 0,  # Starting index for pagination
    "maxResults": 50,  # Number of users to retrieve per call (50 is a reasonable batch size)
}

# This list will store all the users
all_users = []

while True:
    # Make the API request
    response = requests.get(url, headers=headers, auth=auth, params=params)

    # Check if the response was successful
    if response.status_code == 200:
        users = response.json()

        # Add the retrieved users to the list
        all_users.extend(users)

        # Check if we have more users to retrieve
        if len(users) < params['maxResults']:
            # If the number of returned users is less than maxResults, we've retrieved all users
            break
        else:
            # Otherwise, update the startAt parameter to fetch the next batch of users
            params['startAt'] += params['maxResults']
    else:
        # If the request failed, print the error and stop
        print(f"Failed to fetch users: {response.status_code} - {response.text}")
        break

# Print the list of all users
print(json.dumps(all_users, indent=4))