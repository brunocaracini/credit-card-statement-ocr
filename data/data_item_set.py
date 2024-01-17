from data.data import Data
from classes.ItemsSet import ItemsSet

class DataItemSet(Data):

    TABLE_NAME = 'credit_card_statement_items_sets'
    COLUMNS = [
        'id',
        #'card',
        'type',
        'total_ars_amount',
   ]
    FOREIGN_KEYS = [
        'id_credit_card_statement'
    ]

    def __init__(self):
        super().__init__()
    
    def get_by_statement(self, id_statement: int | str):
        return [
            ItemsSet(
                id=res.id,
                card=res.card,
                type=res.type,
                total_ars_amount=res.total_ars_amount
            )
            for res in super().select(
                table=self.TABLE_NAME,
                condition=f'id_credit_card_statement = {id_statement}'
            )
        ]

    def insert(self, items_sets: list[ItemsSet]):
        values = [getattr(items_sets, col) for col in self.COLUMNS if getattr(items_sets, col)]
        columns = [col for col in self.COLUMNS if getattr(items_sets, col)]
        return super().insert(self.TABLE_NAME, columns, values)
    
    def insert_many(self, items_sets: list[ItemsSet], id_credit_card_statement: int):
        values = [[getattr(item_set, col) for col in self.COLUMNS if getattr(item_set, col)] + [id_credit_card_statement] for item_set in items_sets if len(item_set.items) > 0]
        columns = [col for col in self.COLUMNS if getattr(items_sets[0], col)] + self.FOREIGN_KEYS
        return super().insert(self.TABLE_NAME, columns, values)