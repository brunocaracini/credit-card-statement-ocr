"""
   IMPORTS
"""

from ast import iter_child_nodes


class ItemsSet:
    """
       Class thar repsents a set of items of the credit card statement
    """

    def __init__(self,items=[],card=None,type='buy'):
        self._items = items
        self._card = card
        self._total_amount_ars = 0
        self._type = type

    def __str__(self) -> str:
        return f"""
            Item Set
                Items: {str(self.get_items_count()) + " Items"}
                Card: {'Credit Card'}
                Total Amount ARS: {self.calc_total_amount_ars()}
                Type: {self.type}
            """  

    #Getters
    @property       
    def items(self):
        return self._items
    @property
    def card(self):
        return self._card
    @property
    def total_amount_ars(self):
        return self._total_amount_ars
    @property
    def type(self):
        return self._type

    #Setters
    @items.setter
    def items(self,items):
        self._items = items

    @card.setter
    def card(self,card):
        self._card = card

    @total_amount_ars.setter
    def total_amount_ars(self,total_amount_ars):
        self._total_amount_ars = total_amount_ars
    
    @type.setter
    def type(self,type):
        self._type = type

    #Appends
    def append_item(self,item):
        self._items.append(item)

    #Calculations
    def calc_total_amount_ars(self,ret=False):
        return round(sum([item.ars_amount for item in self.items]),2)

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
    