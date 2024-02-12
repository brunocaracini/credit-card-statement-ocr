"""
   IMPORTS
"""
import calendar

class Statement():
    """
       Class thar repsents a credit card statement
    """
    
    def __init__(self,id=None,bank=None,entity=None,year=None,month=12,taxes=None,ars_total_amount=None,usd_total_amount=None,id_credit_cards=None,items_sets=[],filepath=None,is_processed:bool=False, drive_id: str = None, current_closure=None, current_due_date=None, next_closure=None, next_due_date=None):
        self.id = id
        self.bank = bank
        self.entity = entity
        self.year = year
        self.month = month
        self.taxes = taxes
        self.ars_total_amount = ars_total_amount
        self.usd_total_amount = usd_total_amount
        self.id_credit_cards = id_credit_cards
        self.items_sets = items_sets
        self.filepath = filepath
        self.is_processed = is_processed
        self.drive_id = drive_id
        self.current_closure = current_closure
        self.current_due_date = current_due_date
        self.next_closure = next_closure
        self.next_due_date = next_due_date
        self.month_name = self._translate_month_name(month=month)

    #Appends
    def append_items_set(self,item_set):
        self.items_sets.append(item_set)

    #Calculations
    def calc_total_amount_ars(self):
        return round(sum([item_set.calc_total_amount_ars() for item_set in self.items_sets]), 2) if self.items_sets else 0

    def calc_total_amount_usd(self):
        return round(sum([item_set.calc_total_amount_usd() for item_set in self.items_sets]),2) if self.items_sets else 0

    def calc_total_amount_ars_per_card(self):
        return [item_set.calc_total_amount_ars() for item_set in self.items_sets if item_set.type == 'buy'] if self.items_sets else 0

    def calc_total_amount_taxes_ars(self):
        return round(sum([item_set.calc_total_amount_ars() for item_set in self.items_sets if item_set.type == 'taxes']),2) if self.items_sets else 0
            
    def calc_total_amount_buys_ars(self):
        return round(sum([item_set.calc_total_amount_ars() for item_set in self.items_sets if item_set.type == 'buy']),2) if self.items_sets else 0

    def calc_next_statement_total_quotes(self):
        return round(sum([item_set.calc_total_amount_ars() for item_set in self.get_next_statement_quotes_item_sets() if item_set.type == 'buy']),2) if self.items_sets else 0

    def calc_next_statement_total_quotes_per_card(self):
        return [item_set.calc_total_amount_ars() for item_set in self.get_next_statement_quotes_item_sets() if item_set.type == 'buy'] if self.items_sets else 0

    def set_calcs(self):
        for item_set in self.items_sets:
            item_set.total_ars_amount = item_set.calc_total_amount_ars()
        self.ars_total_amount = self.calc_total_amount_ars()
        self.usd_total_amount = self.calc_total_amount_usd()
        self.taxes = self.calc_total_amount_taxes_ars()

    def set_date_fields_from_dict(self, date_dict):
        self.current_closure = date_dict.get('current_closure', self.current_closure)
        self.current_due_date = date_dict.get('current_due_date', self.current_due_date)
        self.next_closure = date_dict.get('next_closure', self.next_closure)
        self.next_due_date = date_dict.get('next_due_date', self.next_due_date)

    #Counts
    def count_total_buys(self):
        return len([item for item_set in self.items_sets for item in item_set.items if item_set.type == 'buy'])

    def count_total_cards(self):
        return len([item_set for item_set in self.items_sets if item_set.type == 'buy'])
    
    def count_quotes_buys(self):
        return sum([item_set.count_quotes_buys() for item_set in self.items_sets])
     
    #Filterings
    def get_next_statement_quotes_item_sets(self):
        return [item_set.get_next_statement_quotes_items() for item_set in self.items_sets if item_set.type == 'buy']
    
    #Updates
    def remove_empty_item_sets(self):
        self.items_sets = [item_set for item_set in self.items_sets if len(item_set.items) > 0]
    
    def _translate_month_name(self, month):
        return {"January": "Enero", "February": "Febrero", "March": "Marzo", "April": "Abril", "May": "Mayo", "June": "Junio", "July": "Julio", "August": "Agosto", "September": "Septiembre", "October": "Octubre", "November": "Noviembre", "December": "Diciembre"}.get(calendar.month_name[month].title(), None)

    #Prints
    def print_all_items(self):
        for item_set in self.items_sets: item_set.print_all_items()
    
    def print_all_item_sets(self):
        for item_set in self.items_sets: print(item_set)

    def print_next_statement_quotes_all_item_sets(self):
        for item_set in self.get_next_statement_quotes_item_sets(): print(item_set)

    def print_next_statement_quotes_all_items(self):
        for item_set in self.get_next_statement_quotes_item_sets(): item_set.print_all_items()
