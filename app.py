import assemblyai as aai
import time
import os
import json
from dotenv import load_dotenv
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from notion_integration import NotionIntegration

load_dotenv()  # Load environment variables from .env file

aai.settings.api_key = os.getenv("ASSEMBLYAI_API_KEY")

CLIENT_FILE = 'credentials.json'
DOCUMENT_ID = os.getenv("GOOGLE_DOCUMENT_ID")
SCOPES = ['https://www.googleapis.com/auth/documents']

notion_integration = NotionIntegration(os.getenv("NOTION_INTEGRATION_TOKEN"))

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


def lemur_call(transcript, prev_responses):
    # Initialize the Lemur instance from the aai module.
    lemur = aai.Lemur()
    
    # The input_text is the transcript that needs to be summarized.
    input_text = transcript
    
    # Constructing the prompt with instructions for the Lemur model.
    # This prompt guides the model on how to process the transcript and previous responses.
    prompt = f"""
    You are a helpful assistant with the goal of taking diligent meeting notes.
    Your task is to create bullet points about what is being said in the live transcript that is being sent to you every 60 seconds.

    Respond only with the newest bullet points and do not include any of the older responses unless they are relevant to the next steps or recommendations.

    Here are the bullet points you have given so far:

    {prev_responses}

    Avoid making up any information not present in the transcript.
    If unsure of the answer, return nothing until more clear information is provided. 

    Avoid any preambles and also remove any text formatting.

    Instructions:
    1. Identify and list key action items from the transcript.
    2. Summarize the main points discussed in the meeting.
    3. Highlight any deadlines mentioned and specify the responsible persons for each action item.
    4. Avoid including irrelevant details or information not present in the transcript.
    5. Provide the summary and action items in a structured and organized manner.

    """
    
    try:
        # Sending the prompt and transcript to the Lemur model for processing.
        # The model is configured with a temperature of 0.8 for creativity balance and a max output size of 3000 characters.
        response = lemur.task(
            prompt=prompt,
            input_text=input_text,  
            final_model="default",
            temperature=0.5,  
            max_output_size=3000
        )
        
        # Printing the response from Lemur for debugging purposes.
        print(response)
        
        # Updating the Google Docs with the response received from Lemur.
        update_google_docs(response.response)
        
        # Returning the response for further processing or storage.
        return response.response 
    except Exception as e:
        # In case of any errors during the process, print the error and return a string "Error".
        print("Error:", e)
        return "Error"

