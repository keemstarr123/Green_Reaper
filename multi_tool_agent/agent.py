import datetime
from google import genai
from zoneinfo import ZoneInfo
from google.adk.agents import Agent
from pymongo import MongoClient
from langchain_community.tools import BraveSearch
import httpx 
import asyncio
from bs4 import BeautifulSoup
from pydantic import BaseModel
from datetime import date, datetime
from google.genai import types
import json
from typing import Optional
import firebase_admin
from firebase_admin import credentials, firestore
from google.oauth2 import service_account
from pathlib import Path
from fastapi.staticfiles import StaticFiles
from google.auth.credentials import Credentials
import base64
from googleapiclient.discovery import build


# Path to your service account credentials
SERVICE_ACCOUNT_FILE2 = 'GCC_account.json'
SCOPES = ['https://www.googleapis.com/auth/calendar']

# Authenticate the service account
credentials3 = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE2, scopes=SCOPES
)

# Build the Calendar API client
service = build('calendar', 'v3', credentials=credentials3)

class Address(BaseModel):
    address: str

class DateTimeField(BaseModel):
    dateTime: str
    timeZone: str

class GoogleCalendarEvent(BaseModel):
    summary: str
    location: str
    description: str 
    start: DateTimeField
    end: DateTimeField

class GoogleEventList(BaseModel):
    event_list: list[GoogleCalendarEvent]

cred = credentials.Certificate("green-reaper.json")
app = firebase_admin.initialize_app(cred)
print("✅ Firebase initialized successfully!")
db = firestore.client()

brave_search_api = "BSAuaNApqhevBk3yppJtcPmITC2VR6s"

search_tool = BraveSearch.from_api_key(api_key = brave_search_api, search_kwargs={"count":3})

async def fetch_pages(url):
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url)
            soup = BeautifulSoup(response.text, 'html.parser')
            body = soup.find("body")
            if body:
                return body.get_text(separator="\n", strip=True)
            else:
                return f"[No <body> tag found for {url}]"
        except Exception as e:
            return f"[Error fetching {url}]: {str(e)}"
    

async def main(urls):
    tasks = [fetch_pages(url) for url in urls]
    results = await asyncio.gather(*tasks)
    return results

async def browse_internet(query: str) -> str:
    """
    Searches the internet in real-time to retrieve information not present in the LLM's training data.
    Simplify and explain about the output and then return back to users.

    This tool:
    - Uses a live search engine to find relevant web pages for the given query.
    - Fetches and parses the HTML content of each result.
    - Returns the raw or structured content (e.g., page body text) from those pages.

    Useful for answering up-to-date questions about recent events, facts, or topics the LLM may not know.

    Args:
        query (str): The user's search question or topic.

    Returns:
        str: Combined text or HTML from the <body> of top search result pages.
    """
    result = json.loads(search_tool.run(query))
    urls = [i['link'] for i in result]
    contents = await main(urls)
    return contents

def add_event(event:GoogleCalendarEvent):
    """
    Populate the required arguments automatically based on your understanding of the context.
    If specific fields are missing, use your best judgment to infer values (e.g., appropriate event titles, dates, or locations) consistent with construction tender scheduling practices.
    ALL field must be presented with values (MAY MAKE UR OWN ASSUMPTIONS) !important

    This tool:
    - Uses the Google Calendar API to insert a new event into a specified shared calendar.
    - Accepts a structured Task model containing details like summary, description, start/end time, and location.
    - Sends the event to the correct calendar ID and confirms the creation via a returned calendar event link.

    Useful for automating scheduling of tender-related milestones, document deadlines, team meetings, or contractor tasks.

    Args:
        event (Task): A Pydantic model representing a calendar event with fields including summary, location, description, start, end, and timezone.
        Include:
        - summary: A short, clear title of the action item
        - location: Where the action occurs (or "Online" if not location-specific)
        - description: A concise elaboration of what the action entails and why it is required
        - start: Scheduled start date/time in ISO 8601 format (e.g., "2025-05-10T09:00:00+08:00")
        - end: Scheduled end date/time in ISO 8601 format
        - timeZone: Use "Asia/Kuala_Lumpur" by default
    Returns:
        str: A confirmation message with a link to the created event in Google Calendar.
    """
    calendar_id = "1fcbaedeedb15f25a1c8e71ad79eded5f1a118c95cf4c32f091ce736c140e41d@group.calendar.google.com"
    created_event = service.events().insert(calendarId=calendar_id, body=event).execute()
    return ("✅ Event created:", created_event['htmlLink'])

        
def get_tender_document():
    items = list(db.collection("caching_data").order_by("timestamp", direction=firestore.Query.DESCENDING).stream())[0].to_dict()
    print(items)
    document = items['document']
    
    return document 

