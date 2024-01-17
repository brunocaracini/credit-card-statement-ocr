from controllers.statement_controller import StatementController
from data.data_statement import DataStatement
sc = StatementController()
s = sc.insert_with_ocr(
    filepath='Resumen de tarjeta de crédito VISA-12-2023.pdf',
    entity='visa',
    bank='Santander',
    year=2023,
    month=5,
    id_user=1,
    id_credit_cards=1
)
print(s.ars_total_amount)