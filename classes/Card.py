class Card:
    def __init__(
        self,
        id: int = None,
        entity: str = None,
        bank: str = None,
        last_four_numbers: str = None,
        expiration_date: str = None,
        is_extension: bool = None,
        drive_path: str = None,
    ):
        """
        Constructor for the Card class.

        Parameters:
        - id (int): The ID of the card.
        - entity (str): The entity associated with the card.
        - bank (str): The bank associated with the card.
        - last_four_numbers (str): The last four digits of the card number.
        - expiration_date (str): The expiration date of the card.
        - is_extension (bool): Flag indicating whether the card is an extension.
        - drive_path (str): The drive path associated with the card.
        """
        self._id = id
        self._entity = entity
        self._bank = bank
        self._expiration_date = expiration_date
        self._is_extension = is_extension
        self._last_four_numbers = last_four_numbers
        self._drive_path = drive_path

    def __str__(self) -> str:
        return f"""
            Card
                ID: {self.id}
                Entity: {self.entity}
                Bank: {self.bank}
                Expiration Date: {self.expiration_date}
                Extension: {'True' if self.is_extension else 'False'}
                Last four numbers: {self.last_four_numbers}
                Drive Path: {self.drive_path}
            """

    # Getters
    @property
    def id(self):
        return self._id

    @property
    def entity(self):
        return self._entity

    @property
    def bank(self):
        return self._bank

    @property
    def expiration_date(self):
        return self._expiration_date

    @property
    def is_extension(self):
        return self._is_extension

    @property
    def last_four_numbers(self):
        return self._last_four_numbers

    @property
    def drive_path(self):
        return self._drive_path

    # Setters
    @id.setter
    def id(self, value):
        self._id = value

    @entity.setter
    def entity(self, value):
        self._entity = value

    @bank.setter
    def bank(self, value):
        self._bank = value

    @expiration_date.setter
    def expiration_date(self, value):
        self._expiration_date = value

    @is_extension.setter
    def is_extension(self, value):
        self._is_extension = value

    @last_four_numbers.setter
    def last_four_numbers(self, value):
        self._last_four_numbers = value

    @drive_path.setter
    def drive_path(self, value):
        self._drive_path = value

    # Calculations
    def get_last_four_numbers(self):
        return self.number[-4:]
