import json
import os
from dotenv import load_dotenv
import assemblyai as aai
from sentence_transformers import SentenceTransformer
from sklearn.neighbors import NearestNeighbors
import numpy as np

load_dotenv()
aai.settings.api_key = os.getenv("ASSEMBLYAI_API_KEY")

def load_all_transcript_data():
    """
    Load and concatenate all stored transcript data from a JSON file.
    """
    with open("transcripts.json", "r") as file:
        data = json.load(file)
    sentences = []
    for item in data:
        sentences.extend(item["full_transcript"].split(". "))
    return sentences

def precompute_embeddings():
    """
    Pre-compute and store sentence embeddings for all sentences in the historical data.
    """
    print("Pre-computing embeddings for all sentences...")
    sentences = load_all_transcript_data()
    embedder = SentenceTransformer("multi-qa-mpnet-base-dot-v1")
    sentence_embeddings = np.array([embedder.encode(sentence, show_progress_bar=True) for sentence in sentences])

    # Store the embeddings and sentences in a file
    with open("sentence_embeddings.json", "w") as f:
        json.dump({
            "sentences": sentences,
            "embeddings": sentence_embeddings.tolist()  # Convert numpy array to list for JSON serialization
        }, f)
    print("Embeddings pre-computed and stored successfully.")

def load_precomputed_embeddings():
    """
    Load pre-computed sentence embeddings and corresponding sentences from a file.
    """
    with open("sentence_embeddings.json", "r") as f:
        data = json.load(f)
    return data["sentences"], np.array(data["embeddings"])

def semantic_search(user_input):
    """
    Perform semantic search on historical data based on user input using pre-computed embeddings.
    """
    sentences, sentence_embeddings = load_precomputed_embeddings()
    embedder = SentenceTransformer("multi-qa-mpnet-base-dot-v1")
    user_input_embedding = embedder.encode(user_input)

    knn = NearestNeighbors(n_neighbors=3, metric="cosine")
    knn.fit(sentence_embeddings)
    distances, indices = knn.kneighbors([user_input_embedding])

    matches = [sentences[index] for index in indices[0]]
    return matches

def ask_lemur(question):
    """
    Use LeMUR to generate a response based on the question.
    """
    client = aai.Client(aai.settings.api_key)
    response = client.lemur.generate(question=question)
    return response['text']

def chat_with_lemur_and_semantic_search():
    """
    Chat interface that uses LeMUR for generating responses and semantic search for finding relevant historical responses.
    """
    print("Chat with your audio data. Ask questions about any of your recordings. Type 'quit' to exit.")
    while True:
        user_input = input("You: ")
        if user_input.lower() == 'quit':
            print("Exiting chatbot. Goodbye!")
            break

        lemur_response = ask_lemur(user_input)
        print(f"LeMUR: {lemur_response}")

        matches = semantic_search(user_input)
        print("Semantic Search: Here are some relevant responses based on your question:")
        for match in matches:
            print(f"- {match}")

if __name__ == "__main__":
    # Uncomment the next line to precompute embeddings when needed
    # precompute_embeddings()
    chat_with_lemur_and_semantic_search()