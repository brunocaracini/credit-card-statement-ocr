"""
   IMPORTS
"""

from ast import iter_child_nodes


class ItemsSet:
    """
       Class thar repsents a set of items of the credit card statement
    """

    def __init__(self,items=[],card=None,type='buy',id=None,total_ars_amount=0):
        self.id = id
        self.items = items
        self.card = card
        self.total_ars_amount = total_ars_amount
        self.type = type

    def __str__(self) -> str:
        return f"""
            Item Set
                ID: {self.id}
                Items: {str(self.get_items_count()) + " Items"}
                Card: {'Credit Card'}
                Total Amount ARS: {self.calc_total_amount_ars()}
                Type: {self.type}
            """  

    #Appends
    def append_item(self,item):
        self.items.append(item)

    #Calculations
    def calc_total_amount_ars(self,ret=False):
        return round(sum([item.ars_amount for item in self.items if item.ars_amount]),2) if self.items else 0
    
    def calc_total_amount_usd(self,ret=False):
        return round(sum([item.usd_amount for item in self.items if item.usd_amount]),2) if self.items else 0

    def get_items_count(self):
        return len(self.items)

    def get_next_statement_quotes_items(self):
        quotes_item_set = self
        quotes_item_set.items = list(filter(lambda x: x.type != 'taxes' and x.current_quota < x.total_quotes,quotes_item_set.items))
        return quotes_item_set

    def count_quotes_buys(self):
        return len([item for item in self.items if item.type == 'buy' and item.total_quotes is not None and item.total_quotes > 1])
        
    #Prints
    def print_all_items(self):
        for item in self.items: print(item)
    