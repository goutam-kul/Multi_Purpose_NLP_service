from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
import os.path
import io
import pickle

class DriveLoader:
    def __init__(self):
        self.SCOPES = ['https://www.googleapis.com/auth/drive.readonly']
        self.creds = None

    def authenticate(self):
        # Check if we have valid credentials
        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                self.creds = pickle.load(token)
        
        # If no valid credentials available, let user log in
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', self.SCOPES)
                self.creds = flow.run_local_server(port=0)
            
            # Save credentials for future use
            with open('token.pickle', 'wb') as token:
                pickle.dump(self.creds, token)

    def download_model(self, file_id, destination_folder):
        """
        Download model files from Google Drive
        """
        try:
            service = build('drive', 'v3', credentials=self.creds)
            
            # Create destination folder if it doesn't exist
            os.makedirs(destination_folder, exist_ok=True)
            
            # Get file metadata
            file_metadata = service.files().get(fileId=file_id).execute()
            file_name = file_metadata.get('name')
            
            # Download file
            request = service.files().get_media(fileId=file_id)
            file = io.BytesIO()
            downloader = MediaIoBaseDownload(file, request)
            done = False
            
            while done is False:
                status, done = downloader.next_chunk()
                print(f"Download {int(status.progress() * 100)}%")
                
            file.seek(0)
            
            # Save the file
            with open(os.path.join(destination_folder, file_name), 'wb') as f:
                f.write(file.read())
                
            return os.path.join(destination_folder, file_name)
            
        except Exception as e:
            raise Exception(f"Error downloading model: {str(e)}")