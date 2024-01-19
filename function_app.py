import azure.functions as func
from resources.logger import Logger
from controllers import CardController, StatementController
from submodules.google_drive_module.drive import GoogleDrive

app = func.FunctionApp()

@app.schedule(schedule="*/30 * * * * *", arg_name="myTimer", run_on_startup=True,
              use_monitor=False) 
def statement_scanner(myTimer: func.TimerRequest) -> None:
    card_controller = CardController()
    statement_controller = StatementController()
    logger = Logger.get_logger(name="Azure Function App")
    for card in card_controller.get_all():
        if card.drive_path:
            logger.info('-' * 80)
            logger.info(f"Running for card {card.bank} - {card.entity}")

            files = GoogleDrive.get_files(calculate_paths=True, path=card.drive_path, item_type="file")
            statements = statement_controller.get_by_id_card(id_card=card.id)
            
            new_statements = [d for d in files if d['id'] not in [statement.drive_id for statement in statements]]

            if new_statements:
                for file in new_statements:
                    statement_controller.insert_with_ocr(
                        file=GoogleDrive.download_file_content_bytes_by_id(file_id=file['id']),
                        bank=card.bank,
                        entity=card.entity,
                        year=2024,
                        month=2,
                        id_user=1,
                        id_credit_cards=card.id,
                        drive_id=file['id'],
                        filepath=file['path']
                    )
                    logger.info('-' * 80)
            else:
                logger.info(f"All statements have been processed for {card.bank} - {card.entity}")
                
    logger.info('Python timer trigger function has successfuly finished.')