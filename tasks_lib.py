import os
import requests
import datetime
from dotenv import load_dotenv
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow

load_dotenv()


class GoogleTasks:
    # Authentication and scopes
    scope = "https://www.googleapis.com/auth/tasks"
    oauth_endpoint = "https://oauth2.googleapis.com/token"
    access_token = None
    refresh_token = os.getenv("GOOGLE_CREDENTIALS_REFRESH_TOKEN")

    # Targets
    TARGET_TASK_LIST_ID = os.getenv("GOOGLE_TASKS_TARGET_TASK_LIST_ID")

    # Decorators:

    def google_tasks_api_service_creator(func):
        def wrapper(*args, **kwargs):
            # Authenticates and constructs service.
            service = GoogleTasks._get_service(
                api_name="tasks",
                api_version="v1",
                scopes=GoogleTasks.scope,
            )
            result = func(service, *args, **kwargs)
            return result

        return wrapper

    def logging(func):
        def wrapper(*args, **kwargs):
            # Authenticates and constructs service.
            import logging

            # Set up the logger
            logger = logging.getLogger("Google Tasks Module")
            logger.setLevel(logging.INFO)

            # Create a file handler
            """handler = logging.FileHandler('mylogfile.log')
            handler.setLevel(logging.INFO)"""

            # Create a console handler
            handler = logging.StreamHandler()
            handler.setLevel(logging.INFO)

            # Create a formatter
            formatter = logging.Formatter(
                "%(name)s - %(asctime)s - %(levelname)s - %(message)s"
            )
            handler.setFormatter(formatter)

            # Add the handler to the logger
            logger.addHandler(handler)
            result = func(logger, *args, **kwargs)
            return result

        return wrapper

    # Private methods:

    @staticmethod
    def _get_service(api_name, api_version, scopes):
        """Get a service that communicates to a Google API.

        Args:
            api_name: The name of the api to connect to.
            api_version: The api version to connect to.
            scopes: A list auth scopes to authorize for the application.
            key_file_location: The path to a valid service account JSON key file.

        Returns:
            A service that is connected to the specified API.
        """
        creds = None

        if GoogleTasks.access_token:
            creds = Credentials(token=GoogleTasks.access_token, scopes=scopes)

        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            payload = (
                f"client_id={os.getenv('GOOGLE_CREDENTIALS_CLIENT_ID')}&"
                f"client_secret={os.getenv('GOOGLE_CREDENTIALS_CLIENT_SECRET')}&"
                f"refresh_token={os.getenv('GOOGLE_CREDENTIALS_REFRESH_TOKEN')}&"
                f"grant_type={os.getenv('GOOGLE_CREDENTIALS_GRANT_TYPE')}"
            )
            headers = {"Content-Type": "application/x-www-form-urlencoded"}

            response = requests.request(
                "POST", GoogleTasks.oauth_endpoint, headers=headers, data=payload
            )

            token = response.json()["access_token"]
            creds = Credentials(token=token, scopes=scopes)

            if creds.valid:
                GoogleTasks.access_token = token

        try:
            service = build(api_name, api_version, credentials=creds)
            return service
        except HttpError as err:
            print(err)

    @staticmethod
    def _now(utc: bool = False):
        return datetime.datetime.utcnow().isoformat() + "Z" if utc else ""

    @staticmethod
    @logging
    @google_tasks_api_service_creator
    def create_task(
        service,
        logger,
        title: str,
        notes: str,
        due: datetime = None,
        task_list_id: str = TARGET_TASK_LIST_ID,
    ):
        """Creates a task in the specified task list and assigns it to the given email."""

        task = {
            "title": title,
            "notes": notes,
            "due": due.isoformat() + "Z" if due else None,
        }
        try:
            task = service.tasks().insert(tasklist=task_list_id, body=task).execute()
            return task
        except HttpError as error:
            logger.error(f"An error occurred: {error}")
            return None

    @staticmethod
    @logging
    @google_tasks_api_service_creator
    def get_task_lists(service, logger, max_results: int = None):
        try:
            results = service.tasklists().list(maxResults=max_results).execute()
            return results.get("items", [])
        except HttpError as error:
            logger.error(f"An error occurred while fetching task lists: {error}")
            return None


if __name__ == "__main__":
    GoogleTasks.create_task(
        title="Test", due=datetime.datetime(year=2024, day=30, month=1), notes=""
    )
