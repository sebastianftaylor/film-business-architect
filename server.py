from flask import Flask, request, jsonify
from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
import json
import os

# Initialize Flask app
app = Flask(__name__)

# Define required scopes
SCOPES = ['https://www.googleapis.com/auth/drive.file', 'https://www.googleapis.com/auth/documents']

# Function to get credentials
def get_credentials():
    # Load token from file
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

    # Refresh token if needed
    if creds.expired and creds.refresh_token:
        creds.refresh(Request())

        # Save updated token
        with open('token.json', 'w') as token_file:
            updated_token_data = {
                'token': creds.token,
                'refresh_token': creds.refresh_token,
                'token_uri': creds.token_uri,
                'client_id': creds.client_id,
                'client_secret': creds.client_secret,
                'scopes': creds.scopes
            }
            json.dump(updated_token_data, token_file)

    return creds

# Route to create Google Doc
@app.route('/create-document', methods=['POST'])
def create_document():
    """
    Expects JSON input: { "title": "My New Document", "content": "Hello, world!" }
    """
    try:
        data = request.get_json(force=True)
        title = data.get('title', 'Untitled Document')
        content = data.get('content', '')

        creds = get_credentials()

        # Build Google Docs service
        docs_service = build('docs', 'v1', credentials=creds)

        # Create a new doc
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

        # Return the document URL
        doc_url = f"https://docs.google.com/document/d/{doc_id}/edit"
        return jsonify({"documentId": doc_id, "docUrl": doc_url})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Flask entry point
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))  # Default to port 5000 if PORT is not set
    app.run(host='0.0.0.0', port=port, debug=True)
