from controllers.statement_controller import StatementController
from data.data_statement import DataStatement
sc = StatementController()
s = sc.insert_with_ocr(
    filepath='Resumen de tarjeta de crédito VISA-03-04-2023.pdf',
    entity='visa',
    bank='santander',
    year=2023,
    month=4,
    id_user=1
)
print(s.ars_total_amount)
