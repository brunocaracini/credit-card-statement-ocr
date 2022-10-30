"""
   IMPORTS
"""
from types import TracebackType

class Statement():
    """
       Class thar repsents a credit card statement
    """
    
    def __init__(self,id=None,year=None,month=None,taxes=None,ars_total_amount=None,usd_total_amount=None,id_credit_cards=None,items_sets=[]):
        self.id = id
        self.year = year
        self.month = month
        self.taxes = taxes
        self.ars_total_amount = ars_total_amount
        self.usd_total_amount = usd_total_amount
        self.id_credit_cards = id_credit_cards
        self.items_sets = items_sets

    #Getters
    

    #Setters

    #Appends
    def append_items_set(self,item_set):
        self.items_sets.append(item_set)

    #Calculations
    def calc_total_amount_ars(self):
        return round(sum([item_set.calc_total_amount_ars() for item_set in self.items_sets]),2)

    def calc_total_amount_ars_per_card(self):
        return [item_set.calc_total_amount_ars() for item_set in self.items_sets if item_set.type == 'buy']

    def calc_total_amount_taxes_ars(self):
        return round(sum([item_set.calc_total_amount_ars() for item_set in self.items_sets if item_set.type == 'taxes']),2)
            
    def calc_total_amount_buys_ars(self):
        return round(sum([item_set.calc_total_amount_ars() for item_set in self.items_sets if item_set.type == 'buy']),2)

    def calc_next_statement_total_quotes(self):
        return round(sum([item_set.calc_total_amount_ars() for item_set in self.get_next_statement_quotes_item_sets() if item_set.type == 'buy']),2)

    def calc_next_statement_total_quotes_per_card(self):
        return [item_set.calc_total_amount_ars() for item_set in self.get_next_statement_quotes_item_sets() if item_set.type == 'buy']

    def set_calcs(self):
        self.ars_total_amount = self.calc_total_amount_ars()

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

    #Prints
    def print_all_items(self):
        for item_set in self.items_sets: item_set.print_all_items()
    
    def print_all_item_sets(self):
        for item_set in self.items_sets: print(item_set)

    def print_next_statement_quotes_all_item_sets(self):
        for item_set in self.get_next_statement_quotes_item_sets(): print(item_set)

    def print_next_statement_quotes_all_items(self):
        for item_set in self.get_next_statement_quotes_item_sets(): item_set.print_all_items()
