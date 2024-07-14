from googleapiclient.discovery import build
from google.oauth2.service_account import Credentials
from googleapiclient.http import MediaIoBaseUpload
import gspread
import pandas as pd
import io

# Define the scope
scope = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
]

# Add your credentials
creds = Credentials.from_service_account_file(r'C:\Users\zohai\OneDrive\Projects\LL_FinancialDashboard\key.json', scopes=scope)
client = gspread.authorize(creds)

# Google Drive API setup
drive_service = build('drive', 'v3', credentials=creds)

# Folder ID (replace with your folder ID)
folder_id = '1YyFQwmCj1dC8Y0qz-UTMA2pxDEVaNQQS'

# List all files in the folder
results = drive_service.files().list(
    q=f"'{folder_id}' in parents and trashed=false",  # only non-trashed files in the folder
    pageSize=1000,
    fields="files(id, name, mimeType)"
).execute()
items = results.get('files', [])

# Process Google Sheets files
dataframes = []

for item in items:
    if item['mimeType'] == 'application/vnd.google-apps.spreadsheet':
        try:
            sheet = client.open_by_key(item['id']).sheet1
            df = pd.DataFrame(sheet.get_all_records())
            dataframes.append(df)
        except Exception as e:
            print(f"An error occurred processing file {item['name']} ({item['id']}): {e}")

# Combine all dataframes into a single one
if dataframes:
    combined_df = pd.concat(dataframes, ignore_index=True)
    
    # Use an in-memory buffer to save the CSV data
    csv_buffer = io.BytesIO()
    combined_df.to_csv(csv_buffer, index=False, encoding='utf-8')
    csv_buffer.seek(0)  # Move the buffer cursor to the beginning
    print("Data combined and saved to an in-memory buffer.")
else:
    print("No Google Sheets files were processed.")

# Check if the combined_data.csv file exists in Google Drive
existing_file_id = None
for item in items:
    if item['name'] == 'combined_data.csv':
        existing_file_id = item['id']
        break

# Upload or update the file on Google Drive
file_metadata = {
    'name': 'combined_data.csv',
    'parents': [folder_id]
}
media = MediaIoBaseUpload(csv_buffer, mimetype='text/csv')

if existing_file_id:
    # Update the existing file
    drive_service.files().update(
        fileId=existing_file_id,
        media_body=media
    ).execute()
    print("File updated on Google Drive with ID:", existing_file_id)
else:
    # Upload as a new file
    drive_service.files().create(
        body=file_metadata,
        media_body=media,
        fields='id'
    ).execute()
    print("File uploaded to Google Drive")

print("Process complete.")
