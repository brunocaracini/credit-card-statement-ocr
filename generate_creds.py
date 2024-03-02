import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/tasks"]


def main():
  """Shows basic usage of the Tasks API.
  Prints the title and ID of the first 10 task lists.
  """
  flow = InstalledAppFlow.from_client_secrets_file(
          "credentials.json", SCOPES
      )
  creds = flow.run_local_server(port=0)
  # Save the credentials for the next run
  with open("token.json", "w") as token:
    token.write(creds.to_json())

  try:
    service = build("tasks", "v1", credentials=creds)

    # Call the Tasks API
    results = service.tasklists().list(maxResults=10).execute()
    items = results.get("items", [])

    if not items:
      print("No task lists found.")
      return

    print("Task lists:")
    for item in items:
      print(f"{item['title']} ({item['id']})")
  except HttpError as err:
    print(err)


if __name__ == "__main__":
  main()