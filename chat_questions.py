import json
import assemblyai as aai
from dotenv import load_dotenv
import os

load_dotenv()

aai.api_key = os.getenv("ASSEMBLYAI_API_KEY")

def load_all_transcript_data():
    """
    Load and concatenate all stored transcript data from a JSON file.
    """
    all_transcripts = ""
    with open("transcripts.json", "r") as file:
        data = json.load(file)
        for item in data:
            all_transcripts += item["full_transcript"] + " " 
    return all_transcripts

def ask_questions():
    """
    Continuously ask user-defined questions across all transcript data.
    """
    context = load_all_transcript_data()
    if not context:
        print("No transcript data found.")
        return

    print("Chat with your audio data. Ask questions about any of your recordings. Type 'quit' to exit.")

    client = aai.Client()  # Initialize the AssemblyAI client

    while True:
        user_input = input("You: ")
        if user_input.lower() == 'quit':
            print("Exiting chatbot. Goodbye!")
            break

        # Prepare the question for the LeMUR API
        questions = [{"question": user_input}]

        try:
            # Directly use the LeMUR API for question-answering with the historical transcript data
            result = client.lemur.question(
                input_text=context,  # Use the concatenated transcripts as the context for the questions
                questions=questions,
            )

            # Assuming 'result' contains the answers, adjust according to the actual response structure
            for qa_response in result['answers']:
                print(f"Bot: {qa_response['answer']}")
        except Exception as e:
            print(f"An error occurred: {e}")
            continue

if __name__ == "__main__":
    ask_questions()