def make_changes(original_submission:str, change_request: str):
    """
    Generates a revised construction tender document by interpreting and applying vague or specific change requests using AI.

    This tool:
    - Uses Gemini Pro to interpret user change requests and generate Python code that edits Word documents.
    - Injects the original tender submission and requested changes into a prompt for code generation.
    - Executes the generated Python script to construct a new `.docx` file reflecting all modifications.

    Useful for automating tender updates, proposal revisions, and document personalization without manual editing.

    Args:
        original_data (str): The full original tender submission text as a multi-line string.
        change_request (List[str]): A list of change instructions. These can be specific (e.g., “update the deadline”) or vague (e.g., “emphasize sustainability”).

    Returns:
        str: The path to the revised Word document (e.g., 'Revised_Tender_Submission.docx') that can be sent to the frontend for user download.
    """
    CHANGES_PROMPT = f'''
    Role:
    You are the best prompt engineer in the world and an expert Python developer specializing in document automation. You excel at translating vague change requests into precise, executable code.

    Task:
    Based on the **Original Tender Submission** and the **Change Requests** provided below, generate a complete Python script that uses the `python-docx` library to:

    1. Load the original submission text (you may assume it’s provided as a multi-line string or read from a file).  
    2. Programmatically apply each change request to the text (e.g., insert sections, update wording, add bullet lists).  
    3. Construct a new Word document (`.docx`) that reflects all requested revisions, preserving headings, formatting, and any tables or lists.  
    4. Save the resulting document as `Revised_Tender_Submission.docx`.

    If any change request is too vague to implement directly, include a brief inline comment in the code asking for clarification (e.g., `# TODO: clarify what “expand risk section” means exactly`).

    Input Placeholders:
    ```python
    original_text = """
    {original_submission}
    """

    change_requests ={change_request}
    ]
    '''

    client = genai.Client(
      vertexai=True,
      project="green-reaper",
      location="global",
  )


    model = "gemini-2.5-pro-preview-03-25"
    contents = [
    types.Content(
      role="user",
      parts=[types.Part.from_text(text=CHANGES_PROMPT)]
    )
  ]
    generate_content_config = types.GenerateContentConfig(
    temperature = 1,
    top_p = 0.95,
    seed = 0,
    max_output_tokens = 8192,
    response_modalities = ["TEXT"],
    safety_settings = [types.SafetySetting(
      category="HARM_CATEGORY_HATE_SPEECH",
      threshold="OFF"
    ),types.SafetySetting(
      category="HARM_CATEGORY_DANGEROUS_CONTENT",
      threshold="OFF"
    ),types.SafetySetting(
      category="HARM_CATEGORY_SEXUALLY_EXPLICIT",
      threshold="OFF"),types.SafetySetting(
      category="HARM_CATEGORY_HARASSMENT",
      threshold="OFF"
    )],
  )

    output = client.models.generate_content(
    model = model,
    contents = contents,
    config = generate_content_config,
    )
    print(output)
    return "File has been saved to output Revised_Tender_Submission.docx"



def get_weather(city: str) -> dict:
    """Retrieves the current weather report for a specified city.

    Args:
        city (str): The name of the city for which to retrieve the weather report.

    Returns:
        dict: status and result or error msg.
    """
    if city.lower() == "new york":
        return {
            "status": "success",
            "report": (
                "The weather in New York is sunny with a temperature of 25 degrees"
                " Celsius (77 degrees Fahrenheit)."
            ),
        }
    else:
        return {
            "status": "error",
            "error_message": f"Weather information for '{city}' is not available.",
        }


def get_current_time(city: str) -> dict:
    """Returns the current time in a specified city.

    Args:
        city (str): The name of the city for which to retrieve the current time.

    Returns:
        dict: status and result or error msg.
    """

    if city.lower() == "new york":
        tz_identifier = "America/New_York"
    else:
        return {
            "status": "error",
            "error_message": (
                f"Sorry, I don't have timezone information for {city}."
            ),
        }

    tz = ZoneInfo(tz_identifier)
    now = datetime.datetime.now(tz)
    report = (
        f'The current time in {city} is {now.strftime("%Y-%m-%d %H:%M:%S %Z%z")}'
    )
    return {"status": "success", "report": report}


root_agent = Agent(
    name="construction_tender_validator_agent",
    model="gemini-2.0-flash-001",
    description=(
        f"A highly experienced construction consultant with over 20 years of expertise in the industry. This agent specializes in answering questions related to construction project planning, sustainable building practices, material selection, scheduling, budgeting, and site management. It provides professional advice for residential, commercial, and infrastructure projects based on industry best practices and real-world insights. today's date {datetime.today().strftime("%Y-%m-%d")} Always give short and concise answer in 1-2 sentence. "
    ),
    instruction=(
        """
Always structure your response as:  
<h2 class="text-lg font-bold text-gray-800 mb-2">Your headline here</h2>  
<p class="text-sm text-gray-700">Your concise advice here.</p>"""
    ),
    tools=[get_weather, get_current_time, add_event, make_changes, browse_internet],
)