from apps.documents.parser.docx_parser import parse_docx


print("=" * 60)
print("TEST DOCX PARSER")
print("=" * 60)

file_path = r"D:\test_docx.docx"

result = parse_docx(file_path)

print("\nFILE:")
print(result["file_name"])

print("\nJUMLAH PARAGRAF:")
print(result["paragraph_count"])

print("\nPARAGRAF:")
for index, paragraph in enumerate(result["paragraphs"], start=1):
    print(f"\n[{index}]")
    print(f"Text      : {paragraph['text']}")
    print(f"Style     : {paragraph['style']}")
    print(f"Alignment : {paragraph['alignment']}")

print("\nSECTIONS / MARGIN:")

for index, section in enumerate(result["sections"], start=1):
    print(f"\nSection {index}")
    print(f"Top    : {section['top_margin']}")
    print(f"Bottom : {section['bottom_margin']}")
    print(f"Left   : {section['left_margin']}")
    print(f"Right  : {section['right_margin']}")

print("\n" + "=" * 60)
print("TEST SELESAI")
print("=" * 60)