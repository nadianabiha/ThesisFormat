
from pathlib import Path
from apps.documents.parser.docx_parser import extract_docx_metadata

BASE_DIR = Path(__file__).resolve().parent
DOCX_FILE = Path(r"D:\test_docx.docx")

if not DOCX_FILE.exists():
    raise FileNotFoundError(
        f"File contoh tidak ditemukan: {DOCX_FILE}"
    )

metadata = extract_docx_metadata(DOCX_FILE)

print("=" * 50)
print("TEST DOCX METADATA")
print("=" * 50)
print("Nama file       :", metadata["file_name"])
print("Jumlah paragraf :", metadata["paragraph_count"])
print("Jumlah section  :", metadata["section_count"])
print("Nama font       :", metadata["font_names"])
print("Ukuran font (pt):", metadata["font_sizes"])
print("Margin section  :")

for index, section in enumerate(metadata["sections"], start=1):
    print(f"  Section {index}:")
    for side, value in section.items():
        print(f"    {side}: {value:.2f} cm")

print("\nTEST DOCX METADATA SELESAI")