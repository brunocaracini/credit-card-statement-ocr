import pandas as pd
from data.data import Data
from classes.Item import Item

class DataItem(Data):

    TABLE_NAME = 'credit_card_statemens_items'
    COLUMNS = [
        'id',
        'date',
        'concept',
        'ars_amount',
        'usd_amount',
        'current_quota',
        'total_quotes',
        'receipt',
        'type'
    ]
    FOREIGN_KEYS = [
        'id_item_set'
    ]

    def __init__(self):
        super().__init__()
    
    def get_by_item_set(self, id_item_set: int | str):
        return [
            Item(
                id=res.id,
                date=res.date,
                concept=res.concept,
                ars_amount=res.ars_amount,
                usd_amount=res.usd_amount,
                current_quota=res.current_quota,
                total_quotes=res.total_quotes,
                receipt=res.receipt,
                type=res.type
            )
            for res in super().select(
                table = self.TABLE_NAME,
                condition=f'id_item_set = {id_item_set}'
            )
        ]

    def insert(self, statement):
        values = [getattr(statement, col) for col in self.COLUMNS if getattr(statement, col)]
        columns = [col for col in self.COLUMNS if getattr(statement, col)]
        return super().insert(self.TABLE_NAME, columns, values)

    def insert_many(self, items: list[Item], id_item_set: int):
        values = [[getattr(item, col) for col in self.COLUMNS if getattr(item, col)] + [id_item_set] for item in items]
        columns = [col for col in self.COLUMNS if getattr(items[0], col)] + self.FOREIGN_KEYS
        return super().insert(self.TABLE_NAME, columns, values)
    
    def export_to_excel(self, items: list[Item]):
        values = [[getattr(item, col) for col in self.COLUMNS if getattr(item, col)] for item in items]
        columns = [col for col in self.COLUMNS if getattr(items[0], col)]

        df = pd.DataFrame(values, columns=columns)
        writer = pd.ExcelWriter('example.xlsx')
        df.to_excel(writer, sheet_name='statement', index=False, na_rep='-')
        writer.save()