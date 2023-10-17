class Item:
    """
       Class that represents an item of the credit card statement. An item is a
       a charge, such as a purchase or a tax.
    """

    def __init__(self,id=None,date=None,concept=None,ars_amount=None,usd_amount=None,current_quota=None,total_quotes=None,receipt=None, type='buy'):
        self._id = id
        self._date = date
        self._concept = concept
        self._ars_amount = ars_amount
        self._usd_amount = usd_amount
        self._current_quota = current_quota
        self._total_quotes = total_quotes
        self._receipt = receipt
        self._type = type
        self.porcentage_paid = round((self.current_quota - 1) * 100/self.total_quotes) if self.type != 'taxes' else None

    def __str__(self) -> str:
        return f"""
            Item
                ID: {self.id}
                Date: {self.date}
                Concept: {self.concept}
                Ars Amount: {self.ars_amount}
                USD Amount: {self.usd_amount}
                Current Quote: {self.current_quota}
                Total Quotes: {self.total_quotes}
                Receipt Number: {self.receipt}
                Type: {self.type}
            """  
    #Getters
    @property
    def id(self):
        return self._id

    @property
    def date(self):
        return self._date

    @property
    def ars_amount(self):
        return self._ars_amount

    @property
    def concept(self):
        return self._concept

    @property
    def usd_amount(self):
        return self._usd_amount

    @property
    def current_quota(self):
        return self._current_quota

    @property
    def total_quotes(self):
        return self._total_quotes
    
    @property
    def receipt(self):
        return self._receipt

    @property
    def type(self):
        return self._type

    #Setters
    @id.setter
    def id(self,id):
        self._id = id

    @date.setter
    def date(self,date):
        self._date = date

    @concept.setter
    def concept(self,concept):
        self._concept = concept

    @ars_amount.setter
    def ars_amount(self,ars_amount):
        self._ars_amount = ars_amount

    @usd_amount.setter
    def usd_amount(self,usd_amount):
        self._usd_amount = usd_amount

    @receipt.setter
    def receipt(self,receipt):
        self._receipt = receipt

    @total_quotes.setter
    def total_quotes(self,total_quotes):
        self._total_quotes = total_quotes

    @current_quota.setter
    def current_quota(self,current_quota):
        self._current_quota = current_quota

    @current_quota.setter
    def current_quota(self,current_quota):
        self._current_quota = current_quota
    
    #Methods
    def set_quotes_values_from_string(self,value,quote_prefix=''):
        value = value.replace(quote_prefix,'').strip(' ')
        current_quota,total_quotes = value.split('/')
        self.current_quota = int(current_quota)
        self.total_quotes = int(total_quotes)
