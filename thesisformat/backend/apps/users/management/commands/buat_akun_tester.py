"""
Buat (atau setel ulang) akun untuk Tim Tester, sesuai
USERMANUAL/AKUN_TESTER_ThesisFormat.pdf:

    python manage.py buat_akun_tester

Jalankan sekali di laptop dan sekali di server setelah deploy. Aman
dijalankan berulang: akun yang sudah ada dikembalikan ke data semula
(mis. setelah tester tidak sengaja mengganti password-nya).
"""

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

# Akun khusus pengujian (bukan akun pribadi). Datanya sama dengan PDF.
TESTER_ACCOUNTS = [
    {
        "role": "Mahasiswa",
        "username": "tester_mahasiswa",
        "email": "mahasiswa.tester@example.com",
        "password": "TesterMhs#2026",
        "is_staff": False,
        "is_superuser": False,
    },
    {
        "role": "Admin",
        "username": "tester_admin",
        "email": "admin.tester@example.com",
        "password": "TesterAdmin#2026",
        # Admin = web dashboard (Staff) + Django Admin Panel /admin/ (Superuser).
        "is_staff": True,
        "is_superuser": True,
    },
]


class Command(BaseCommand):
    help = "Buat atau setel ulang akun Mahasiswa dan Admin untuk Tim Tester."

    def handle(self, *args, **options):
        User = get_user_model()
        for data in TESTER_ACCOUNTS:
            user, created = User.objects.get_or_create(username=data["username"])
            user.email = data["email"]
            user.is_staff = data["is_staff"]
            user.is_superuser = data["is_superuser"]
            user.is_active = True
            user.set_password(data["password"])
            user.save()
            status = "dibuat" if created else "disetel ulang"
            self.stdout.write(self.style.SUCCESS(
                f"{data['role']}: {data['username']} ({data['email']}) {status}."
            ))
