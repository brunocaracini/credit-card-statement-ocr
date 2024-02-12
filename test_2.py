from libraries.ocr_engine import OcrEngine
from controllers.statement_controller import StatementController, OcrEngine
from submodules.google_drive_module.google_drive import GoogleDrive
import os


statement_controller = StatementController()
file = GoogleDrive.download_file_by_id("1W_PBV2Lz9_yi-uLM5g-3GJfARsoJtxj9")
ocr = OcrEngine()

ocr.statement_orc_scanner(
    bank="VISA",
    entity="Coinag",
    pdf_content=file
)

for iset in ocr.statement.items_sets:
    print(iset)

ocr.statement.set_calcs()
print(ocr.statement.taxes)
print(ocr.statement.ars_total_amount)