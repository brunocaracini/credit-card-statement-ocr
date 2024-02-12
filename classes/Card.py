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
        self.id = id
        self.entity = entity
        self.bank = bank
        self.expiration_date = expiration_date
        self.is_extension = is_extension
        self.last_four_numbers = last_four_numbers
        self.drive_path = drive_path

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

    # Calculations
    def get_last_four_numbers(self):
        return self.number[-4:]
