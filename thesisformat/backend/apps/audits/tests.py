import shutil
import tempfile
from unittest import mock

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import SimpleTestCase, override_settings
from rest_framework.test import APITestCase

from apps.audits.models import AIRun, AuditResult, FindingFeedback
from apps.documents.models import Document
from apps.documents.scoring import normalize_category, normalize_semantic
from apps.documents.semantic.prompts import DEFAULT_ASPECTS, build_semantic_prompt
from apps.rules.models import MasterRule, RuleVersion

User = get_user_model()

TEMP_MEDIA = tempfile.mkdtemp()

# Format 50 (1 lulus, 1 gagal) + semantik 0 (abstrak gagal)
# -> skor = 0.4*50 + 0.6*0 = 20.
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

    def _review(self, document, body):
        return self.client.patch(
            f"/api/v1/admin/documents/{document.pk}/review/", body, format="json",
        )

    # ---------- Hak akses ----------

    def test_requires_staff(self):
        self.assertEqual(self.client.get("/api/v1/admin/stats/").status_code, 401)
        self._login(self.student)
        for url in (
            "/api/v1/admin/stats/",
            "/api/v1/admin/documents/",
            f"/api/v1/admin/documents/{self.doc_a.pk}/",
            "/api/v1/admin/ai-performance/",
            "/api/v1/admin/ai-performance/retest-candidates/",
            "/api/v1/admin/rules/",
        ):
            self.assertEqual(self.client.get(url).status_code, 403, url)
        self.assertEqual(self._review(self.doc_a, {}).status_code, 403)
        response = self.client.post(f"/api/v1/admin/documents/{self.doc_a.pk}/reanalyze/")
        self.assertEqual(response.status_code, 403)

    def test_token_contains_is_staff(self):
        response = self.client.post(
            "/api/token/",
            {"username": "admin@test.id", "password": "rahasia123"},
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data["user"]["is_staff"])

    # ---------- Statistik & daftar ----------

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
        self.assertEqual(data["top_findings"][0]["count"], 2)
        self.assertEqual(sum(b["count"] for b in data["score_distribution"]), 2)
        self.assertEqual(len(data["trend"]), 8)
        self.assertEqual(data["trend"][-1]["uploads"], 3)

    def test_document_list_filters_and_ordering(self):
        self._login(self.admin)
        data = self.client.get("/api/v1/admin/documents/?ordering=score_high").data
        self.assertEqual(
            [d["title"] for d in data["results"]],
            ["Skripsi A.docx", "PKL B.docx", "Kosong.pdf"],  # tanpa skor di bawah
        )
        self.assertEqual(self.client.get("/api/v1/admin/documents/?document_type=pkl").data["count"], 2)
        self.assertEqual(self.client.get("/api/v1/admin/documents/?search=siti").data["count"], 3)
        data = self.client.get("/api/v1/admin/documents/?review_status=none").data
        self.assertEqual([d["title"] for d in data["results"]], ["Kosong.pdf"])
        data = self.client.get("/api/v1/admin/documents/?page_size=2&page=2").data
        self.assertEqual((data["page"], data["total_pages"], len(data["results"])), (2, 2, 1))

    def test_document_list_score_and_ai_filters(self):
        self._login(self.admin)
        AuditResult.objects.filter(document=self.doc_b).update(
            recommendations={"has_format_score": True, "has_semantic_score": False},
        )

        def titles(query):
            data = self.client.get(f"/api/v1/admin/documents/?{query}").data
            return sorted(d["title"] for d in data["results"])

        self.assertEqual(titles("score_min=75"), ["Skripsi A.docx"])
        self.assertEqual(titles("score_max=74"), ["PKL B.docx"])
        self.assertEqual(titles("ai=success"), ["Skripsi A.docx"])
        self.assertEqual(titles("ai=failed"), ["PKL B.docx"])
        self.assertEqual(len(titles("score_min=abc")), 3)

    def test_stats_consistent_with_filters(self):
        self._login(self.admin)
        overview = self.client.get("/api/v1/admin/stats/").data["overview"]
        self.assertEqual(
            overview["passing_count"],
            self.client.get("/api/v1/admin/documents/?score_min=75").data["count"],
        )
        self.assertEqual(
            overview["needs_improvement"],
            self.client.get("/api/v1/admin/documents/?score_max=74").data["count"],
        )

    def test_student_list(self):
        self._login(self.admin)
        data = self.client.get("/api/v1/admin/students/").data
        self.assertEqual(data["count"], 1)
        student = data["results"][0]
        self.assertEqual(student["document_count"], 3)
        self.assertEqual(student["average_score"], 70.0)
        self.assertEqual(student["pending_review"], 2)

    # ---------- 1. CATAT: tinjauan admin ----------

    def test_marking_finding_incorrect_recalculates_score(self):
        self._login(self.admin)

        # Tandai temuan "Abstrak" keliru -> semantik tidak lagi gagal.
        response = self._review(
            self.doc_b,
            {"rejected_findings": [2, 2], "review_note": "Abstrak sudah sesuai"},
        )
        self.assertEqual(response.status_code, 200, response.data)
        # Dihitung ulang: hanya format (50) yang tersisa -> skor 50.
        self.assertEqual(response.data["score"], 50)
        review = response.data["review"]
        self.assertEqual(review["status"], "corrected")
        self.assertEqual(review["system_score"], 60)
        self.assertEqual(review["corrected_score"], 50)
        self.assertEqual(review["removed_findings"], 1)
        self.assertEqual(review["reviewed_by"]["email"], "admin@test.id")
        self.assertEqual([f["rejected"] for f in response.data["findings"]], [False, False, True])
        self.assertEqual(response.data["findings"][0]["aspect"], "font_name")
        self.assertEqual(response.data["findings"][2]["aspect_label"], "Abstrak")

        # Umpan balik tercatat untuk pengamatan pola.
        feedback = FindingFeedback.objects.get(document=self.doc_b)
        self.assertEqual((feedback.source, feedback.aspect), ("semantic", "abstrak"))

        # Mahasiswa melihat skor hasil hitung ulang, temuan keliru disembunyikan.
        self._login(self.student)
        history = self.client.get("/api/v1/documents/history/").data["documents"]
        doc_b = next(d for d in history if d["id"] == self.doc_b.pk)
        self.assertEqual(doc_b["score"], 50)
        self.assertEqual(doc_b["result"]["system_score"], 60)
        self.assertEqual(doc_b["result"]["removed_findings"], 1)
        self.assertEqual(doc_b["result"]["review_note"], "Abstrak sudah sesuai")
        self.assertEqual(len(doc_b["result"]["findings"]), 2)

    def test_unmarking_restores_score_and_removes_feedback(self):
        self._login(self.admin)
        self._review(self.doc_a, {"rejected_findings": [0]})
        self.assertEqual(FindingFeedback.objects.count(), 1)

        response = self._review(self.doc_a, {"rejected_findings": []})
        self.assertEqual(response.data["score"], 80)
        self.assertEqual(response.data["review"]["status"], "validated")
        self.assertIsNone(response.data["review"]["corrected_score"])
        self.assertEqual(FindingFeedback.objects.count(), 0)

    def test_review_validation_errors(self):
        self._login(self.admin)
        self.assertEqual(self._review(self.doc_a, {"rejected_findings": [9]}).status_code, 400)
        # Temuan yang lulus tidak bisa ditandai keliru.
        self.assertEqual(self._review(self.doc_a, {"rejected_findings": [1]}).status_code, 400)
        self.assertEqual(self._review(self.doc_c, {}).status_code, 409)
        response = self.client.patch(
            "/api/v1/admin/documents/99999/review/", {}, format="json",
        )
        self.assertEqual(response.status_code, 404)

    # ---------- 2. AMATI: kinerja AI ----------

    def test_ai_performance(self):
        self._login(self.admin)
        AIRun.objects.create(document=self.doc_a, trigger="upload", status="success",
                             model="gemini-3.5-flash", duration_ms=20000)
        AIRun.objects.create(document=self.doc_b, trigger="upload", status="failed",
                             error_type="unavailable", unknown_categories=["isi"])
        self._review(self.doc_a, {"rejected_findings": [2]})

        data = self.client.get("/api/v1/admin/ai-performance/").data
        runs = data["runs"]
        self.assertEqual((runs["total"], runs["success"], runs["failed"]), (2, 1, 1))
        self.assertEqual(runs["success_rate"], 50.0)
        self.assertEqual(runs["avg_duration_ms"], 20000)
        self.assertEqual(runs["failure_reasons"][0]["type"], "unavailable")
        self.assertEqual(runs["by_model"][0]["model"], "gemini-3.5-flash")
        self.assertEqual(runs["unknown_category_runs"], 1)

        abstrak = next(a for a in data["aspects"] if a["aspect"] == "abstrak")
        self.assertEqual(abstrak["failed_count"], 2)    # gagal di 2 dokumen
        self.assertEqual(abstrak["feedback_count"], 1)  # 1 ditandai keliru
        self.assertEqual(abstrak["feedback_rate"], 50.0)
        self.assertEqual(data["aspects"][0]["aspect"], "abstrak")  # paling bermasalah di atas
        self.assertEqual(data["recent_feedback"][0]["aspect_label"], "Abstrak")
        self.assertEqual(data["versions"][-1]["version"], 0)
        self.assertEqual(data["feedback_total"], 1)

    def test_retest_candidates(self):
        self._login(self.admin)
        self._review(self.doc_a, {"rejected_findings": [2]})
        self._review(self.doc_b, {"rejected_findings": [0]})
        data = self.client.get(
            "/api/v1/admin/ai-performance/retest-candidates/?source=semantic&aspect=abstrak"
        ).data
        self.assertEqual([r["document_id"] for r in data["results"]], [self.doc_a.pk])

    # ---------- 3. PERBAIKI: aturan & instruksi AI ----------

    def test_rules_list_and_update_creates_version(self):
        self._login(self.admin)
        data = self.client.get("/api/v1/admin/rules/").data
        # Migration: 7 aspek umum + 6 aturan susunan bab per jenis dokumen,
        # tercatat sebagai 1 versi (Penyesuaian Pedoman Polinela 2018).
        self.assertEqual(len(data["semantic"]), 13)
        self.assertEqual(data["current_version"], 1)
        self.assertEqual(RuleVersion.objects.count(), 1)

        abstrak = MasterRule.objects.get(category="semantic", rule_key="abstrak", document_type="")
        response = self.client.patch(
            f"/api/v1/admin/rules/{abstrak.pk}/",
            {"instruction": "Abstrak maksimal 300 kata.", "note": "Longgarkan abstrak"},
            format="json",
        )
        self.assertEqual(response.status_code, 200, response.data)
        self.assertEqual(response.data["version"], RuleVersion.current())
        self.assertEqual(RuleVersion.current(), 2)
        version = RuleVersion.objects.get(pk=2)
        self.assertEqual(version.note, "Longgarkan abstrak")
        self.assertEqual(version.changes[0]["after"]["instruction"], "Abstrak maksimal 300 kata.")

        # Instruksi baru dipakai saat membangun prompt.
        aspects = MasterRule.semantic_aspects("pkl")
        self.assertIn("Abstrak maksimal 300 kata.", build_semantic_prompt("teks", "PKL", aspects))

        # Tanpa perubahan -> ditolak.
        response = self.client.patch(
            f"/api/v1/admin/rules/{abstrak.pk}/",
            {"instruction": "Abstrak maksimal 300 kata."}, format="json",
        )
        self.assertEqual(response.status_code, 400)

    def test_disable_aspect_and_validation(self):
        self._login(self.admin)
        semantic = MasterRule.objects.filter(category="semantic", document_type="")
        abstrak = semantic.get(rule_key="abstrak")
        self.client.patch(f"/api/v1/admin/rules/{abstrak.pk}/", {"active": False}, format="json")
        keys = [a["key"] for a in MasterRule.semantic_aspects("pkl")]
        self.assertNotIn("abstrak", keys)
        self.assertEqual(len(keys), 6)

        # Aspek terakhir tidak boleh dinonaktifkan.
        semantic.exclude(pk=abstrak.pk).exclude(rule_key="sitasi").update(active=False)
        sitasi = semantic.get(rule_key="sitasi")
        response = self.client.patch(f"/api/v1/admin/rules/{sitasi.pk}/", {"active": False}, format="json")
        self.assertEqual(response.status_code, 400)

        font = MasterRule.objects.create(
            category="physical", rule_key="font_size", rule_value={"value": 12},
        )
        bad = self.client.patch(f"/api/v1/admin/rules/{font.pk}/", {"value": 99}, format="json")
        self.assertEqual(bad.status_code, 400)
        good = self.client.patch(f"/api/v1/admin/rules/{font.pk}/", {"value": "11.5"}, format="json")
        self.assertEqual(good.status_code, 200, good.data)
        self.assertEqual(good.data["rule"]["value"], 11.5)

    # ---------- 4. BUKTIKAN: analisis ulang ----------

    @mock.patch("apps.documents.pipeline.run_jalur_b")
    @mock.patch("apps.documents.pipeline.run_jalur_a")
    def test_reanalyze_compares_with_previous_feedback(self, jalur_a, jalur_b):
        self._login(self.admin)
        self._review(self.doc_b, {"rejected_findings": [0, 2]})  # font name & abstrak keliru

        jalur_a.return_value = {
            "parsed_document": {"paragraphs": [{"text": "isi"}]},
            "findings": [{"rule_key": "font_name", "status": "failed", "message": "Font salah"}],
            "summary": {},
        }
        jalur_b.return_value = {
            "findings": [{"category": "Abstract", "issue": "Abstrak sesuai", "status": "passed"}],
            "summary": {}, "error": None, "error_type": "", "model": "gemini-3.5-flash",
            "duration_ms": 1234, "unknown_categories": [],
        }

        response = self.client.post(f"/api/v1/admin/documents/{self.doc_b.pk}/reanalyze/")
        self.assertEqual(response.status_code, 200, response.data)
        comparison = response.data["comparison"]
        self.assertEqual(comparison["ai_status"], "success")
        result = {item["aspect"]: item["still_present"] for item in comparison["feedback"]}
        self.assertEqual(result, {"font_name": True, "abstrak": False})
        self.assertEqual((comparison["resolved"], comparison["still_present"]), (1, 1))
        # Kategori "Abstract" dikenali sebagai "abstrak"; tanda keliru direset.
        document = response.data["document"]
        self.assertEqual(document["findings"][1]["aspect"], "abstrak")
        self.assertEqual(document["review"]["status"], "pending")
        self.assertEqual(document["review"]["removed_findings"], 0)
        self.assertEqual(document["ai"]["model"], "gemini-3.5-flash")
        # Riwayat umpan balik tetap ada untuk pengamatan pola.
        self.assertEqual(FindingFeedback.objects.filter(document=self.doc_b).count(), 2)

        run = AIRun.objects.get(document=self.doc_b)
        self.assertEqual((run.trigger, run.triggered_by, run.status), ("reanalyze", self.admin, "success"))

        # Instruksi AI dari MasterRule dikirim ke Jalur B.
        aspects = jalur_b.call_args.kwargs["aspects"]
        self.assertEqual(len(aspects), 7)

    @mock.patch("apps.documents.pipeline.run_jalur_b")
    @mock.patch("apps.documents.pipeline.run_jalur_a")
    def test_reanalyze_when_ai_fails(self, jalur_a, jalur_b):
        self._login(self.admin)
        self._review(self.doc_b, {"rejected_findings": [2]})
        jalur_a.return_value = {"parsed_document": {}, "findings": [], "summary": {}}
        jalur_b.return_value = {
            "findings": [], "summary": {}, "error": "503 UNAVAILABLE",
            "error_type": "unavailable", "model": "", "duration_ms": 5,
            "unknown_categories": [],
        }
        response = self.client.post(f"/api/v1/admin/documents/{self.doc_b.pk}/reanalyze/")
        comparison = response.data["comparison"]
        self.assertEqual(comparison["ai_status"], "failed")
        self.assertEqual(comparison["ai_error_label"], "Gemini sedang sibuk (503)")
        self.assertIsNone(comparison["feedback"][0]["still_present"])

    def test_reanalyze_missing_file(self):
        self._login(self.admin)
        Document.objects.filter(pk=self.doc_a.pk).update(file="documents/tidak-ada.docx")
        response = self.client.post(f"/api/v1/admin/documents/{self.doc_a.pk}/reanalyze/")
        self.assertEqual(response.status_code, 409)

    # ---------- Upload mahasiswa ikut tercatat ----------

    @mock.patch("apps.documents.pipeline.run_jalur_b")
    @mock.patch("apps.documents.pipeline.run_jalur_a")
    def test_upload_records_ai_run(self, jalur_a, jalur_b):
        jalur_a.return_value = {"parsed_document": {}, "findings": [], "summary": {}}
        jalur_b.return_value = {
            "findings": [{"category": "sitasi", "issue": "OK", "status": "passed"}],
            "summary": {}, "error": None, "error_type": "", "model": "gemini-3.8-flash",
            "duration_ms": 900, "unknown_categories": [],
        }
        self._login(self.student)
        response = self.client.post(
            "/api/v1/documents/upload/",
            {"title": "baru.docx", "document_type": "pkl",
             "file": SimpleUploadedFile("baru.docx", b"isi")},
            format="multipart",
        )
        self.assertEqual(response.status_code, 201, response.data)
        run = AIRun.objects.get(document_id=response.data["document"]["id"])
        self.assertEqual((run.trigger, run.status, run.model), ("upload", "success", "gemini-3.8-flash"))


