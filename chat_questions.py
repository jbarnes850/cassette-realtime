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

def semantic_search(user_input, sentences, sentence_embeddings):
    """
    Perform semantic search on historical data based on user input.
    """
    embedder = SentenceTransformer("multi-qa-mpnet-base-dot-v1")
    user_input_embedding = embedder.encode(user_input)

    # Use k-nearest neighbors to find the most semantically similar sentences
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
    sentences = load_all_transcript_data()
    embedder = SentenceTransformer("multi-qa-mpnet-base-dot-v1")
    sentence_embeddings = np.array([embedder.encode(sentence) for sentence in sentences])

    print("Chat with your audio data. Ask questions about any of your recordings. Type 'quit' to exit.")
    while True:
        user_input = input("You: ")
        if user_input.lower() == 'quit':
            print("Exiting chatbot. Goodbye!")
            break

        # Use LeMUR to generate a response based on the user's question
        lemur_response = ask_lemur(user_input)
        print(f"LeMUR: {lemur_response}")

        # Perform semantic search to find relevant historical responses
        matches = semantic_search(user_input, sentences, sentence_embeddings)
        print("Semantic Search: Here are some relevant responses based on your question:")
        for match in matches:
            print(f"- {match}")

if __name__ == "__main__":
    chat_with_lemur_and_semantic_search()