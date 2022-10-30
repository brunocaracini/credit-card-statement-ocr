from data.data_statement import DataStatement

class StatementController:

    def __init__(self) -> None:
        self.data_statement = DataStatement()
    
    def get_all(self):
        return self.data_statement.get_all()

    def get_last(self):
        s = self.data_statement.get_last()
        s.set_calcs()
        return s