class PedomanPolinelaRulesTests(APITestCase):
    """Aturan hasil migration 0005 (Pedoman Penulisan Polinela 2018)."""

    def test_physical_rules_body_scope_and_margin(self):
        margin = MasterRule.objects.get(category="physical", rule_key="margin")
        self.assertEqual(
            margin.rule_value["value"],
            {"top_margin": 3, "right_margin": 3, "bottom_margin": 3, "left_margin": 4},
        )

    def test_chapter_structure_per_document_type(self):
        def hierarki(document_type):
            aspects = MasterRule.semantic_aspects(document_type)
            return next(a["instruction"] for a in aspects if a["key"] == "hierarki_bab")

        self.assertIn("KEADAAN UMUM", hierarki("pkl"))
        self.assertIn("TUJUAN PRAKTIKUM", hierarki("praktik"))
        self.assertIn("RENCANA ANGGARAN BIAYA", hierarki("proposal_penelitian"))
        self.assertIn("Analisis Situasi", hierarki("proposal_pengabdian"))
        self.assertIn("METODOLOGI", hierarki("makalah_ilmiah"))
        self.assertIn("TINJAUAN PUSTAKA", hierarki("tugas_akhir"))
        # Aspek lain tetap memakai aturan umum.
        self.assertEqual(len(MasterRule.semantic_aspects("pkl")), 7)


