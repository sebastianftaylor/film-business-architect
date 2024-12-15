from __future__ import print_function
import os.path
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import json

# Scopes define what access you’re requesting
SCOPES = ['https://www.googleapis.com/auth/drive.file', 'https://www.googleapis.com/auth/documents']
CREDS_FILE = 'credentials.json'

def main():
    creds = None
    # Check if token.json (where we'll store your tokens) already exists
    if os.path.exists('token.json'):
        with open('token.json', 'r') as token:
            creds = json.load(token)

    if not creds or not creds.get('refresh_token'):
        # Initiate the OAuth flow
        flow = InstalledAppFlow.from_client_secrets_file(CREDS_FILE, SCOPES)
        # run_local_server will handle the redirect automatically, use port=3000 if you like
        creds = flow.run_local_server(port=3000, prompt='consent', authorization_prompt_message='')
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            json.dump({
                'token': creds.token,
                'refresh_token': creds.refresh_token,
                'token_uri': creds.token_uri,
                'client_id': creds.client_id,
                'client_secret': creds.client_secret,
                'scopes': creds.scopes
            }, token)
    
    print("Refresh token:", creds.get('refresh_token'))

if __name__ == '__main__':
    main()
