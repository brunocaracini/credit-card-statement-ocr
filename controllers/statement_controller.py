import locale
from classes.Statement import Statement
from calendar_lib import GoogleCalendar
from tasks_lib import GoogleTasks
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

    def update(self, statement: Statement):
        return super().update(
            statement=statement,
        )

    def insert_with_ocr(
        self,
        file: dict,
        filepath: str,
        entity: str,
        bank: str,
        year: int,
        month: int,
        id_user: int,
        drive_id: str,
        id_credit_cards: int | list[int] = None,
        csv_export: bool = False,
    ):
        statement = self.process_ocr(file=file, entity=entity, bank=bank)
        statement = self.set_statement_properties(
            statement=statement,
            filepath=filepath,
            year=year,
            month=month,
            id_user=id_user,
            drive_id=drive_id,
            id_credit_cards=id_credit_cards,
        )
        try:
            self.insert_statement_related_data(
                statement=statement, csv_export=csv_export
            )
        except Exception as e:
            print(f"Error while inserting data of statement with ID {statement.id}")
            statement.is_processed = 0
            self.update(statement=statement)
        return statement

    def process_ocr(self, file, entity: str, bank: str):
        ocr = OcrEngine()
        if (
            entity.lower() == "visa"
            or entity.lower() == "mastercard"
            or entity.lower() == "amex"
        ):
            ocr.statement_orc_scanner(
                pdf_content=file, bank=bank, entity=entity.upper()
            )
        ocr.statement.set_calcs()
        return ocr.statement

    def set_statement_properties(
        self,
        statement: Statement,
        filepath: str,
        year: int,
        month: int,
        id_user: int,
        drive_id: str,
        id_credit_cards: int | list[int] = None,
    ):
        properties_to_set = {
            "year": year,
            "month": month,
            "filepath": filepath,
            "is_processed": 1,
            "drive_id": drive_id,
        }

        for property_name, value in properties_to_set.items():
            setattr(statement, property_name, value)

        statement.id_credit_cards = (
            id_credit_cards
            if isinstance(id_credit_cards, list)
            else [id_credit_cards]
            if id_credit_cards
            else None
        )

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

        statement.print_all_items()
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

    def get_by_id_card(self, id_card: int):
        return super().get_by_id_card(id_card)

    def create_calendar_task_current_due(
        self, statement: Statement, entity: str, bank: str
    ):
        locale.setlocale(locale.LC_NUMERIC, 'es_AR')
        formatted_ars = locale.format_string("%.2f", statement.ars_total_amount, grouping=True)
        formatted_usd = locale.format_string("%.2f", statement.usd_total_amount, grouping=True)
        summary = f"Pagar {entity} {bank} - Total de ${str(formatted_ars)} ARS + ${str(formatted_usd)} USD"
        description = f"""El resumen tarjeta {entity} {bank} del mes de {statement.month_name} con cierre el {statement.current_closure.strftime('%d/%m/%Y')} vence este día.\n\nEl total a pagar es de:
            - ${str(formatted_ars)} ARS
            - ${str(formatted_usd)} USD
        """
        try:
            GoogleTasks.create_task(
                title=summary,
                notes=description,
                due=statement.current_due_date
            )
        except Exception as error:
            raise error
            print("Error while creating the calendar task")

    def create_calendar_event_next_dates(
        self, statement: Statement, entity: str, bank: str
    ):
        summary_closure = f"Cierre {entity} {bank}"
        description_closure = f"El resumen tarjeta {entity} {bank} del mes de {statement.month_name} cierra el {statement.next_closure.strftime('%d/%m/%Y')}"

        summary_due = f"Vencimiento {entity} {bank}"
        description_due = f"El resumen tarjeta {entity} {bank} del mes de {statement.month_name} vence el {statement.next_due_date.strftime('%d/%m/%Y')}"
        try:
           GoogleCalendar.create_event(
                all_day=True,
                start=statement.next_closure,
                end=statement.next_closure,
                summary=summary_closure,
                description=description_closure
            )
           GoogleCalendar.create_event(
                all_day=True,
                start=statement.next_due_date,
                end=statement.next_due_date,
                summary=summary_due,
                description=description_due
            )
        except:
            print("Error while creating the calendar event")
