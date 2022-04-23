from controllers.statement_controller import StatementController

sc = StatementController()
sc.statement_orc_scanner_visa('Visa ICBC Resumen 202202.pdf',entity='VISA')
sc.statement.print_all_items()