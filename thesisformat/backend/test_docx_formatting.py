from pathlib import Path
from apps.documents.parser.docx_parser import parse_docx

DOCX_FILE = Path(r"D:\test_docx.docx")  # ganti kalau mau test file lain

if not DOCX_FILE.exists():
    raise FileNotFoundError(f"File tidak ditemukan: {DOCX_FILE}")

result = parse_docx(DOCX_FILE)

font_names = set()
font_sizes = set()

for paragraph in result["paragraphs"]:
    for run in paragraph["runs"]:
        if run["font_name"]:
            font_names.add(run["font_name"])
        if run["font_size"] is not None:
            font_sizes.add(run["font_size"])

print("=" * 50)
print("TEST DOCX FORMATTING")
print("=" * 50)
print("Nama file       :", result["file_name"])
print("Jumlah paragraf :", result["paragraph_count"])
print("Jumlah section  :", len(result["sections"]))

print("\nFont yang digunakan :", sorted(font_names))
print("Ukuran font (pt)    :", sorted(font_sizes))

print("\nMargin:")
for i, section in enumerate(result["sections"], start=1):
    print(f"\nSection {i}")
    print(f"  Top    : {section['top_margin']} cm")
    print(f"  Bottom : {section['bottom_margin']} cm")
    print(f"  Left   : {section['left_margin']} cm")
    print(f"  Right  : {section['right_margin']} cm")

print("\nContoh paragraf awal:")
for i, paragraph in enumerate(result["paragraphs"][:5], start=1):
    print(f"\nParagraf {i}")
    print("Teks:", repr(paragraph["text"][:100]))
    print("Style:", paragraph["style"])
    print("Alignment:", paragraph["alignment"])
    print("Line spacing:", paragraph["line_spacing"])
    print("Space before:", paragraph["space_before"])
    print("Space after:", paragraph["space_after"])
    print("First line indent:", paragraph["first_line_indent"])
    print("Runs:", paragraph["runs"][:3])

print("\nTEST DOCX FORMATTING SELESAI")