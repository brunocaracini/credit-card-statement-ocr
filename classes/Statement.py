"""
   IMPORTS
"""
import calendar

class Statement():
    """
       Class thar repsents a credit card statement
    """
    
    def __init__(self,id=None,bank=None,entity=None,year=None,month=12,taxes=None,ars_total_amount=None,usd_total_amount=None,id_credit_cards=None,items_sets=[],filepath=None,is_processed:bool=False):
        self.id = id
        self._bank = bank
        self._entity = entity
        self._year = year
        self._month = month
        self._taxes = taxes
        self._ars_total_amount = ars_total_amount
        self._usd_total_amount = usd_total_amount
        self._id_credit_cards = id_credit_cards
        self._items_sets = items_sets
        self._filepath = filepath
        self._is_processed = is_processed
        self.month_name = calendar.month_name[month]
        
    #Getters
    @property       
    def bank(self):
        return self._bank
    
    @property
    def entity(self):
        return self._entity
    
    @property
    def year(self):
        return self._year
    
    @property
    def month(self):
        return self._month
    
    @property
    def taxes(self):
        return self._taxes
    
    @property
    def ars_total_amount(self):
        return self._ars_total_amount
    
    @property
    def usd_total_amount(self):
        return self._usd_total_amount
    
    @property
    def id_credit_cards(self):
        return self._id_credit_cards
    
    @property
    def items_sets(self):
        return self._items_sets
    
    @property
    def filepath(self):
        return self._filepath
    
    @property
    def is_processed(self):
        return self.is_processed

    #Setters
    @bank.setter
    def bank(self, value):
        self._bank = value
    
    @entity.setter
    def entity(self, value):
        self._entity = value
    
    @year.setter
    def year(self, value):
        self._year = value
    
    @month.setter
    def month(self, value):
        self._month = value
    
    @taxes.setter
    def taxes(self, value):
        self._taxes = value
    
    @ars_total_amount.setter
    def ars_total_amount(self, value):
        self._ars_total_amount = value
    
    @usd_total_amount.setter
    def usd_total_amount(self, value):
        self._usd_total_amount = value
    
    @id_credit_cards.setter
    def id_credit_cards(self, value):
        self._id_credit_cards = value
    
    @items_sets.setter
    def items_sets(self, value):
        self._items_sets = value

    @filepath.setter
    def filepath(self, value):
        self._filepath = value

    @is_processed.setter
    def is_processed(self, value):
        self._is_processed = value

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
        for item_set in self.items_sets:
            item_set.total_ars_amount = item_set.calc_total_amount_ars()
        self.ars_total_amount = self.calc_total_amount_ars()
        self.taxes = self.calc_total_amount_taxes_ars()

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

    #Prints
    def print_all_items(self):
        for item_set in self.items_sets: item_set.print_all_items()
    
    def print_all_item_sets(self):
        for item_set in self.items_sets: print(item_set)

    def print_next_statement_quotes_all_item_sets(self):
        for item_set in self.get_next_statement_quotes_item_sets(): print(item_set)

    def print_next_statement_quotes_all_items(self):
        for item_set in self.get_next_statement_quotes_item_sets(): item_set.print_all_items()
