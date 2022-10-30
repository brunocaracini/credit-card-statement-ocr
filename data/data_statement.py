from data.data import Data
from classes.Statement import Statement
from controllers.orc_controller import OrcController

class DataStatement(Data):

    def __init__(self):
        super().__init__()

    def get_all(self):
        orc = OrcController()
        orc.statement_orc_scanner_visa('C:/Users/bruno.tomas.caracini/OneDrive - Accenture/Desktop/Ariel/Visa ICBC Resumen 202202.pdf',entity='VISA')
        orc.statement.calc_total_amount_ars()
        return [orc.statement]

    def get_last(self):
        orc = OrcController()
        orc.statement_orc_scanner_visa('C:/Users/bruno.tomas.caracini/OneDrive - Accenture/Desktop/Ariel/Visa ICBC Resumen 202202.pdf',entity='VISA')
        orc.statement.calc_total_amount_ars()
        return orc.statement

