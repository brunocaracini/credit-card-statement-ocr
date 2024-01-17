from data.data import Data
from classes.Statement import Statement
from libraries.ocr_engine import OcrEngine

class DataStatement(Data):

    TABLE_NAME = 'credit_card_statements'
    COLUMNS = [
        'id',
        'bank',
        'entity',
        'month',
        'year',
        'taxes',
        'ars_total_amount',
        'usd_total_amount',
        'filepath'
    ]

    FOREIGN_KEYS = [
        'id_user'
    ]

    def __init__(self):
        super().__init__()

    def get_all(self):
        orc = OcrEngine()
        orc.statement_orc_scanner_visa('C:/Users/bruno.tomas.caracini/OneDrive - Accenture/Desktop/Ariel/Visa ICBC Resumen 202202.pdf',entity='VISA')
        orc.statement.calc_total_amount_ars()
        return [orc.statement]

    def get_latests(self, id_user: int | str):
        self.openConn()
        query = f'''
            SELECT t1.id, t1.bank, t1.ars_total_amount, t1.usd_total_amount, t1.filepath, t1.entity, t1.year, t1.month
            FROM {self.TABLE_NAME} t1
            INNER JOIN (
                SELECT entity, MAX(year) AS max_year, MAX(month) AS max_month
                FROM {self.TABLE_NAME}
                WHERE id_user = %s
                GROUP BY entity
            ) t2 ON t1.entity = t2.entity AND t1.year = t2.max_year AND t1.month = t2.max_month;
        '''
        self.cursor.execute(query, (str(id_user),))
        return [
                Statement(
                    id=res.id,
                    bank=res.bank,
                    entity=res.entity,
                    year=res.year,
                    month=res.month,
                    ars_total_amount=res.ars_total_amount,
                    usd_total_amount=res.usd_total_amount,
                    filepath=res.filepath
                )
                for res in self.cursor.fetchall()
            ]
    
    def insert(self, statement: Statement, id_user: int):
        values = [getattr(statement, col) for col in self.COLUMNS if getattr(statement, col)] + [id_user]
        columns = [col for col in self.COLUMNS if getattr(statement, col)] + self.FOREIGN_KEYS
        return super().insert(self.TABLE_NAME, columns, values)

