class Card:
    
    def __init__(self, id=None,entity=None,bank=None,number=None,last_four_numbers=None,expiration_date=None,holder=None,cvv=None,is_extension=None):
        self.id = id
        self.entity = entity
        self.bank = bank
        self.number = number
        self.expiration_date = expiration_date
        self.holder = holder
        self.cvv = cvv
        self.is_extension = is_extension
        self.last_four_numbers = last_four_numbers
    
    #Getters
    def get_id(self):
        return self.id
    
    def get_entity(self):
        return self.entity

    def get_bank(self):
        return self.bank
    
    #Calculations
    def calc_total_payment_for_last_period(self):
        pass
    
    def get_last_four_numbers(self):
        return self.number[-4:]