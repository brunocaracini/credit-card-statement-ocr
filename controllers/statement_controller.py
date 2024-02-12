import locale
from classes.Item import Item
from resources.logger import Logger
from classes.ItemsSet import ItemsSet
from classes.Statement import Statement
from libraries.ocr_engine import OcrEngine
from tasks_lib import GoogleTasks
from submodules.google_calendar_module.google_calendar import GoogleCalendar
from data import DataItem, DataItemSet, DataStatement, DataCardStatement


class StatementController(DataStatement):
    def __init__(self) -> None:
        self.data_item = DataItem()
        self.data_item_set = DataItemSet()
        self.data_card_statement = DataCardStatement()
        self.logger = Logger.get_logger(name="Statement Controller")

    def get_all(self):
        self.logger.info("Fetching all statements")
        return super().get_all()

    def get_by_id_card(self, id_card: int):
        self.logger.info(f"Fetching statement by card ID {id_card}")
        return super().get_by_id_card(id_card)

    def get_latests(self, id_user: int | str):
        self.logger.info(f"Fetching latest statements for user {id_user}")
        statements = super().get_latests(id_user=id_user)
        for s in statements:
            s.items_sets = self.data_item_set.get_by_statement(id_statement=s.id)
            for item_set in s.items_sets:
                item_set.items = self.data_item.get_by_item_set(id_item_set=item_set.id)
        return statements

    def insert(self, statement: Statement, id_user: int):
        self.logger.info(f"Inserting new statement for user {id_user}")
        result = super().insert(statement=statement, id_user=id_user)
        self.logger.info("Statement inserted successfully")
        return result

    def update(self, statement: Statement):
        self.logger.info(f"Updating statement with ID {statement.id}")
        result = super().update(
            statement=statement,
        )
        self.logger.info("Statement updated successfully")
        return result

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
        self.logger.info("Inserting statement using OCR")
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
            self.logger.info("Statement inserted successfully")
        except Exception as e:
            self.logger.error(f"Error while inserting data of statement with ID {statement.id}")
            self.logger.error(f"Reason of the error: {str(e)}")
            self.logger.info("Changing the status of the statement to unprocessed")
            statement.is_processed = 0
            self.update(statement=statement)
            self.logger.info("Status of the statement has been successfully set to unprocessed")
            raise e
        return statement

    def process_ocr(self, file, entity: str, bank: str):
        self.logger.info("Processing OCR")
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
        self.logger.info("Setting statement properties")
        properties_to_set = {
            "year": year,
            "month": month,
            "filepath": filepath,
            "is_processed": 1,
            "drive_id": drive_id,
        }

        for property_name, value in properties_to_set.items():
            setattr(statement, property_name, value)
        statement.month_name = statement._translate_month_name(month=month)

        statement.id_credit_cards = (
            id_credit_cards
            if isinstance(id_credit_cards, list)
            else [id_credit_cards]
            if id_credit_cards
            else None
        )

        statement.remove_empty_item_sets()
        if all(item.type != "taxes" for item in statement.items_sets):
            item_set = ItemsSet(
                type="taxes"
            )
            item_set.append_item(item=Item(
                concept="Compensatory concept for $0 taxes statement",
                ars_amount=0,
                type="taxes"
            ))
            statement.items_sets += item_set
        statement.id = self.insert(statement=statement, id_user=id_user)
        self.logger.info("Statement properties set successfully")
        return statement

    def insert_statement_related_data(
        self, statement: Statement, csv_export: bool = False
    ):
        self.logger.info("Inserting statement related data")
        for id_credit_card in statement.id_credit_cards:
            self.data_card_statement.insert(
                id_credit_card=id_credit_card, id_statement=statement.id
            )

        statement.print_all_items()
        if len(statement.items_sets) > 0:
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
        self.logger.info("Statement related data inserted successfully")

    def create_calendar_task_current_due(
        self, statement: Statement, entity: str, bank: str
    ):
        self.logger.info("Creating calendar task for current due date")
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
            self.logger.info("Calendar task for current due date created successfully")
        except Exception as error:
            self.logger.error("Error while creating the Google Tasks task")
            self.logger.error(f"Error details: {str(error)}")

    def create_calendar_event_next_dates(
        self, statement: Statement, entity: str, bank: str
    ):
        self.logger.info("Creating calendar events for next closure and due dates")
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
            self.logger.info("Calendar events for next closure and due dates created successfully")
        except Exception as error:
            self.logger.error("Error while creating the Google Calendar event")
            self.logger.error(f"Error details: {str(error)}")
