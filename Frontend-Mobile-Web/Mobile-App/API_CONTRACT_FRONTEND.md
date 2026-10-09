# Frontend API Contract - ThesisFormat

Dokumen ini adalah kontrak kebutuhan data dari frontend Person 4, bukan implementasi backend. Endpoint disediakan Person 1 menggunakan Django REST API. Backend bertanggung jawab atas validasi, penyimpanan, parsing (Person 2), analisis (Person 3), dan skor final.

## Autentikasi

### POST /auth/login/

Request JSON: email, password.

Contoh response:

    {
      "access": "jwt_token",
      "refresh": "refresh_token",
      "user": {
        "id": 1,
        "name": "Mahasiswa",
        "email": "mahasiswa@polinela.ac.id"
      }
    }

Frontend membutuhkan access/refresh token dan profil ringkas. Untuk endpoint terlindungi, gunakan Authorization: Bearer <access>.

### POST /auth/register/

Request JSON: name, email, password. Response minimal berisi user id, name, email. Error validasi dikembalikan sebagai JSON yang bisa ditampilkan di form.

## Dokumen

### POST /documents/upload/

Request multipart/form-data dengan field file (PDF atau DOCX) dan document_type (skripsi, proposal, karya_tulis_ilmiah, laporan_penelitian).

Contoh response:

    {
      "document_id": 15,
      "file_name": "Proposal_Skripsi.docx",
      "document_type": "proposal",
      "status": "processing"
    }

### GET /documents/

Daftar dokumen milik pengguna saat ini. Frontend memerlukan id, file_name, document_type, upload_date, status, dan score.

Status yang dipakai UI: processing, completed, failed.

### GET /documents/{id}/result/

Contoh response:

    {
      "document_id": 15,
      "file_name": "Proposal_Skripsi.docx",
      "document_type": "proposal",
      "total_score": 86,
      "format_score": 92,
      "semantic_score": 82,
      "findings": [
        {
          "type": "error",
          "title": "Margin kiri belum sesuai",
          "location": "Halaman 4",
          "detail": "3.5 cm, seharusnya 4 cm"
        }
      ]
    }

Nilai findings.type: error, warning, success.

## Profil

### GET /profile/

Response JSON minimal: id, name, email.

## Kebutuhan antar-person

- Person 1: endpoint di atas, JWT, otorisasi dokumen per pengguna, format respons dan error.
- Person 2: format data parsing dan format lokasi temuan yang akan ditampilkan.
- Person 3: definisi semantic_score, jenis temuan error/warning/success, serta kesepakatan bahwa backend mengirim skor final.
- Person 4: hanya mengirim input dan menampilkan response. Tidak menghitung margin, sitasi, skor, atau menjalankan AI di Flutter.

## Django Admin

Belum diimplementasikan karena model backend belum diberikan. Setelah Person 1 menyediakan model, Person 4 dapat membantu registrasi tampilan Document, AuditResult, dan MasterRules tanpa mengubah logika backend.
