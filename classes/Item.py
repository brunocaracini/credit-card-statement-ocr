import re

class Item:
    """
       Class that represents an item of the credit card statement. An item is a
       a charge, such as a purchase or a tax.
    """

    def __init__(self,id=None,date=None,concept=None,ars_amount=0,usd_amount=0,current_quota=None,total_quotes=None,receipt='-', type='buy'):
        self.id = id
        self.date = date
        self.concept = concept
        self.ars_amount = ars_amount
        self.usd_amount = usd_amount
        self.current_quota = current_quota
        self.total_quotes = total_quotes
        self.receipt = receipt
        self.type = type
        self.porcentage_paid = current_quota

    def __str__(self) -> str:
        return f"""
            Item
                ID: {self.id}
                Date: {self.date}
                Concept: {self.concept}
                ARS Amount: {self.ars_amount}
                USD Amount: {self.usd_amount}
                Current Quote: {self.current_quota}
                Total Quotes: {self.total_quotes}
                Receipt Number: {self.receipt}
                Type: {self.type}
            """  
    
    #Methods
    def set_quotes_values_from_string(self,value,quote_prefix=''):
        value = value.replace(quote_prefix,'').strip(' ')
        current_quota,total_quotes = value.split('/')
        self.current_quota = int(re.sub(r'\D', '', current_quota))
        self.total_quotes = int(re.sub(r'\D', '', total_quotes))
        self.porcentage_paid = round((self.current_quota - 1) * 100/self.total_quotes) if self.type != 'taxes' else None
    
    
