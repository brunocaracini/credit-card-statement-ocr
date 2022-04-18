"""
   IMPORTS
"""
from types import TracebackType

class Statement:
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
            