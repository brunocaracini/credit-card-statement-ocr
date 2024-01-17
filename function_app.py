import logging
import azure.functions as func
from controllers import CardController, StatementController


app = func.FunctionApp()

@app.schedule(schedule="0 * * * *", arg_name="myTimer", run_on_startup=True,
              use_monitor=False) 
def statement_scanner(myTimer: func.TimerRequest) -> None:
    if myTimer.past_due:
        card_controller = CardController()
        statement_controller = StatementController()
        for card in card_controller.get_all():
            # Get google drive files on card's path

            # Check if there is any new file

            # If there is a new file, process it, else, pass
            pass
        logging.info('The timer is past due!')

    logging.info('Python timer trigger function executed.')