from notion_client import Client
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

class NotionIntegration:
    def __init__(self, integration_token):
        # Initialize the Notion client with the provided integration token
        self.notion = Client(auth=integration_token)

    def update_notion_page(self, page_id, content):
        # Attempt to update a Notion page with the given content
        try:
            # Append a new paragraph block to the children of the specified page
            self.notion.pages.update(
                page_id=page_id,
                properties={},
                children=[
                    {
                        "object": "block",
                        "type": "paragraph",
                        "paragraph": {
                            "text": [
                                {
                                    "type": "text",
                                    "text": {
                                        "content": content,
                                    }
                                }
                            ]
                        }
                    }
                ]
            )
            # If successful, print a success message
            print("Notion page updated successfully.")
        except Exception as e:
            # If an error occurs, print an error message with the exception
            print(f"Failed to update Notion page: {e}")

notion_integration = NotionIntegration(os.getenv("NOTION_INTEGRATION_TOKEN"))