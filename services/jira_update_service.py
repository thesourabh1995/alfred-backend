from openai import OpenAI
import requests
from requests.auth import HTTPBasicAuth
from config import JIRA_URL, JIRA_EMAIL, JIRA_API_TOKEN, OPENAI_API_KEY
from models.ApiFormat import ApiFormat
from models.JiraResponse import JiraResponse
from models.UserIntent import UserIntent
from models.ticket import Ticket
from typing import List, Dict, Optional
import json

client = OpenAI(api_key=OPENAI_API_KEY)

transition = [
  {
    "id": "11",
    "name": "To Do"
  },
  {
    "id": "21",
    "name": "In Progress"
  },
  {
    "id": "31",
    "name": "Done"
  },
  {
    "id": "41",
    "name": "Reopened"
  }
]

current_user = "developer1"

def read_text_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()

def prompt_processor_update(intent_object):
    """Prompt OpenAI to determine intent and extract parameters."""
    file_content = ""
    try:
        file_content = read_text_file('api_prompt_context.txt')
    except Exception as e:
        print(e)

    messages = [
        {
            "role": "system",
            "content": (
                "You are a Jira Cloud REST API assistant. Your task is to identify the user's intent and generate appropriate steps "
                "with corresponding Jira REST API URLs, payloads, and HTTP methods (POST, PUT, GET, DELETE) based on the user's input.\n\n"
                "The input might involve creating, reading, updating, or deleting issues, adding or editing comments, updating issue status, or other Jira-related tasks. "
                "You need to determine the operation type and provide the correct REST API endpoints, payloads, and HTTP methods according to the Jira Cloud REST API documentation.\n\n"
                "If the user's input requires multiple steps to complete, break it down into individual operations (e.g., adding a comment and updating issue status).\n\n"
                "Here is how you will respond:\n"
                "1. Identify the intent: Is the user trying to create an issue, update a field, add a comment, update the status, retrieve issue details, analytical information or delete something?\n"
                "2. If multiple operations are required, generate the steps sequentially. For each step, generate:\n"
                "   - The appropriate Jira Cloud REST API URL (e.g., '/rest/api/3/issue/{issue_id}/comment').\n"
                "   - payload must be pure JSON format, without any comment.\n"
                "   - The HTTP method (POST for create, PUT for update, GET for read, DELETE for delete).\n"
                "3. Return the output in strictly JSON format, containing an array of steps. Each step should have keys: 'url', 'payload', and 'method'.\n"
                "4. Ensure the format is strictly JSON avoid any wrapper or description.\n\n"
                "Example inputs:\n"
                "1. \"Create a new issue in project ABC with summary 'Bug found' and description 'Error 500 on login'.\"\n"
                "2. \"Update the comment on issue XYZ-123 with 'The issue has been resolved'.\"\n"
                "3. \"Close the issue 1234 with comment 'Issue resolved'.\"\n"
                "4. \"Retrieve all issues assigned to me.\"\n\n"
                "5. \"If query has the only transition update required choose appropriate transition id from below object : \"\n\n"
                f"{transition},\n\n"
                "For example, if the input is 'Close the issue 1234 with comment Issue resolved', the output should have two steps:\n"
                "Step 1: Add the comment\n"
                "Step 2: Update the issue status to 'Done'\n\n"
                "User Input : \"\n\n"
                f"{intent_object},\n\n"
                f"Additional context from the text file:\n{file_content}\n\n"
                "Output the result in pure JSON format without any comment, explanation or wrappers. Keys should be 'url', 'payload' (pure JSON format), and 'method'. Strictly JSON.\n\n"
                "Make sure to use the latest Jira Cloud REST API documentation and include all necessary fields in the JSON payload for each action."
            )
        }
    ]

    completion = client.chat.completions.create(
        model="gpt-4o-mini",  # Adjust as needed
        messages=messages,
        temperature=0.5
    )
    response_content = completion.choices[0].message.content.strip()
    print(response_content)
    try:
        api_response = json.loads(response_content)
        # print("API response : ", api_response)
        return api_response

    except json.JSONDecodeError as e:
        print(f"Error parsing JSON: {e}")
        return {"error": "Invalid JSON format", "raw_response": response_content}

def prompt_user_intent(user_input: str) -> UserIntent:
    """Prompt OpenAI to determine intent and extract parameters."""
    messages = [
        {
            "role": "system",
            "content": (
                "You are a virtual assistant for Jira issue management. "
                "You need to identify the user's intent and extract relevant parameters. "
                "The user might want to either update an issue or query tickets.\n\n"
                "Must Output a JSON with 'intent' ('update', 'query', 'analytics') , 'parameters' and original text. "
                "Example: { 'intent': 'update', 'parameters': { 'issue_id': 'ID', 'summary': '...', 'description': '...' }}."
            )
        },
        {"role": "user", "content": f"{user_input}"}
    ]

    completion = client.chat.completions.create(
        model="gpt-4o-mini",  # Adjust as needed
        messages=messages
    )

    response_content = completion.choices[0].message.content.strip()
    print(json.loads(response_content))
    return json.loads(response_content)

def update_jira_issue(api_object):
    """Update a Jira issue."""
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json"
    }

    url = f'{JIRA_URL}'+f'{api_object.url}'
    try:
        response = {}
        if api_object.method == "POST":
            response = requests.post(
                url,
                headers=headers,
                auth=HTTPBasicAuth(JIRA_EMAIL, JIRA_API_TOKEN),
                json=api_object.payload
            )
        elif api_object.method == "PUT":
            response = requests.put(
                url,
                headers=headers,
                auth=HTTPBasicAuth(JIRA_EMAIL, JIRA_API_TOKEN),
                json=api_object.payload
            )
        print(response)
        if response.status_code == 204:
            return {"status": "success", "message": f"Issue updated successfully updated."}
    except Exception as e:
        print("response :: ", e)
        return {"status": "error", "message": "Failed to update the issue."}

