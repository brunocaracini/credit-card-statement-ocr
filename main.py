from controllers.statement_controller import StatementController

sc = StatementController()
sc.statement_orc_scanner_visa('Visa ICBC Resumen 202202.pdf',entity='VISA')
print(sc.statement.calc_total_amount_ars())

for item_set in [item for item in sc.statement.items_sets]:
    print(item_set)