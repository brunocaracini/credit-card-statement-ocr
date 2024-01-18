import logging
import azure.functions as func
from controllers import CardController, StatementController
from submodules.google_drive_module.drive import GoogleDrive

app = func.FunctionApp()

@app.schedule(schedule="*/30 * * * * *", arg_name="myTimer", run_on_startup=True,
              use_monitor=False) 
def statement_scanner(myTimer: func.TimerRequest) -> None:
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
            if len(new_statements) > 0:
                for file in new_statements:
                    statement_controller.insert_with_ocr(
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
            else:
                logging.info(f"All the statements have been procesed for {card.bank} - {card.entity}")

                
        # If there is a new file, process it, else, pass
                
    logging.info('Python timer trigger function executed.')