class PhysicalCheckerTests(SimpleTestCase):
    """Pemeriksa format hanya menilai teks isi (Pedoman 1.4)."""

    BODY = "Ini adalah kalimat teks isi yang cukup panjang untuk diperiksa formatnya."

    def _paragraph(self, text, size=12, alignment="JUSTIFY", spacing=1.5, bold=False, style="Normal"):
        return {
            "text": text, "style": style, "alignment": alignment, "line_spacing": spacing,
            "runs": [{"text": text, "font_name": "Times New Roman", "font_size": size, "bold": bold}],
        }

    def _check(self, paragraphs, rules, sections=None):
        from apps.documents.checker.physical_checker import check_physical_rules
        document = {"paragraphs": paragraphs, "sections": sections or []}
        return {f["rule_key"]: f for f in check_physical_rules(document, rules)}

    def test_headings_captions_and_abstract_are_not_body(self):
        paragraphs = [
            self._paragraph("I. PENDAHULUAN", size=14, alignment="CENTER", spacing=1.0, bold=True),
            self._paragraph(self.BODY),
            self._paragraph("1.1 Latar Belakang", bold=True, alignment="LEFT", spacing=1.0),
            self._paragraph(self.BODY),
            self._paragraph("Tabel 1. Hasil analisis kandungan unsur hara pada tanah percobaan",
                            size=10, alignment="CENTER", spacing=1.0),
            self._paragraph("ABSTRAK", bold=True, alignment="CENTER"),
            self._paragraph(self.BODY, spacing=1.0),  # abstrak memang spasi 1
            self._paragraph("Judul Bab Memakai Style Heading", size=14, alignment="CENTER",
                            spacing=1.0, style="Heading 1"),
            self._paragraph(self.BODY),
        ]
        rules = {"font_size": {"value": 12}, "alignment": {"value": "JUSTIFY"},
                 "line_spacing": {"value": 1.5}}
        result = self._check(paragraphs, rules)
        self.assertEqual({k: v["status"] for k, v in result.items()},
                         {"font_size": "passed", "alignment": "passed", "line_spacing": "passed"})

        # Cara lama (semua paragraf) menilai judul & tabel sebagai salah.
        old = {k: {**v, "scope": "all"} for k, v in rules.items()}
        self.assertEqual(self._check(paragraphs, old)["font_size"]["status"], "failed")

    def test_real_body_errors_still_detected(self):
        paragraphs = [self._paragraph(self.BODY, size=11, alignment="LEFT", spacing=1.15)]
        rules = {"font_size": {"value": 12}, "alignment": {"value": "JUSTIFY"},
                 "line_spacing": {"value": 1.5}}
        result = self._check(paragraphs, rules)
        self.assertTrue(all(f["status"] == "failed" for f in result.values()))
        self.assertTrue(result["font_size"]["message"].startswith("Teks isi:"))

    def test_cover_page_is_not_body(self):
        # Judul sampul panjang (>15 kata) dan baris "Salah satu syarat..." di sampul.
        cover_title = ("RANCANG BANGUN PROTOTIPE SISTEM MANAJEMEN BANDWIDTH BERBASIS MIKROTIK "
                       "UNTUK MENINGKATKAN KUALITAS LAYANAN JARINGAN INTERNET DI LINGKUNGAN KAMPUS")
        paragraphs = [
            self._paragraph(cover_title, size=14, alignment="CENTER", spacing=1.0, bold=True),
            self._paragraph("Salah Satu Syarat tugas mata kuliah Penulisan Karya Ilmiah",
                            size=14, alignment="CENTER", spacing=1.0),
            self._paragraph("KATA PENGANTAR", size=14, alignment="CENTER", bold=True),
            self._paragraph("BAB I PENDAHULUAN", size=14, alignment="CENTER", bold=True),
            self._paragraph(self.BODY),
        ]
        rules = {"font_size": {"value": 12}, "alignment": {"value": "JUSTIFY"},
                 "line_spacing": {"value": 1.5}}
        result = self._check(paragraphs, rules)
        self.assertEqual({k: v["status"] for k, v in result.items()},
                         {"font_size": "passed", "alignment": "passed", "line_spacing": "passed"})

    def test_document_without_known_sections_is_still_checked(self):
        paragraphs = [self._paragraph(self.BODY, size=11)]
        result = self._check(paragraphs, {"font_size": {"value": 12}})
        self.assertEqual(result["font_size"]["status"], "failed")

    def test_exact_line_spacing_length_is_ignored(self):
        # Spasi "exact" dari Word berupa panjang absolut (mis. 16510), bukan 1,5.
        paragraphs = [self._paragraph(self.BODY, spacing=16510), self._paragraph(self.BODY)]
        result = self._check(paragraphs, {"line_spacing": {"value": 1.5}})
        self.assertEqual(result["line_spacing"]["status"], "passed")

    def test_margin_message_is_readable(self):
        rules = {"margin": {"value": {"top_margin": 3, "right_margin": 3,
                                      "bottom_margin": 3, "left_margin": 4}}}
        sections = [{"top_margin": 2.54, "bottom_margin": 3, "left_margin": 4, "right_margin": 3}]
        result = self._check([], rules, sections)["margin"]
        self.assertEqual(result["status"], "failed")
        self.assertIn("atas 2,54 cm, seharusnya 3 cm", result["message"])


class ScoringHelpersTests(SimpleTestCase):

    def test_normalize_category(self):
        self.assertEqual(normalize_category("abstrak"), "abstrak")
        self.assertEqual(normalize_category("Abstract"), "abstrak")
        self.assertEqual(normalize_category("Sitasi & Kepustakaan"), "sitasi")
        self.assertEqual(normalize_category("hierarki-urutan bab"), "hierarki_bab")
        self.assertEqual(normalize_category("tidak dikenal"), "")
        self.assertEqual(normalize_category(None), "")
        self.assertEqual(
            normalize_semantic([{"category": "Konsistensi Istilah Teknis", "status": "failed"}])[0]["title"],
            "Konsistensi istilah teknis",
        )

    def test_prompt_lists_only_given_aspects(self):
        prompt = build_semantic_prompt("teks", "PKL", DEFAULT_ASPECTS[:2])
        self.assertIn('"sitasi" / "daftar_isi"', prompt)
        self.assertNotIn("ABSTRAK", prompt)
        self.assertIn("ABSTRAK", build_semantic_prompt("teks"))
