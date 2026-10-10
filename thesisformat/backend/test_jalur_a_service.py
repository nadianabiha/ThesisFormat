from types import SimpleNamespace

from apps.documents.parser.jalur_a_service import run_jalur_a


DOCX_FILE = r"D:\test_docx.docx"  # ganti ke PROPOSAL.docx kalau mau tes file itu

dummy_rules = [
    SimpleNamespace(rule_key="font_name", rule_value={"value": "Times New Roman"}),
    SimpleNamespace(rule_key="font_size", rule_value={"value": 14, "styles": ["Title"]}),
    SimpleNamespace(rule_key="alignment", rule_value={"value": "CENTER", "styles": ["Title"]}),
    SimpleNamespace(rule_key="font_size", rule_value={"value": 12, "styles": ["Body Text"]}),
    SimpleNamespace(rule_key="alignment", rule_value={"value": "JUSTIFY", "styles": ["Body Text"]}),
    SimpleNamespace(rule_key="line_spacing", rule_value={"value": 1.5, "styles": ["Body Text"]}),
    SimpleNamespace(
        rule_key="margin",
        rule_value={
            "value": {
                "top_margin": 3,
                "bottom_margin": 3,
                "left_margin": 4,
                "right_margin": 3,
            }
        },
    ),
]

result = run_jalur_a(DOCX_FILE, dummy_rules)

print("=" * 60)
print("TEST JALUR A SERVICE")
print("=" * 60)

print("Checker applied:", result["checker_applied"])
print("Summary:", result["summary"])

print("\n--- Findings ---")
for item in result["findings"]:
    print("\nRULE:", item["rule_key"])
    print("STATUS:", item["status"])
    print("MESSAGE:", item["message"])
    print("EXPECTED:", item["expected"])
    print("FOUND:", item["found"])

print("\nSELESAI")