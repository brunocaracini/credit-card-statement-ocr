from data.data import Data

class DataCardStatement(Data):

    TABLE_NAME = 'credit_cards_statements'
    COLUMNS = [
        'id',
   ]
    FOREIGN_KEYS = [
        'id_credit_card',
        'id_statement'
    ]

    def __init__(self):
        super().__init__()
    
    def insert(self, id_credit_card: int, id_statement: int):
        values = [id_credit_card, id_statement]
        columns = [col for col in self.FOREIGN_KEYS]
        return super().insert(self.TABLE_NAME, columns, values)