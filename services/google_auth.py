import json
import os
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
import pickle

# Scopes required for Google Sign-In
SCOPES = ['https://www.googleapis.com/auth/userinfo.email',
          'https://www.googleapis.com/auth/userinfo.profile',
          'openid']

CREDENTIALS_FILE = 'credentials.json'
TOKEN_FILE = 'token.pickle'


def get_google_user_info():
    """
    Authenticate with Google and return user info
    Returns: dict with email, name, and google_id
    """
    creds = None
    
    # Always delete old token to force account selection
    if os.path.exists(TOKEN_FILE):
        os.remove(TOKEN_FILE)
        creds = None
    
    # Always prompt for account selection
    if not os.path.exists(CREDENTIALS_FILE):
        return None, "credentials.json file not found. Please download it from Google Cloud Console."
    
    try:
        flow = InstalledAppFlow.from_client_secrets_file(
            CREDENTIALS_FILE, SCOPES)
        
        # Force account selection screen every time
        creds = flow.run_local_server(
            port=0,
            prompt='select_account',  # Show account picker
            authorization_prompt_message='Please select your Google account to continue.'
        )
        
        # Save credentials temporarily (will be deleted on next login)
        with open(TOKEN_FILE, 'wb') as token:
            pickle.dump(creds, token)
    except Exception as e:
        return None, f"Authentication failed: {str(e)}"
    
    # Get user info from Google
    try:
        from googleapiclient.discovery import build
        service = build('oauth2', 'v2', credentials=creds)
        user_info = service.userinfo().get().execute()
        
        return {
            'email': user_info.get('email'),
            'name': user_info.get('name'),
            'google_id': user_info.get('id'),
            'picture': user_info.get('picture')
        }, None
    except Exception as e:
        return None, str(e)


def clear_google_token():
    """Clear saved Google token (for logout)"""
    if os.path.exists(TOKEN_FILE):
        os.remove(TOKEN_FILE)