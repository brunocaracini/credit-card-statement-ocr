import datetime
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.oauth2 import service_account


class GoogleCalendar:
    scope = "https://www.googleapis.com/auth/calendar"
    key_file_location = "credit-cards-automation-7034849bd49b.json"

    TARGET_CALENDAR_ID = "trc3lp054jnp25o88n9b3pncf4@group.calendar.google.com"

    # Decorators:

    def google_api_service_creator(func):
        def wrapper(*args, **kwargs):
            # Authenticates and constructs service.
            service = GoogleCalendar._get_service(
                api_name="calendar",
                api_version="v3",
                scopes=[GoogleCalendar.scope],
                key_file_location=GoogleCalendar.key_file_location,
            )
            result = func(service, *args, **kwargs)
            return result

        return wrapper

    def logging(func):
        def wrapper(*args, **kwargs):
            # Authenticates and constructs service.
            import logging

            # Set up the logger
            logger = logging.getLogger("Google Calendar Module")
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
    def _get_service(api_name, api_version, scopes, key_file_location):
        """Get a service that communicates to a Google API.

        Args:
            api_name: The name of the api to connect to.
            api_version: The api version to connect to.
            scopes: A list auth scopes to authorize for the application.
            key_file_location: The path to a valid service account JSON key file.

        Returns:
            A service that is connected to the specified API.
        """
        credentials = service_account.Credentials.from_service_account_file(
            key_file_location
        )

        scoped_credentials = credentials.with_scopes(scopes)

        # Build the service object.
        service = build(api_name, api_version, credentials=scoped_credentials)

        return service

    @staticmethod
    def _now(utc: bool = False):
        return datetime.datetime.utcnow().isoformat() + "Z" if utc else ""

    @staticmethod
    @logging
    @google_api_service_creator
    def get_calendar_ids(service, logger):
        try:
            calendar_list = service.calendarList().list().execute()
            calendar_ids = [calendar["id"] for calendar in calendar_list["items"]]
            print(calendar_ids)
            return calendar_ids
        except HttpError as error:
            logger.error(f"An error occurred: {error}")
            return []

    @staticmethod
    @logging
    @google_api_service_creator
    def get_calendar_by_id(service, logger, calendar_id: str):
        try:
            calendar = service.calendars().get(calendarId=calendar_id).execute()
            return calendar
        except HttpError as error:
            logger.error(f"An error occurred: {error}")
            return []

    @staticmethod
    @logging
    @google_api_service_creator
    def get_events_for_calendar(
        service, logger, calendar_id: str, future_events_only: bool = False
    ):
        """Retrieves events from the specified calendar.

        Args:
            service: Authenticated service instance of the Google API Client.
            calendar_id: The ID of the calendar to retrieve events from.

        Returns:
            A list of event dictionaries, or None if an error occurs.
        """

        try:
            now = GoogleCalendar._now()
            events_result = (
                service.events()
                .list(
                    calendarId=calendar_id,
                    timeMin=now if future_events_only else None,
                    maxResults=10,  # Adjust maxResults as needed
                    singleEvents=True,
                    orderBy="startTime",
                )
                .execute()
            )
            events = events_result.get("items", [])
            return events
        except HttpError as error:
            logger.error(f"An error occurred: {error}")
            return None

    @staticmethod
    @logging
    @google_api_service_creator
    def create_event(
        service,
        logger,
        calendar_id,
        summary: str,
        description: str,
        all_day=False,
        start: datetime = None,
        end: datetime = None,
    ):
        """Creates an event on the specified calendar.

        Args:
            service: Authenticated service instance of the Google API Client.
            calendar_id: The ID of the calendar to create the event on.
            summary: The summary of the event.
            description: The description of the event.
            all_day: Whether the event is an all-day event.
            start: The start time of the event (datetime object) for non-all-day events.
            end: The end time of the event (datetime object) for non-all-day events.

        Returns:
            The created event object, or None if an error occurs.
        """

        event = {
            "summary": summary,
            "description": description,
            "start": {
                "date": start.date().isoformat()
                if all_day
                else start.isoformat()  # Adjust formatting for time-only events if needed
            },
            "end": {
                "date": end.date().isoformat()
                if all_day
                else end.isoformat()  # Adjust formatting for time-only events if needed
            },
        }

        try:
            event = (
                service.events().insert(calendarId=calendar_id, body=event).execute()
            )
            return event
        except HttpError as error:
            logger.error(f"An error occurred: {error}")
            return None


if __name__ == "__main__":
    files = GoogleCalendar.create_event(
        calendar_id=GoogleCalendar.TARGET_CALENDAR_ID,
        summary="Test Vencimiento",
        description="Test",
        all_day=True,
        start=datetime.datetime.now(),
        end=datetime.datetime.now()
    )
