from openai import OpenAI
import requests
from requests.auth import HTTPBasicAuth
from config import JIRA_URL, JIRA_EMAIL, JIRA_API_TOKEN, OPENAI_API_KEY

openai_api_key = 'openai_api_key'
JIRA_URL = JIRA_URL
JIRA_EMAIL = JIRA_EMAIL
JIRA_API_TOKEN = JIRA_API_TOKEN
client = OpenAI(api_key=OPENAI_API_KEY)

def generate_jql_query(user_input):
    messages = [
        {"role": "system",
         "content": "You are a helpful assistant that converts natural language to Jira JQL queries. Response will only have jql query, no text or description is required"},
        {"role": "user", "content": f'Convert the following natural language query to a Jira JQL query: "{user_input}"'}
    ]

    completion = client.chat.completions.create(
        model="gpt-4o-mini",  # You can use another available model
        messages=messages
    )

    print(completion)
    message_content = completion.choices[0].message.content.strip()

    if '```jql' in message_content:
        jql_query = message_content.split('```jql')[1].split('```')[0].strip()
    else:
        jql_query = message_content

    return jql_query


def search_jira_tickets(jql_query):
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json"
    }

    url = f'{JIRA_URL}/rest/api/3/search'

    print("jql_query : "+jql_query)
    params = {
        'jql': jql_query
    }

    response = requests.get(
        url,
        headers=headers,
        auth=HTTPBasicAuth(JIRA_EMAIL, JIRA_API_TOKEN),
        params=params
    )

    if response.status_code == 200:
        print("Jira API success response")
        return response.json()  # Returns Jira tickets as JSON
    else:
        print("Jira API failure response")
        return response.status_code, response.text  # Returns error details

def parse_jira_response(response):
    issues = response.get("issues", [])

    parsed_issues = []

    for issue in issues:
        issue_data = {
            "id": issue.get("id"),
            "key": issue.get("key"),
            "summary": issue["fields"].get("summary"),
            "description": issue["fields"].get("description", {}).get("content"),
            "assignee": issue["fields"].get("assignee", {}).get("displayName"),
            "creator": issue["fields"].get("creator", {}).get("displayName"),
            "reporter": issue["fields"].get("reporter", {}).get("displayName"),
            "status": issue["fields"].get("status", {}).get("name"),
            "priority": issue["fields"].get("priority", {}).get("name"),
            "created": issue["fields"].get("created"),
            "updated": issue["fields"].get("updated"),
            "project": issue["fields"].get("project", {}).get("name"),
            "issuetype": issue["fields"].get("issuetype", {}).get("name"),
            "watches": issue["fields"].get("watches", {}).get("watchCount"),
            "timeoriginalestimate": issue["fields"].get("timeoriginalestimate"),
            "timeestimate": issue["fields"].get("timeestimate"),
            "fixVersions": [v.get("name") for v in issue["fields"].get("fixVersions", [])],
            "labels": issue["fields"].get("labels", []),
            "subtasks": [subtask.get("key") for subtask in issue["fields"].get("subtasks", [])]
        }

        parsed_issues.append(issue_data)

    return parsed_issues

def search_tickets(user_input):
    jql_query = generate_jql_query(user_input)
    print(f"Generated JQL Query: {jql_query}")
    tickets = search_jira_tickets(jql_query)
    parsed_tickets = parse_jira_response(tickets)
    return parsed_tickets

if __name__ == '__main__':
    user_question = "Show me all the tickets from project project1 and assignee to user name Developer"
    tickets = search_tickets(user_question)
    print(tickets)