from flask import Flask, request, jsonify
from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
import json
import os

app = Flask(__name__)

# The scopes you used during the OAuth flow must match here
SCOPES = ['https://www.googleapis.com/auth/drive.file', 'https://www.googleapis.com/auth/documents']

def get_credentials():
    # Load the token and create Credentials object
    with open('token.json', 'r') as token_file:
        token_data = json.load(token_file)

    creds = Credentials(
        token=token_data.get('token'),
        refresh_token=token_data.get('refresh_token'),
        token_uri=token_data.get('token_uri'),
        client_id=token_data.get('client_id'),
        client_secret=token_data.get('client_secret'),
        scopes=token_data.get('scopes')
    )

    # If the access token is expired, creds.refresh() will use the refresh token to get a new one
    if creds.expired and creds.refresh_token:
        creds.refresh(Request())

        # Save the updated token if it changed
        with open('token.json', 'w') as token_file:
            token_data = {
                'token': creds.token,
                'refresh_token': creds.refresh_token,
                'token_uri': creds.token_uri,
                'client_id': creds.client_id,
                'client_secret': creds.client_secret,
                'scopes': creds.scopes
            }
            json.dump(token_data, token_file)

    return creds

@app.route('/create-document', methods=['POST'])
def create_document():
    """
    Expects JSON input: { "title": "My New Document", "content": "Hello, world!" }
    """
    data = request.get_json(force=True)
    title = data.get('title', 'Untitled Document')
    content = data.get('content', '')

    creds = get_credentials()

    # Build the Docs service
    docs_service = build('docs', 'v1', credentials=creds)
    # Create a blank doc
    doc = docs_service.documents().create(body={"title": title}).execute()
    doc_id = doc.get('documentId')

    # Insert content if provided
    if content:
        requests = [{
            'insertText': {
                'location': {
                    'index': 1
                },
                'text': content
            }
        }]
        docs_service.documents().batchUpdate(documentId=doc_id, body={'requests': requests}).execute()

    # Return a link to the created doc
    doc_url = f"https://docs.google.com/document/d/{doc_id}/edit"
    return jsonify({"documentId": doc_id, "docUrl": doc_url})

if __name__ == '__main__':
    app.run(port=5000, debug=True)