class TranscriptAccumulator:
    def __init__(self):
        # Initializes the TranscriptAccumulator class with empty transcript and previous responses.
        # Also, sets the last update time to the current time.
        self.transcript = ""
        self.prev_responses = ""
        self.last_update_time = time.time()

    def add_transcript(self, transcript_segment):
        # This method adds a new segment of transcript to the accumulator.
        # It concatenates the new segment to the existing transcript with a space for readability.
        self.transcript += " " + transcript_segment
        current_time = time.time()  # Captures the current time to check if 60 seconds have passed.
        if current_time - self.last_update_time > 60:
            # If more than 60 seconds have passed since the last update, it processes the accumulated transcript.
            self.lemur_output = lemur_call(self.transcript, self.prev_responses)
            #Notion integration
            page_id = os.getenv("NOTION_PAGE_ID")
            notion_integration.update_notion_page(page_id, self.lemur_output)
            # The output from the Lemur model is stored as the latest response.
            self.prev_responses = self.lemur_output  # Appends the new output to previous responses with a new line for separation.
            self.store_full_transcript()  # Store the full transcript before clearing it
            self.transcript = ""  # Clears the transcript for the next accumulation cycle.
            self.last_update_time = current_time  # Updates the last update time to the current time.
            self.store_action_items_as_json(self.lemur_output)  # Stores the action items from the Lemur output into a JSON file.

    def store_action_items_as_json(self, lemur_output):
        # This method stores the structured Lemur output into a JSON file named 'action_items.json'.
        structured_data = self.parse_lemur_output(lemur_output)  # Parses the Lemur output into a structured format.
        file_path = "action_items.json"
        try:
            with open(file_path, "r+") as file:
                # Tries to open the file in read+write mode to update the existing content.
                data = json.load(file)  # Loads the existing data from the file.
                data.append(structured_data)  # Appends the new structured data to the existing data.
                file.seek(0)  # Moves the file cursor to the beginning of the file.
                json.dump(data, file, indent=4)  # Writes the updated data back to the file with indentation for readability.
        except FileNotFoundError:
            # If the file does not exist, it creates a new file and writes the structured data into it.
            with open(file_path, "w") as file:
                json.dump([structured_data], file, indent=4)  # Writes the structured data as a list into the new file.

    def parse_lemur_output(self, lemur_output):
        # This method should be implemented to parse the Lemur output into a structured format suitable for JSON storage.
        # The placeholder structure includes meeting date, action items, recommendations, and next steps.
        structured_data = {
            "meeting_date": time.strftime("%Y-%m-%d", time.gmtime()),  # Formats the current date in YYYY-MM-DD format.
            "action_items": [
                # Placeholder for action items extracted from lemur_output.
            ],
            "recommendations": [
                # Placeholder for recommendations extracted from lemur_output.
            ],
            "next_steps": [
                # Placeholder for next steps extracted from lemur_output.
            ]
        }
        return structured_data  # Returns the structured data for storage.
    
    def store_full_transcript(self):
        """
        Stores the full transcript in a JSON file named 'transcripts.json'.
        """
        structured_transcript = {
            "meeting_id": "unique_meeting_identifier",  # Generate or pass a unique identifier
            "full_transcript": self.transcript,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
        }
        file_path = "transcripts.json"
        try:
            with open(file_path, "r+") as file:  # Corrected indentation for the 'with' statement
                try:
                    data = json.load(file)  # Attempts to load existing data
                except json.JSONDecodeError:  # Handles empty file scenario
                    data = []  # Initialize as empty list if file is empty
                data.append(structured_transcript)  # Appends new transcript
                file.seek(0)  # Resets file position to the beginning
                json.dump(data, file, indent=4)  # Writes updated data back to file
        except FileNotFoundError:  # Handles file not found scenario
            with open(file_path, "w") as file:  # Creates a new file if it doesn't exist
                json.dump([structured_transcript], file, indent=4)  # Writes the structured transcript as a list

transcript_accumulator = TranscriptAccumulator()  # Instantiates the TranscriptAccumulator class.

def on_open(session_opened: aai.RealtimeSessionOpened):  # Defines a function to handle the event when a session is opened.
    print("Session opened with ID:", session_opened.session_id)  # Prints the session ID when a session is opened.


def on_error(error: aai.RealtimeError):
    print("Error:", error)


def on_close():
    print("Session closed")

def on_data(transcript: aai.RealtimeTranscript):
    # Check if the transcript text is empty, if so, return immediately.
    if not transcript.text:
        return

    # Check if the transcript is of type RealtimeFinalTranscript, which indicates the end of a spoken segment.
    if isinstance(transcript, aai.RealtimeFinalTranscript):
        # Print the transcript text to the console, adding a new line at the end for readability.
        print(transcript.text, end="\r\n")
        # Add the transcript text to the TranscriptAccumulator instance for processing and storage.
        transcript_accumulator.add_transcript(transcript.text)

# Create an instance of RealtimeTranscriber from the assemblyai module.
# This instance is configured with a sample rate of 16,000 Hz, which is a common sample rate for audio recordings.
# The on_data, on_error, on_open, and on_close functions are passed as callbacks to handle different events during transcription.
transcriber = aai.RealtimeTranscriber(
    sample_rate=16_000,
    on_data=on_data,
    on_error=on_error,
    on_open=on_open,
    on_close=on_close,
)

# Establish a connection to the AssemblyAI API for real-time transcription.
transcriber.connect()

# Create an instance of MicrophoneStream from the assemblyai.extras module.
# This instance captures audio input from the microphone at a sample rate of 16,000 Hz.
microphone_stream = aai.extras.MicrophoneStream(sample_rate=16_000)

# Start streaming audio data from the microphone to the RealtimeTranscriber instance for transcription.
transcriber.stream(microphone_stream)

# Close the transcription stream once done.
# This is important to release resources and properly terminate the connection to the AssemblyAI API.
transcriber.close()