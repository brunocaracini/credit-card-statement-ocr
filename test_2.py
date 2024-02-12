from libraries.ocr_engine import OcrEngine
from controllers.statement_controller import StatementController, OcrEngine
from submodules.google_drive_module.drive import GoogleDrive
import os


statement_controller = StatementController()
file = GoogleDrive.download_file_by_id("10tsSxQIgoJnP9zKLFbpEFSXoUGEA7e3X")
ocr = OcrEngine()

ocr.statement_orc_scanner(
    bank="HSBC",
    entity="MASTERCARD",
    pdf_content=file
)

for iset in ocr.statement.items_sets:
    print(iset)

ocr.statement.set_calcs()
print(ocr.statement.taxes)
print(ocr.statement.ars_total_amount)