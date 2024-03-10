"""
   IMPORTS
"""

import io
import re
import pdfplumber
from datetime import datetime
from unidecode import unidecode

from classes.Item import Item
from classes.Card import Card
from classes.Statement import Statement
from classes.ItemsSet import ItemsSet


class OcrEngine:
    """
    Handles the logic of the statements.
    """

    # Regexs
    DATE_REGEX = [
        ".*?^([0-9][0-9](/|-)[0-9][0-9](/|-)[0-9][0-9])$.*",
        r"^(([0-2][0-9])|([3][0-1]))/((0[1-9])|(1[0-2]))/\d{4}$",
        ".*?^([0-9][0-9](/|-|\.)[0-9][0-9](/|-|\.)[0-9][0-9])$.*",
        "^(([0-9])|([0][0-9])|([1-2][0-9])|([3][0-1]))\-(Ene|Feb|Mar|Apr|May|Jun|Jul|Ago|Sep|Oct|Nov|Dic)\-\d{2}$",
        "^(([0-9])|([0][0-9])|([1-2][0-9])|([3][0-1]))\-(Enero|Febrero|Marzo|Abril|Mayo|Junio|Julio|Agosto|Septiem.|Octubre|Noviem.|Diciem.)\-\d{2}$",
    ]
    CARD_TOTAL = [
        "TOTAL CONSUMOS DE",
        "TOTAL TARJETA",
        "TOTAL CONSUMOS",
        "TOTAL TITULAR",
        "TOTAL ADICIONAL",
        "Total de cuotas a vencer",
    ]
    QUOTE_REGEX = "[0-50]/[0-50]"

    # Prefixs
    QUOTE_PREFIX = ["CUOTA", "C."]

    # Currencies
    CURRENCIES = [
        " USD ",
        " EUR ",
        " GBP ",
    ]

    # Taxes
    IMPUESTOS = ["IMPUESTO"]
    IVA = ["IVA", "I.V.A"]
    INTERESES_FINANCIACION = ["INTERESES"]

    # Invalid Line values
    INVALID_LINES = ["SU PAGO EN PESOS", "SU PAGO", "TNA", "SALDO ANTERIOR"]

    # Statement dates
    STATEMENT_DATES = {
        "CURRENT_DUE_DATE": [
            "VENCIMIENTOACTUAL",
            "VTOACTUAL",
            "VTO.ACTUAL",
            "VENCIMIENTOACTUAL:",
            "VTO.ACTUAL",
        ],
        "NEXT_DUE_DATE": [
            "PROXIMOVENCIMIENTO",
            "PROXIMOVTO",
            "PROXIMOVTO.",
            "PROXIMOVTO.:",
            "PROXIMOVENCIMIENTO:",
            "PROXIMOVTO:",
            "PROX.VTO",
            "PROX.VTO.",
            "PROX.VTO.:",
        ],
        "CURRENT_CLOSURE": ["CIERREACTUAL", "CIERREACTUAL:", "CUENTAAL", "CUENTAAL:"],
        "NEXT_CLOSURE": [
            "PROXIMOCIERRE",
            "PROXIMOCIERRE:",
            "PROX.CIERRE",
            "PROX.CIERRE.",
            "PROX.CIERRE:",
        ],
    }

    # Values
    IVA_VALUE = 0.21

    def __init__(self):
        self.statement = Statement(
            items_sets=[],
            is_processed=0,
            current_closure=None,
            current_due_date=None,
            next_closure=None,
            next_due_date=None,
        )
        self.list_splitted_item = []
        self.statement_dates = []

    def statement_orc_scanner(
        self, pdf_path: str = None, pdf_content=None, bank="ICBC", entity="VISA"
    ):
        self.statement.bank = bank
        self.statement.entity = entity
        items_set = ItemsSet(items=[])
        taxes_got = False
        previous_date = ""

        # Get pdf text
        text = (
            self.extract_text_from_statement_pdf(pdf_path)
            if not pdf_content
            else self.extract_text_from_statement_pdf_in_memory(pdf_content=pdf_content)
        )

        for line in text.split("\n"):
            self.list_splitted_item = list(
                filter(lambda x: len(x) > 0, line.split(" "))
            )

            # Dates extraction
            self.statement_dates += self.extract_statement_dates(
                entity=entity, bank=bank
            )
            if bank.upper() == "SANTANDER":
                self.statement_dates += self.extract_dates_visa_santander()
            elif bank.upper() == "COINAG":
                self.statement_dates += self.extract_dates_visa_coinag()

            # For MASTERCARD only: looking for taxes at the begining
            if entity == "MASTERCARD" and not taxes_got:
                taxes_items_set = ItemsSet(items=[], type="taxes")
                if self.is_tax() and not self.filter_tax_by_amount():
                    print(self.list_splitted_item)
                    ars_amount = self.extract_ars_amount()
                    concept = self.extract_concept()
                    item = Item(concept=concept, ars_amount=ars_amount, type="taxes")
                    taxes_items_set.append_item(item)

                if len(taxes_items_set.items) > 0:
                    self.statement.append_items_set(taxes_items_set)

            if any(x in line.upper() for x in getattr(self, "CARD_TOTAL")):
                # Set Card Value for ItemSet
                items_set.card = (
                    Card(
                        entity=entity,
                        bank=bank,
                        last_four_numbers=self.extract_last_four_numbers(),
                    )
                    if entity == "VISA"
                    else (
                        Card(entity=entity, bank=bank)
                        if entity == "MASTERCARD"
                        else None
                    )
                )
                self.statement.append_items_set(items_set)
                items_set = ItemsSet(items=[])

            date = self.multi_regex_match(
                attr="DATE_REGEX", previous_date=previous_date
            )

            if (
                date != False
                and self.is_valid_line(line)
                and not self.is_multi_date_line()
            ):
                taxes_got = False
                previous_date = date
                quote = self.extract_quote()
                receipt = self.exctract_receipt(entity=entity)
                ars_amount = self.extract_ars_amount()
                usd_amount = 0
                concept = self.extract_concept()

                if self.contains_any_currency(concept=concept):
                    usd_amount = ars_amount
                    ars_amount = 0

                if not self.is_tax(concept):
                    item = Item(
                        date=date,
                        concept=concept,
                        ars_amount=ars_amount,
                        usd_amount=usd_amount,
                        receipt=receipt,
                        type="buy" if ars_amount >= 0 else "bonus",
                    )
                    item.set_quotes_values_from_string(quote)
                else:
                    ars_amount = (
                        ars_amount
                        if concept not in getattr(self, "IVA")
                        and entity.upper() == "VISA"
                        else round(ars_amount * getattr(self, "IVA_VALUE"), 2)
                    )
                    item = Item(
                        date=date, concept=concept, ars_amount=ars_amount, type="taxes"
                    )

                items_set.append_item(item)

        self.statement.set_date_fields_from_dict(
            date_dict=self.extract_variables_as_dict()
        )

        # Append Taxes Items Set
        if entity in ["VISA", "AMEX"]:
            items_set.type = "taxes"
            self.statement.append_items_set(items_set)

    def extract_date(self):
        try:
            dates = [
                list(filter(re.compile(regex).match, self.list_splitted_item))[0]
                for regex in getattr(self, "DATE_REGEX")
                if list(filter(re.compile(regex).match, self.list_splitted_item)) != []
            ]
            self.list_splitted_item.remove(dates[0])
            return dates[0]
        except:
            return None

    def filter_tax_by_amount(self):
        for word in self.list_splitted_item:
            try:
                if "," in word or "." in word:
                    float(word.replace(" ", "").replace(".", "").replace(",", "."))
                    return False
            except:
                continue
        return True

    def extract_last_four_numbers(self):
        return int([x for x in self.list_splitted_item if self.is_number(x)][0])

    def extract_quote(self):
        r = re.compile(getattr(self, "QUOTE_REGEX"))
        quote = list(filter(r.search, self.list_splitted_item))

        quote_prefixs = [
            x
            for word in getattr(self, "QUOTE_PREFIX")
            for x in self.list_splitted_item
            if word in x.upper() and not re.search(getattr(self, "QUOTE_REGEX"), x)
        ]
        [self.list_splitted_item.remove(x) for x in quote_prefixs]

        if len(quote) > 0:
            self.list_splitted_item.remove(quote[0])
            prefixes = [
                prefix for prefix in getattr(self, "QUOTE_PREFIX") if prefix in quote[0]
            ]
            for prefix in prefixes:
                quote[0] = quote[0].upper().replace(prefix, "")
            return quote[0]
        else:
            return "01/01"

    def exctract_receipt(self, entity):
        receipts = [x for x in self.list_splitted_item if x.endswith("*")]
        if len(receipts) < 1 or not receipts[0].replace("*", "").isdigit():
            receipts = [x for x in self.list_splitted_item if x.isdigit()]

        if "*" in self.list_splitted_item:
            self.list_splitted_item.remove("*")

        if len(receipts) > 0:
            (
                self.list_splitted_item.remove(receipts[0])
                if receipts[0] in self.list_splitted_item
                else None
            )
            return receipts[0].replace("*", "")

    def extract_ars_amount(self):
        first_element_zero = False
        negative = False  # Initialize negative outside the loop
        for i, element in enumerate(self.list_splitted_item[::-1]):  # Added enumerate to keep track of index
            number = element.strip(" ").replace(".", "").replace(",", ".")
            if self.is_number(number):
                if number[-1] == "-":
                    number = number[:-1]
                    negative = True
                elif number[0] == "-":
                    number = number[1:]
                    negative = True
                if float(number) == 0:
                    first_element_zero = True
                    continue
                # Check if the next element is a "-"
                if i < len(self.list_splitted_item) and self.list_splitted_item[i+1].strip() == "-":
                    negative = True
                self.list_splitted_item.remove(element)
                return (
                    round(float(number) * -1, 2) if negative else round(float(number), 2)
                )
        if first_element_zero:
            self.list_splitted_item.remove(element)
            return 0

    def extract_concept(self):
        return " ".join(self.list_splitted_item) + " "

    def is_tax(self, concept=None):
        if concept is None:
            concept = (
                self.list_splitted_item[0]
                if len(self.list_splitted_item) > 1
                else False
            )
        if not concept:
            return False

        taxes = (
            getattr(self, "IMPUESTOS")
            + getattr(self, "IVA")
            + getattr(self, "INTERESES_FINANCIACION")
        )
        for tax in taxes:
            if any(
                tax in word.upper()
                for word in list(
                    filter(lambda x: len(x) > 0, concept.upper().split(" "))
                )
            ):
                return True
        return False

    def is_valid_line(self, line):
        return not any(
            invalid_line in line for invalid_line in getattr(self, "INVALID_LINES")
        )

    def is_multi_date_line(self):
        return (
            True
            if len(
                [
                    el
                    for regex in getattr(self, "DATE_REGEX")
                    for el in self.list_splitted_item
                    if re.match(regex, el)
                ]
            )
            > 1
            else False
        )

    def extract_statement_dates(self, entity: str, bank: str):
        result = []
        for date_list, keywords in self.STATEMENT_DATES.items():
            for i in range(len(self.list_splitted_item) - 1):
                current_str = self.list_splitted_item[i].strip()
                next_str = self.list_splitted_item[i + 1].strip()

                # Check if the current string ends with ":" and the next string is not empty
                if (
                    entity.upper() in ["VISA", "AMEX"]
                    and bank.upper() == "SANTANDER"
                    and current_str.endswith(":")
                    and next_str
                ):
                    # Split the current string at the ":" and add both parts to the list
                    current_str, rest_of_current_str = current_str.rsplit(":", 1)
                    self.list_splitted_item[i] = current_str
                    self.list_splitted_item.insert(i + 1, rest_of_current_str)

                combined_str = unidecode(current_str + next_str).strip().upper()

                if any(keyword in combined_str for keyword in keywords):
                    if entity.upper() == "MASTERCARD":
                        date = self.list_splitted_item[i + 2]
                    elif entity.upper() == "VISA" and bank.upper() == "MACRO BMA":
                        date = re.sub(r"(\d+)(\D+)(\d+)", r"\1-\2-\3", next_str)
                        if not bool(re.match(r"^\d+\D+\d+$", date)):
                            continue
                    else:
                        date = "-".join(self.list_splitted_item[i + 2 : i + 5])
                    result.append((date_list, date))
        return result if result else []

    def extract_variables_as_dict(self):
        variables_dict = {
            "current_closure": None,
            "current_due_date": None,
            "next_closure": None,
            "next_due_date": None,
        }
        for key, value in self.statement_dates:
            if key == "CURRENT_CLOSURE" and not variables_dict["current_closure"]:
                variables_dict["current_closure"] = OcrEngine.convert_to_datetime(value)
            elif key == "NEXT_CLOSURE" and not variables_dict["next_closure"]:
                variables_dict["next_closure"] = OcrEngine.convert_to_datetime(value)
            elif key == "CURRENT_DUE_DATE" and not variables_dict["current_due_date"]:
                variables_dict["current_due_date"] = OcrEngine.convert_to_datetime(
                    value
                )
            elif key == "NEXT_DUE_DATE" and not variables_dict["next_due_date"]:
                variables_dict["next_due_date"] = OcrEngine.convert_to_datetime(value)

        return variables_dict

    def multi_regex_match(self, attr, previous_date):
        # Creating value to be asserted
        value = self.list_splitted_item[0] if len(self.list_splitted_item) > 1 else ""
        if not any(re.match(regex, value) for regex in getattr(self, attr)):
            # If it is not matching by default, we create a parsed value to assert
            day_number = self.list_splitted_item[0]
            value = (
                "-".join(self.list_splitted_item[0:3])
                if len(self.list_splitted_item) > 2
                else ""
            )
            if any(re.match(regex, value) for regex in getattr(self, attr)):
                # Removing the date from string
                for ele in self.list_splitted_item[0:3]:
                    self.list_splitted_item.remove(ele)
                return value
            elif day_number == self.extract_day_number_from_formated_date(
                formated_date=previous_date
            ):
                self.list_splitted_item.remove(self.list_splitted_item[0])
                return previous_date
            elif (
                len(day_number) >= 2
                and self.is_number(value=day_number)
                and int(day_number.strip(",").strip(".")) <= 31
            ):
                self.list_splitted_item.remove(self.list_splitted_item[0])
                return self.replace_day_number_in_formated_date(
                    formated_date=previous_date, day_number=day_number
                )
            else:
                return False
        else:
            return self.extract_date()

    def contains_any_currency(self, concept: str):
        """
        Check if any currency in the list currencies is present in the given concept.

        Args:
        - concept (str): The string to search within.

        Returns:
        - bool: True if any currency is found, False otherwise.
        """
        return any(currency in concept for currency in self.CURRENCIES)

    def extract_dates_visa_santander(self):

        cadena = " ".join(self.list_splitted_item)
        pattern = (
            r"CIERRE (\d{1,2}\s\w{3})\s(\d{2}).*?VENCIMIENTO (\d{1,2}\s\w{3})\s(\d{2})"
        )

        matches = re.search(pattern, cadena)

        if matches:
            current_closure_date = f"{matches.group(1)}-{matches.group(2)}".replace(
                " ", "-"
            )
            current_due_date = f"{matches.group(3)}-{matches.group(4)}".replace(
                " ", "-"
            )
            return [
                ("CURRENT_CLOSURE", current_closure_date),
                ("CURRENT_DUE_DATE", current_due_date),
            ]
        return []

    def extract_dates_visa_coinag(self):

        text = " ".join(self.list_splitted_item)
        pattern = r"2000\s+ROSARIO\s+(\d+\s+\w+\s+\d+)"

        match = re.search(pattern, text)

        if match:
            current_due_date = match.group(1).replace(" ", "-")
            return [("CURRENT_DUE_DATE", current_due_date)]
        else:
            return []

    @staticmethod
    def is_number(value):
        value = value.strip(" ").replace(",", ".")
        if value == "":
            return False
        elif value[-1] == "-":
            value = value[:-1]
        elif value[0] == "-":
            value = value[1:]
        return (
            True
            if type(value) in [int, float]
            else str(value).replace(".", "", 1).isdigit()
        )

    @staticmethod
    def extract_text_from_statement_pdf(pdf_path: str):
        with pdfplumber.open(pdf_path) as pdf:
            return "".join([page.extract_text() for page in pdf.pages])

    @staticmethod
    def extract_text_from_statement_pdf_in_memory(pdf_content):
        with pdfplumber.open(io.BytesIO(pdf_content)) as pdf:
            return "".join([page.extract_text() for page in pdf.pages])

    @staticmethod
    def extract_day_number_from_formated_date(formated_date):
        splitted_date = formated_date.split("-")
        return splitted_date[2] if len(splitted_date) > 2 else ""

    @staticmethod
    def replace_day_number_in_formated_date(formated_date, day_number):
        splitted_date = formated_date.split("-")
        if len(splitted_date) >= 2:
            splitted_date[2] = day_number
            return "-".join(splitted_date[0:3])
        else:
            return False

    @staticmethod
    def convert_to_datetime(date_str):
        month_mapping = {
            "Ene": 1,
            "Feb": 2,
            "Mar": 3,
            "Abr": 4,
            "May": 5,
            "Jun": 6,
            "Jul": 7,
            "Ago": 8,
            "Sep": 9,
            "Set": 9,
            "Oct": 10,
            "Nov": 11,
            "Dic": 12,
            "Enero": 1,
            "Febrero": 2,
            "Marzo": 3,
            "Abril": 4,
            "Mayo": 5,
            "Junio": 6,
            "Julio": 7,
            "Agosto": 8,
            "Septiembre": 9,
            "Setiembre": 9,
            "Octubre": 10,
            "Noviembre": 11,
            "Diciembre": 12,
        }
        day, month_str, year = date_str.split("-")
        month = month_mapping.get(month_str.title())

        # Convert two-digit year to four-digit year
        if len(year) == 2:
            if int(year) < 30:
                year = f"20{year}"
            else:
                year = f"19{year}"
        try:
            result_date = datetime(int(year), month, int(day))
            return result_date
        except ValueError:
            return None
