from functools import wraps

from data.data import Data
from classes.Statement import Statement
from libraries.ocr_engine import OcrEngine


def instantiate_statements(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)

        if isinstance(result, tuple):
            return Statement(**dict(zip(DataStatement.COLUMNS, result)))
        elif isinstance(result, list):
            return [Statement(**dict(zip(DataStatement.COLUMNS, values))) for values in result]
        else:
            raise ValueError(
                "Unsupported result type. Function should return a named tuple or a list of named tuples."
            )
    return wrapper

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
        'filepath',
        'is_processed',
        'drive_id'
    ]

    FOREIGN_KEYS = [
        'id_user',
    ]

    def __init__(self):
        super().__init__()

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
    
    @instantiate_statements
    def get_by_id_card(self, id_card: int):
        from data import DataCardStatement
        self.openConn()
        query = f'''
            SELECT {', '.join(['cs.' + column for column in self.COLUMNS])} 
            FROM {self.TABLE_NAME} cs
            JOIN {DataCardStatement.TABLE_NAME} ccs 
                on cs.id = ccs.id_statement
            WHERE ccs.id_credit_card = %s
        '''
        self.cursor.execute(query, (str(id_card),))
        return self.cursor.fetchall()
    
    def insert(self, statement: Statement, id_user: int):
        values = [getattr(statement, col) for col in self.COLUMNS if getattr(statement, col)] + [id_user]
        columns = [col for col in self.COLUMNS if getattr(statement, col)] + self.FOREIGN_KEYS
        return super().insert(self.TABLE_NAME, columns, values)
    
    def update(self, statement: Statement):
        values = [getattr(statement, col) for col in self.COLUMNS if getattr(statement, col)]
        columns = [col for col in self.COLUMNS if getattr(statement, col)]
        return super().update(self.TABLE_NAME, set_values=dict(zip(columns, values)), condition=f"id={statement.id}")

