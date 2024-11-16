from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException, UploadFile, File
from pydantic import BaseModel

from models.FieldModel import CreateTicketModel
from models.FormInput import FormInput
from models.ticket import Ticket
from services.TranscriptionService import TranscriptionService
from services.jira_service import search_tickets
from services.jira_update_service import initiate_process, save_ticket

router = APIRouter(prefix="/assistant")
service = TranscriptionService()

class SearchQuery(BaseModel):
    user_input: str


def convert_form_input_to_api_object(form_input: FormInput) -> dict:
    current_date = datetime.now(timezone.utc).isoformat()
    return {
        "fields": {
            "assignee": {
                "id": form_input.assignee  # Assuming assignee ID is passed here
            },
            "description": {
                "content": [
                    {
                        "content": [
                            {
                                "text": form_input.description,  # Use the description from FormInput
                                "type": "text"
                            }
                        ],
                        "type": "paragraph"
                    }
                ],
                "type": "doc",
                "version": 1
            },
            "issuetype": {
                "id": form_input.issuetype  # Use the issue type ID from FormInput
            },
            "priority": {
                "id": form_input.priority  # Use the priority ID from FormInput
            },
            "project": {
                "id": form_input.project  # Use the project ID from FormInput
            },
            "summary": form_input.summary,  # Use the summary from FormInput
            "created": current_date  # Use the created date from FormInput
        },
        "update": {}
    }

@router.post("/search-tickets")
async def search_tickets_handler(query: SearchQuery):
    try:
        user_input = query.user_input
        tickets_response = search_tickets(user_input)

        if isinstance(tickets_response, list):
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
                for ticket in tickets_response
            ]

            # Return the tickets as a response
            return {"tickets": tickets}
        else:
            raise ValueError("Expected a list of tickets.")
    except Exception as e:
        # Log the exception or handle it as needed
        return {"error": str(e)}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/assistant")
async def start_assistance(query: SearchQuery):
    try:
        user_input = query.user_input
        tickets_response = initiate_process(user_input)
        print("controller :: ", tickets_response)
        return {"response": tickets_response}
    except Exception as e:
        # Log the exception or handle it as needed
        return {"error": str(e)}

@router.post("/create-ticket")
def create_ticket(fields: FormInput):
    try:
        form_payload = convert_form_input_to_api_object(fields)
        print("form_payload :: ", form_payload)
        response = save_ticket(form_payload)
        print("save ticket response :: ", response)
        return response
    except Exception as e:
        # Log the exception or handle it as needed
        return {"error": str(e)}

@router.post("/speech-to-text")
async def transcribe_audio(file: UploadFile = File(...)):
    # Ensure the uploaded file is in mp3 format
    if not file.filename.endswith('.mp3'):
        raise HTTPException(status_code=400, detail="Only .mp3 files are allowed")

    # Save the uploaded file temporarily
    audio_file_path = f"/tmp/{file.filename}"
    with open(audio_file_path, "wb") as buffer:
        buffer.write(await file.read())

    try:
        # Call the transcription service
        transcription = service.transcribe_audio(audio_file_path)
        return {"text": transcription}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/test")
def test_endpoint():
    try:
        return {"tickets": "Test Object"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))