from functools import wraps

from data.data import Data
from classes.Card import Card


def instantiate_cards(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)

        if isinstance(result, tuple):
            return Card(**dict(zip(DataCard.COLUMNS, result)))
        elif isinstance(result, list):
            return [Card(**dict(zip(DataCard.COLUMNS, values))) for values in result]
        else:
            raise ValueError(
                "Unsupported result type. Function should return a named tuple or a list of named tuples."
            )
    return wrapper


class DataCard(Data):
    TABLE_NAME = "credit_cards"
    COLUMNS = [
        "id",
        "bank",
        "entity",
        "expiration_date",
        "last_four_numbers",
        "is_extension",
        "drive_path",
    ]

    FOREIGN_KEYS = [
        "id_user"
    ]

    def __init__(self):
        super().__init__()

    @instantiate_cards
    def get_all(self):
        return super().select(table=self.TABLE_NAME, columns=self.COLUMNS)

    def insert(self, card: Card, id_user: int):
        values = [getattr(card, col) for col in self.COLUMNS if getattr(card, col)] + [
            id_user
        ]
        columns = [
            col for col in self.COLUMNS if getattr(card, col)
        ] + self.FOREIGN_KEYS
        return super().insert(self.TABLE_NAME, columns, values)
