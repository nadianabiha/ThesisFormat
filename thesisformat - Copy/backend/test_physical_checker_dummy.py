from types import SimpleNamespace

from apps.documents.parser.docx_parser import parse_docx
from apps.documents.checker.physical_checker import check_physical_rules

DOCX_FILE = r"D:\test_docx.docx"   # ganti ke PROPOSAL.docx kalau mau tes file itu


def make_rule(rule_key, value, styles=None):
    payload = {"value": value}
    if styles:
        payload["styles"] = styles
    return SimpleNamespace(rule_key=rule_key, rule_value=payload)


parsed = parse_docx(DOCX_FILE)

dummy_rules = [
    # Aturan umum font untuk seluruh dokumen
    make_rule("font_name", "Times New Roman"),

    # Judul / cover
    make_rule("font_size", 14, ["Title"]),
    make_rule("alignment", "CENTER", ["Title"]),

    # Isi naskah utama
    make_rule("font_size", 12, ["Body Text"]),
    make_rule("alignment", "JUSTIFY", ["Body Text"]),
    make_rule("line_spacing", 1.5, ["Body Text"]),

    # Margin dokumen
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

findings = check_physical_rules(parsed, dummy_rules)

print("=" * 60)
print("TEST PHYSICAL CHECKER DUMMY")
print("=" * 60)

for item in findings:
    print("\nRULE:", item["rule_key"])
    print("STATUS:", item["status"])
    print("MESSAGE:", item["message"])
    print("EXPECTED:", item["expected"])
    print("FOUND:", item["found"])

print("\nSELESAI")