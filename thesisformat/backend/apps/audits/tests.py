import shutil
import tempfile

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import override_settings
from rest_framework.test import APITestCase

from apps.audits.models import AuditResult
from apps.documents.models import Document

User = get_user_model()

TEMP_MEDIA = tempfile.mkdtemp()

FINDINGS = [
    {"source": "physical", "status": "failed", "type": "error",
     "title": "font name", "location": "Dokumen", "detail": "Font salah"},
    {"source": "physical", "status": "passed", "type": "success",
     "title": "margin", "location": "Dokumen", "detail": "OK"},
    {"source": "semantic", "category": "abstrak", "status": "failed", "type": "error",
     "title": "Abstrak", "location": "Abstrak", "detail": "Terlalu panjang"},
]


@override_settings(MEDIA_ROOT=TEMP_MEDIA)
class AdminDashboardTests(APITestCase):

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA, ignore_errors=True)

    def setUp(self):
        self.admin = User.objects.create_user(
            username="admin@test.id", email="admin@test.id",
            password="rahasia123", is_staff=True,
        )
        self.student = User.objects.create_user(
            username="mhs@test.id", email="mhs@test.id",
            password="rahasia123", first_name="Siti",
        )
        self.doc_a = self._document("Skripsi A.docx", "tugas_akhir", score=80)
        self.doc_b = self._document("PKL B.docx", "pkl", score=60)
        # Dokumen tanpa hasil pemeriksaan.
        self.doc_c = Document.objects.create(
            user=self.student, title="Kosong.pdf", document_type="pkl",
            file=SimpleUploadedFile("c.pdf", b"x"),
        )

    def _document(self, title, document_type, score):
        document = Document.objects.create(
            user=self.student, title=title, document_type=document_type,
            status="completed", file=SimpleUploadedFile("f.docx", b"x"),
        )
        AuditResult.objects.create(
            document=document, physical_score=score, semantic_score=score,
            final_score=score, findings=FINDINGS,
            recommendations={"has_format_score": True, "has_semantic_score": True},
        )
        return document

    def _login(self, user):
        self.client.force_authenticate(user)

    # ---------- Hak akses ----------

    def test_requires_staff(self):
        self.assertEqual(self.client.get("/api/v1/admin/stats/").status_code, 401)
        self._login(self.student)
        for url in (
            "/api/v1/admin/stats/",
            "/api/v1/admin/documents/",
            f"/api/v1/admin/documents/{self.doc_a.pk}/",
        ):
            self.assertEqual(self.client.get(url).status_code, 403, url)
        response = self.client.patch(
            f"/api/v1/admin/documents/{self.doc_a.pk}/review/",
            {"review_status": "validated"}, format="json",
        )
        self.assertEqual(response.status_code, 403)

    def test_token_contains_is_staff(self):
        response = self.client.post(
            "/api/token/",
            {"username": "admin@test.id", "password": "rahasia123"},
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data["user"]["is_staff"])

    # ---------- Statistik ----------

    def test_stats(self):
        self._login(self.admin)
        data = self.client.get("/api/v1/admin/stats/").data
        overview = data["overview"]
        self.assertEqual(overview["total_documents"], 3)
        self.assertEqual(overview["total_students"], 1)
        self.assertEqual(overview["average_score"], 70.0)
        self.assertEqual(overview["passing_count"], 1)
        self.assertEqual(overview["review"]["pending"], 2)
        self.assertEqual(len(data["score_by_type"]), len(Document.DocumentType.choices))
        top = data["top_findings"][0]
        self.assertEqual(top["count"], 2)
        self.assertEqual(sum(b["count"] for b in data["score_distribution"]), 2)
        self.assertEqual(len(data["trend"]), 8)
        self.assertEqual(data["trend"][-1]["uploads"], 3)

    # ---------- Daftar dokumen ----------

    def test_document_list_filters_and_ordering(self):
        self._login(self.admin)
        data = self.client.get("/api/v1/admin/documents/?ordering=score_high").data
        self.assertEqual(data["count"], 3)
        self.assertEqual(
            [d["title"] for d in data["results"]],
            ["Skripsi A.docx", "PKL B.docx", "Kosong.pdf"],  # tanpa skor di bawah
        )
        data = self.client.get("/api/v1/admin/documents/?document_type=pkl").data
        self.assertEqual(data["count"], 2)
        data = self.client.get("/api/v1/admin/documents/?search=siti").data
        self.assertEqual(data["count"], 3)
        data = self.client.get("/api/v1/admin/documents/?review_status=none").data
        self.assertEqual([d["title"] for d in data["results"]], ["Kosong.pdf"])
        data = self.client.get("/api/v1/admin/documents/?page_size=2&page=2").data
        self.assertEqual((data["page"], data["total_pages"], len(data["results"])), (2, 2, 1))

    # ---------- Review ----------

    def test_review_correction_is_visible_to_student(self):
        self._login(self.admin)
        url = f"/api/v1/admin/documents/{self.doc_b.pk}/review/"

        response = self.client.patch(url, {"review_status": "corrected"}, format="json")
        self.assertEqual(response.status_code, 400)

        response = self.client.patch(
            url,
            {"review_status": "corrected", "corrected_score": 85,
             "review_note": "Temuan abstrak keliru", "rejected_findings": [2, 2]},
            format="json",
        )
        self.assertEqual(response.status_code, 200, response.data)
        self.assertEqual(response.data["score"], 85)
        self.assertEqual(response.data["review"]["system_score"], 60)
        self.assertEqual(response.data["review"]["reviewed_by"]["email"], "admin@test.id")
        self.assertEqual([f["rejected"] for f in response.data["findings"]], [False, False, True])

        # Mahasiswa melihat skor koreksi dan temuan yang ditolak tidak muncul.
        self._login(self.student)
        history = self.client.get("/api/v1/documents/history/").data["documents"]
        doc_b = next(d for d in history if d["id"] == self.doc_b.pk)
        self.assertEqual(doc_b["score"], 85)
        self.assertEqual(doc_b["findings_count"], 1)
        self.assertEqual(len(doc_b["result"]["findings"]), 2)

    def test_review_back_to_pending_resets(self):
        self._login(self.admin)
        url = f"/api/v1/admin/documents/{self.doc_a.pk}/review/"
        self.client.patch(url, {"review_status": "corrected", "corrected_score": 50}, format="json")
        response = self.client.patch(url, {"review_status": "pending"}, format="json")
        self.assertEqual(response.data["score"], 80)
        self.assertIsNone(response.data["review"]["reviewed_by"])
        self.assertIsNone(response.data["review"]["corrected_score"])

    def test_review_validation_errors(self):
        self._login(self.admin)
        response = self.client.patch(
            f"/api/v1/admin/documents/{self.doc_a.pk}/review/",
            {"review_status": "validated", "rejected_findings": [9]}, format="json",
        )
        self.assertEqual(response.status_code, 400)
        response = self.client.patch(
            f"/api/v1/admin/documents/{self.doc_c.pk}/review/",
            {"review_status": "validated"}, format="json",
        )
        self.assertEqual(response.status_code, 409)
        response = self.client.patch(
            "/api/v1/admin/documents/99999/review/",
            {"review_status": "validated"}, format="json",
        )
        self.assertEqual(response.status_code, 404)
