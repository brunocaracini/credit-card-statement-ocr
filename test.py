import logging
import azure.functions as func
from controllers import CardController, StatementController
from submodules.google_drive_module.drive import GoogleDrive


def statement_scanner() -> None:
    card_controller = CardController()
    statement_controller = StatementController()
    for card in card_controller.get_all():
        if card.drive_path:
            logging.info('--'*80)
            logging.info(f"Running for card {card.bank} - {card.entity}")
            files = GoogleDrive.get_files(
                calculate_paths=True, path=card.drive_path, item_type="file"
            )
            statements = statement_controller.get_by_id_card(id_card=card.id)
            new_statements = [d for d in files if d['id'] not in [statement.drive_id for statement in statements]]
            for file in new_statements:
                print("Resumen ", file['name'])
                sc = StatementController()
                sc.insert_with_ocr(
                    file = GoogleDrive.download_file_content_bytes_by_id(
                        file_id=file['id']
                    ),
                    bank=card.bank,
                    entity=card.entity,
                    year=2024,
                    month=2,
                    id_user=1,
                    id_credit_cards=card.id,
                    drive_id=file['id'],
                    filepath=file['path']
                )
                logging.info('--'*80)

                
        # If there is a new file, process it, else, pass
                
    logging.info('Python timer trigger function executed.')

statement_scanner()