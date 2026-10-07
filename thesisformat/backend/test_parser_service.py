from apps.documents.parser.parser_service import parse_document


print("=" * 60)
print("TEST PARSER SERVICE")
print("=" * 60)


docx_file = r"D:\test_docx.docx"
pdf_file = r"D:\test_pdf.pdf"


print("\nTEST DOCX")
docx_result = parse_document(docx_file)

print(f"File   : {docx_result['file_name']}")
print(f"Format : DOCX")
print(f"Jumlah paragraf : {docx_result['paragraph_count']}")


print("\nTEST PDF")
pdf_result = parse_document(pdf_file)

print(f"File   : {pdf_result['file_name']}")
print(f"Format : PDF")
print(f"Jumlah halaman : {pdf_result['page_count']}")


print("\n" + "=" * 60)
print("PARSER SERVICE BERHASIL")
print("=" * 60)