from controllers.statement_controller import StatementController

sc = StatementController()
s = sc.get_last().calc_total_amount_ars()
print(s.ars_total_amount)