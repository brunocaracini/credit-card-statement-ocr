class Card:
    
    def __init__(self, id=None,entity=None,bank=None,number=None,last_four_numbers=None,expiration_date=None,holder=None,cvv=None,is_extension=None):
        self._id = id
        self._entity = entity
        self._bank = bank
        self._number = number
        self._expiration_date = expiration_date
        self._holder = holder
        self._cvv = cvv
        self._is_extension = is_extension
        self._last_four_numbers = last_four_numbers
    
    def __str__(self) -> str:
        return f"""
            Card
                ID: {self.id}
                Entity: {self.entity}
                Bank: {self.bank}
                Number: {self.number}
                Expiration Date: {self.expiration_date}
                Holder: {self.holder}
                CVV: {self.cvv}
                Extension: {'True' if self.is_extension else 'False'}
                Last four numbers: {self.last_four_numbers}
            """

    #Getters
    @property
    def id(self):
        return self._id
    
    @property
    def entity(self):
        return self._entity

    @property
    def number(self):
        return self._number

    @property
    def bank(self):
        return self._bank
    
    @property
    def expiration_date(self):
        return self._expiration_date
    
    @property
    def holder(self):
        return self._holder
    
    @property
    def cvv(self):
        return self._cvv
    
    @property
    def is_extension(self):
        return self._is_extension
    
    @property
    def last_four_numbers(self):
        return self._last_four_numbers
    
    #Calculations
    def calc_total_payment_for_last_period(self):
        pass
    
    def get_last_four_numbers(self):
        return self.number[-4:]