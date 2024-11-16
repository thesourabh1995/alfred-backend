from openai import OpenAI
import requests
from requests.auth import HTTPBasicAuth
from config import JIRA_URL, JIRA_EMAIL, JIRA_API_TOKEN, OPENAI_API_KEY
from models.JiraResponse import JiraResponse
from models.ticket import Ticket
from typing import List, Optional

client = OpenAI(api_key=OPENAI_API_KEY)

def generate_jql_query(user_input: str) -> str:
    messages = [
        {"role": "system", "content": "You are a helpful assistant that converts natural language to Jira JQL queries. Response will only have jql query, no text or description is required"},
        {"role": "user", "content": f'Convert the following natural language query to a Jira JQL query: "{user_input}"'}
    ]

    completion = client.chat.completions.create(
        model="gpt-4o-mini",  # You can use another available model
        messages=messages
    )

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
    params = {'jql': jql_query}

    response = requests.get(
        url,
        headers=headers,
        auth=HTTPBasicAuth(JIRA_EMAIL, JIRA_API_TOKEN),
        params=params
    )
    # Parse the response and check if it's in valid JSON format
    try:
        return response.json()
    except ValueError as e:
        return {"status": "error", "message": "Invalid JSON response from Jira."}

def parse_jira_response(response: JiraResponse) -> List[Ticket]:
    tickets = []
    for issue in response["issues"]:
        # print("assignee : ", issue["fields"]["assignee"]["displayName"])
        ticket = Ticket(
            id=issue["id"],
            key=issue["key"],
            summary=issue["fields"]["summary"],
            assignee=issue["fields"]["assignee"]["displayName"],
            creator=issue["fields"]["creator"]["displayName"],
            reporter=issue["fields"]["reporter"]["displayName"],
            status=issue["fields"]["status"]["name"],
            priority=issue["fields"]["priority"]["name"],
            created=issue["fields"]["created"],
            updated=issue["fields"]["updated"],
            project=issue["fields"]["project"]["name"],
        )
        tickets.append(ticket)
    return tickets

def search_tickets(user_input: str):
    jql_query = generate_jql_query(user_input)
    tickets = search_jira_tickets(jql_query)
    parsed_tickets = parse_jira_response(tickets)
    return parsed_tickets
