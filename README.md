# Cassette: A Real-Time Speech-to-Text Tool. Documents Notes in Google or Notion and Chat with Your Data using LLM's

## Overview

This application leverages AssemblyAI's Speech-to-Text API and LLM's to implement real-time speech-to-text transcription directly into Google Docs or Notion, all using Python. Designed for efficiency and ease of use, it enables users to transcribe live audio into text, making it an invaluable tool for meetings, lectures, or any scenario where real-time note-taking is essential. Trying to remember what was said, chat with your full database of recordings using LeMUR from Assembly AI.

## Features

- **Real-Time Transcription**: Utilizes AssemblyAI's cutting-edge Speech-to-Text API for accurate, real-time audio transcription.
- **Google Docs & Notion Integration**: Seamlessly updates a Google Doc or Notion page in real-time with transcribed text, allowing for immediate access and collaboration.
- **Large Language Model Summarization**: Employs LLMs to generate concise bullet points from the live transcript, enhancing the readability and utility of the notes.
- **Q&A with Historical Data**: Allows users to interact with their historical transcript data through a Q&A interface, leveraging AssemblyAI's LeMUR API for intelligent responses.
- **Notion Integration**: Automatically updates a Notion page with summarized notes and action items, providing an organized way to manage meeting outcomes.
- **Python-Based**: Fully implemented in Python, offering a flexible and developer-friendly approach to real-time transcription.


## Getting Started

### Prerequisites

- Python 3.6 or later
- Google API credentials (OAuth 2.0 client credentials)
- AssemblyAI API key
- Notion Integration Token

### Installation

1. Clone the repository to your local machine.
2. Install the required Python packages:
   ```bash
   pip install -r requirements.txt
   ```
3. Ensure you have `credentials.json` from Google Cloud Console for OAuth 2.0 client credentials and your AssemblyAI API key.

### Usage

1. Run `app.py` to start the transcription service:
   ```bash
   python app.py
   ```
2. Speak into your microphone, and watch as your speech is transcribed in real-time into the specified Google Doc or Notion page.
3. Use `chat_questions.py` to interact with your historical transcript data through a Q&A interface:

## How It Works

The application captures live audio through the microphone, processes the audio data using AssemblyAI's Speech-to-Text API, and transcribes the speech into text. It then uses a LeMUR to summarize the transcript into bullet points and updates a Google Doc or Notion page in real-time with the transcribed and summarized text.

## Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues to improve the application or suggest new features.

## License

This project is licensed under the MIT License - see the LICENSE file for details.