from controllers.statement_controller import StatementController

sc = StatementController()
sc.statement_orc_scanner_visa('Resumen de tarjeta de crédito VISA-04-04-2022.pdf',entity='VISA')
print(sc.statement.calc_total_amount_ars())

for item_set in [item for item in sc.statement.items_sets]:
    print(item_set)