def generate_jql_query(query_object: UserIntent) -> str:
    """Generate a JQL query based on user input using OpenAI API in message format."""

    # Extract parameters from the query object
    original_text = query_object.get('original_text', "")
    parameters = query_object.get('parameters', {})

    # Create a dynamic parameter description for the message content
    parameter_details = "\n".join([f'{key}: "{value}"' for key, value in parameters.items()])

    # Create the message prompt for OpenAI
    messages = [
        {
            "role": "system",
            "content": (
                "You are a virtual assistant designed to help users generate JQL queries for Jira. "
                "Convert the user's input into a valid JQL query. Response should be just jql query, avoid any description or details."
            )
        },
        {
            "role": "user",
            "content": (
                "When the user input includes context related to ticket statuses, you can assume that 'ticket closed' means the status is 'Done.' If the user input does not mention ticket statuses, please ignore this assumption.\n"
                f"User provided the following request: \"{original_text}\".\n\n"
                "Parameters provided are:\n"
                f"{parameter_details}\n\n"
                f"If user query is related to current logged-in user then use below user:\"{current_user}\". \n\n"
                "Please generate a JQL query based on this input."
            )
        }
    ]

    completion = client.chat.completions.create(
        model="gpt-4o-mini",  # Adjust as needed
        messages=messages,
        temperature=0.5
    )
    jql = completion.choices[0].message.content.strip()
    print("JQL :: ", jql)
    return jql


def search_jira_tickets(jql_query: str):
    """Search Jira tickets based on the JQL query."""
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

    try:
        return response.json()
    except ValueError:
        return {"status": "error", "message": "Invalid JSON response from Jira."}

def convert_tickets_to_dicts(tickets: List[Ticket]) -> List[dict]:
    return [ticket.model_dump() for ticket in tickets]

def generate_analytics(tickets, user_input):
    try:
        original_text = user_input.get('original_text', "")

        messages = [
            {
                "role": "system",
                "content": (
                    "You are a virtual assistant designed to generate detailed analytics reports from ticket data. "
                    "Use the provided tickets and user input to generate insightful, data-driven analysis. "
                    "Focus on key points that will reflect the risk management, performance, Efficiency and Bottlenecks and impacts"
                    "Focus on analyzing the data and provide a concise, actionable report. Report strictly should be in Markdown Text"
                )
            },
            {
                "role": "user",
                "content": (
                    f"Given the following tickets: {tickets}\n\n"
                    f"User provided the following request: \"{original_text}\".\n\n"
                    "Please generate a brief analytics report based on the user input and the ticket data in Markdown text format. Avoid any incomplete report"
                )
            }
        ]

        completion = client.chat.completions.create(
            model="gpt-4o-mini",  # Adjust as needed
            messages=messages,
            temperature=0.5
        )
        jql = completion.choices[0].message.content.strip()
        return jql
    except Exception as e:
        print("Analytics Error:: ", e)

def process_user_input(user_input: str):
    """Process user input and execute based on intent (update or query)."""
    intent_data = prompt_user_intent(user_input)
    print("user intent :: ", intent_data)
    intent = intent_data.get('intent')
    parameters = intent_data.get('parameters', {})

    if intent == 'update':
        # Extract parameters needed for update
        api_objects = prompt_processor_update(intent_data)
        result = None
        for api_object in api_objects:
            api_format = ApiFormat(**api_object)
            print("api object:", api_format)
            result = update_jira_issue(api_format)
            print("API response:", result)  # Optional: Print each API response
        return {"intent": "update", "data": result}


    elif intent == "analytics":
        jql_query = generate_jql_query(intent_data)
        tickets = search_jira_tickets(jql_query)
        parsed_issues = parse_jira_response(tickets)
        analytics = generate_analytics(parsed_issues, intent_data)
        print("analysis : ", analytics)
        return {"intent": "analytics", "data": analytics}

    elif intent == 'query':
        # Generate a JQL query based on user input
        tickets = []
        jql_query = generate_jql_query(intent_data)
        tickets = search_jira_tickets(jql_query)
        parsed_issues = parse_jira_response(tickets)
        if isinstance(parsed_issues, list):
            tickets = [
                {
                    "id": ticket.id,
                    "key": ticket.key,
                    "summary": ticket.summary,
                    "assignee": ticket.assignee,
                    "creator": ticket.creator,
                    "reporter": ticket.reporter,
                    "status": ticket.status,
                    "priority": ticket.priority,
                    "created": ticket.created,
                    "updated": ticket.updated,
                }
                for ticket in parsed_issues
            ]
        return {"intent": "query", "data": tickets}

    else:
        return {"status": "error", "data": "Unknown intent. Please specify if you want to 'update' or 'query' or 'analytics'."}


def parse_jira_response(response: JiraResponse) -> List[Ticket]:
    tickets = []
    for issue in response["issues"]:
        print("issue : ", issue)
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

def initiate_process(user_input):
    response = process_user_input(user_input)
    print(response)
    return response


def convert_voice_to_text(user_input):
    response = process_user_input(user_input)
    print(response)
    return response

def save_ticket(issue_data):
    url = f'{JIRA_URL}/rest/api/3/issue'
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json"
    }

    response = requests.post(
        url,
        data=json.dumps(issue_data),
        headers=headers,
        auth=HTTPBasicAuth(JIRA_EMAIL, JIRA_API_TOKEN)
    )

    if response.status_code == 201:
        print("Response:", response.json())
        return {"status": "success", "message": "Issue created successfully!"}
    else:
        return {"status": "error", "message": "Error while creating issue!"}
