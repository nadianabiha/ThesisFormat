import os

os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE",
    "config.settings",
)

import django

django.setup()

from apps.rules.models import MasterRule

from apps.documents.parser.docx_parser import parse_docx
from apps.documents.checker.physical_checker import (
    check_physical_rules,
)


print("=" * 60)
print("TEST PHYSICAL RULE CHECKER")
print("=" * 60)


# ==========================================
# 1. AMBIL MASTER RULE
# ==========================================

rules = MasterRule.objects.filter(
    category=MasterRule.Category.PHYSICAL,
    active=True,
)

print("\nJUMLAH RULE AKTIF:")
print(rules.count())


# ==========================================
# 2. PARSE DOKUMEN TEST
# ==========================================

file_path = r"D:\test_docx.docx"

print("\nDOKUMEN:")
print(file_path)

parsed_document = parse_docx(file_path)


# ==========================================
# 3. JALANKAN PHYSICAL CHECKER
# ==========================================

findings = check_physical_rules(
    parsed_document,
    rules,
)


# ==========================================
# 4. TAMPILKAN HASIL
# ==========================================

print("\nHASIL PEMERIKSAAN:")

for finding in findings:

    print("\n-----------------------------")

    print(f"Rule     : {finding['rule_key']}")
    print(f"Status   : {finding['status']}")
    print(f"Message  : {finding['message']}")
    print(f"Expected : {finding['expected']}")
    print(f"Found    : {finding['found']}")


print("\n" + "=" * 60)
print("TEST SELESAI")
print("=" * 60)