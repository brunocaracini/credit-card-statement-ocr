from classes.Statement import Statement
from libraries.ocr_engine import OcrEngine
from data import DataItem, DataItemSet, DataStatement, DataCardStatement


class StatementController(DataStatement):
    def __init__(self) -> None:
        self.data_item = DataItem()
        self.data_item_set = DataItemSet()
        self.data_card_statement = DataCardStatement()

    def get_all(self):
        return super().get_all()

    def get_latests(self, id_user: int | str):
        statements = super().get_latests(id_user=id_user)
        for s in statements:
            s.items_sets = self.data_item_set.get_by_statement(id_statement=s.id)
            for item_set in s.items_sets:
                item_set.items = self.data_item.get_by_item_set(id_item_set=item_set.id)
        return statements

    def insert(self, statement: Statement, id_user: int):
        return super().insert(statement=statement, id_user=id_user)

    def insert_with_ocr(
        self,
        filepath: str,
        entity: str,
        bank: str,
        year: int,
        month: int,
        id_user: int,
        id_credit_cards: int | list[int] = None,
        csv_export: bool = False,
    ):
        statement = self.process_ocr(filepath, entity, bank)
        statement = self.set_statement_properties(
            statement=statement,
            filepath=filepath,
            year=year,
            month=month,
            id_user=id_user,
            id_credit_cards=id_credit_cards,
        )
        self.insert_statement_related_data(
            statement=statement, csv_export=csv_export
        )
        return statement

    def process_ocr(self, filepath: str, entity: str, bank: str):
        statement = self.ocr_scann(filepath=filepath, entity=entity, bank=bank)
        statement.print_all_item_sets()
        return statement

    def set_statement_properties(
        self,
        statement: Statement,
        filepath: str,
        year: int,
        month: int,
        id_user: int,
        id_credit_cards: int | list[int] = None,
    ):
        statement.year = year
        statement.month = month
        statement.filepath = filepath
        if id_credit_cards:
            id_credit_cards = (
                id_credit_cards
                if isinstance(id_credit_cards, list)
                else [id_credit_cards]
            )
            statement.id_credit_cards = id_credit_cards
        statement.remove_empty_item_sets()
        statement.id = self.insert(statement=statement, id_user=id_user)
        return statement

    def insert_statement_related_data(
        self, statement: Statement, csv_export: bool = False
    ):
        for id_credit_card in statement.id_credit_cards:
            self.data_card_statement.insert(
                id_credit_card=id_credit_card, id_statement=statement.id
            )

        item_set_ids = self.data_item_set.insert_many(
            items_sets=statement.items_sets, id_credit_card_statement=statement.id
        )
        for i, itemset in enumerate(statement.items_sets):
            itemset.__setattr__("id", item_set_ids[i])

        for item_set in statement.items_sets:
            self.data_item.insert_many(items=item_set.items, id_item_set=item_set.id)

        if csv_export:
            self.data_item.export_to_excel(
                items=[
                    item for item_set in statement.items_sets for item in item_set.items
                ]
            )

    def ocr_scann(self, filepath: str, entity: str, bank: str):
        ocr = OcrEngine()
        if entity.lower() == "visa" or entity.lower() == "mastercard":
            ocr.statement_orc_scanner_visa(
                pdf_path=filepath, bank=bank, entity=entity.upper()
            )
        elif entity.lower() == "amex":
            pass
        ocr.statement.set_calcs()
        return ocr.statement
