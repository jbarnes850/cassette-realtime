import assemblyai as aai
import time
import os
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

aai.settings.api_key = "ASSEMBLY_AI_KEY"

CLIENT_FILE = 'credentials.json'
DOCUMENT_ID = '1xIVwdVLi1mz5kauIbDVfCU3RifJBpDQK_3DxbLuB7FE'
SCOPES = ['https://www.googleapis.com/auth/documents']

def update_google_docs(content):
    creds = None
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CLIENT_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
        with open("token.json", "w") as token:
            token.write(creds.to_json())

    try:
        service = build("docs", "v1", credentials=creds)

        requests = [
            {
                'insertText': {
                    'text': content,
                    'endOfSegmentLocation': {}
                }
            }
        ]

        result = service.documents().batchUpdate(
            documentId=DOCUMENT_ID, body={'requests': requests}).execute()

    except HttpError as err:
        print(err)

## Install the following google api:
## pip install  --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib


def lemur_call(transcript, prev_responses ):
    lemur = aai.Lemur()
    input_text = transcript
    prompt = f"""
    You are a helpful assistant with the goal of taking diligent meeting notes/
    Your task is to create bullet points about what is being said in the live transcript that is being sent to you every 15 seconds.

    Respond only with the newset bullet points and do not include any of the older responses unless they are relevant to the next steps or recommendations.

    Here are the bullet points you have given so far:

    {prev_responses}

    Avoid making up any information not present in the transcript.
    If unsire of the answer, return nothing until more clear information is provided. 

    Avoid any preambles and also remove any text formatting. 

    """
    try:
        response = lemur.task(
            prompt=prompt,
            input_text=input_text,  
            final_model="default",
            temperature=0.8,  
            max_output_size=3000
        )
        print(response)
        update_google_docs(response.response)
        return response.response 
    except Exception as e:
        print("Error:", e)
        return "Error"

class TranscriptAccumulator:
    def __init__(self):
        self.transcript = ""
        self.prev_responses = ""
        self.last_update_time = time.time()

    def add_transcript(self, transcript_segment):  # Defines a method to add a new transcript segment to the accumulator.
        self.transcript += " " + transcript_segment  # Concatenates the new transcript segment to the existing transcript with a space in between.
        current_time = time.time()  # Gets the current time.
        if current_time - self.last_update_time > 15:  # Checks if more than 15 seconds have passed since the last update.
            self.lemur_output = lemur_call(self.transcript, self.prev_responses)  # Calls the lemur_call function with the current transcript and previous responses.
            self.prev_responses = self.lemur_output  # Appends the new lemur output to the previous responses, separated by a newline.
            self.transcript = ""  # Resets the transcript for the next accumulation.
            self.last_update_time = current_time  # Updates the last update time to the current time.

transcript_accumulator = TranscriptAccumulator()  # Creates an instance of the TranscriptAccumulator class.

def on_open(session_opened: aai.RealtimeSessionOpened):  # Defines a function to handle the event when a session is opened.
    print("Session opened with ID:", session_opened.session_id)  # Prints the session ID when a session is opened.


def on_error(error: aai.RealtimeError):
    print("Error:", error)


def on_close():
    print("Session closed")

def on_data(transcript: aai.RealtimeTranscript):
    if not transcript.text:
        return

    if isinstance(transcript, aai.RealtimeFinalTranscript):
        # Add new line after final transcript.
        print(transcript.text, end="\r\n")
        transcript_accumulator.add_transcript(transcript.text)

transcriber = aai.RealtimeTranscriber(
    sample_rate=16_000,
    on_data=on_data,
    on_error=on_error,
    on_open=on_open,
    on_close=on_close,
)

transcriber.connect()

microphone_stream = aai.extras.MicrophoneStream(sample_rate=16_000)

transcriber.stream(microphone_stream)

transcriber.close()
