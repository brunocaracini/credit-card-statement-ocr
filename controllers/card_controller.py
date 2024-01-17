from classes.Statement import Statement
from data import DataItem, DataItemSet, DataCard, DataCardStatement


class CardController(DataCard):
    def __init__(self) -> None:
        self.data_item = DataItem()
        self.data_item_set = DataItemSet()
        self.data_card_statement = DataCardStatement()

    def get_all(self):
        return super().get_all()
    
