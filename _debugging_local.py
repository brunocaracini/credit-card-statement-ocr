import re
import os
from dotenv import load_dotenv
import azure.functions as func
from resources.logger import Logger
from controllers import CardController, StatementController
from submodules.google_drive_module.drive import GoogleDrive

ENVIRONMENT_NAME = os.getenv("ENVIRONMENT_NAME")
if not ENVIRONMENT_NAME or ENVIRONMENT_NAME.lower() == "local":
    load_dotenv()
    print("Running in LOCAL environment")

def statement_scanner() -> None:
    card_controller = CardController()
    statement_controller = StatementController()
    logger = Logger.get_logger(name="Azure Function App")

    [
        process_card_statement(card, logger, statement_controller)
        for card in card_controller.get_all()
        if card.drive_path
    ]

    logger.info("Python timer trigger function has successfully finished.")

def process_card_statement(card, logger, statement_controller):
    logger.info("-" * 80)
    logger.info(f"Running for card {card.bank} - {card.entity}")

    # Get the files
    files = GoogleDrive.get_files(
        calculate_paths=True, path=card.drive_path, item_type="file"
    )
    statements = statement_controller.get_by_id_card(id_card=card.id)

    # Filter the new statements
    new_statements = [
        file
        for file in files
        if file["id"] not in {statement.drive_id for statement in statements}
    ]

    # Process new Statements
    for file in new_statements:
        year, month = map(
            int, re.search(r"(\d{4})-(\d{2})\.pdf", file["name"]).groups()
        )
        logger.info(f'Processing statement for {str(year)}-{str(month)} for {card.entity} - {card.bank}')
        statement = statement_controller.insert_with_ocr(
            file=GoogleDrive.download_file_content_bytes_by_id(file_id=file["id"]),
            bank=card.bank,
            entity=card.entity,
            year=year,
            month=month,
            id_user=1,
            id_credit_cards=card.id,
            drive_id=file["id"],
            filepath=file["path"],
        )

        statement_controller.create_calendar_task_current_due(
            statement=statement, bank=card.bank, entity=card.entity
        )

        statement_controller.create_calendar_event_next_dates(
            statement=statement, bank=card.bank, entity=card.entity
        )

        logger.info(f'Statement for {str(year)}-{str(month)} for {card.entity} - {card.bank} has been successfuly processed')

    logger.info("-" * 80) if new_statements else logger.info(
        f"All statements have been processed for {card.bank} - {card.entity}"
    )

if __name__ == "__main__":
    statement_scanner()