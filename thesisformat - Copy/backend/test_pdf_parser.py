from apps.documents.parser.pdf_parser import parse_pdf


print("=" * 60)
print("TEST PDF PARSER")
print("=" * 60)

file_path = r"D:\test_pdf.pdf"

result = parse_pdf(file_path)

print("\nFILE:")
print(result["file_name"])

print("\nJUMLAH HALAMAN:")
print(result["page_count"])

print("\nHALAMAN:")

for page in result["pages"]:
    print(f"\n--- Page {page['page_number']} ---")
    print(f"Width  : {page['width']}")
    print(f"Height : {page['height']}")
    print(f"Text   : {page['text'][:500]}")

print("\n" + "=" * 60)
print("TEST SELESAI")
print("=" * 60)