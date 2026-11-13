# ThesisFormat – Web Dashboard (Admin)

Dashboard React untuk admin/staf: statistik hasil pemeriksaan, daftar dokumen,
dan review (validasi/koreksi) hasil AI. Input dokumen tetap hanya lewat
aplikasi mobile.

## Teknologi

React 18 + Vite, React Router, Chart.js (`react-chartjs-2`), ikon `lucide-react`,
CSS biasa (`src/styles/index.css`, warna disamakan dengan app mobile).

## Menjalankan (development)

1. Jalankan backend Django dan pastikan migration terbaru sudah dijalankan:
   ```
   cd backend
   python manage.py migrate
   python manage.py runserver
   ```
2. Jalankan dashboard:
   ```
   cd frontend/web
   npm install
   npm run dev
   ```
3. Buka http://localhost:5173 lalu login dengan akun **staf** (`is_staff = True`),
   misalnya akun `admin`. Akun mahasiswa akan ditolak.

Alamat backend bisa diubah lewat file `.env` (salin dari `.env.example`):

```
VITE_API_BASE_URL=http://127.0.0.1:8000
```

## Build produksi

```
npm run build      # hasil di folder dist/
npm run preview    # mencoba hasil build secara lokal
```

## Struktur

```
src/
├── api/            client.js (JWT + refresh otomatis), dashboard.js (endpoint)
├── auth/           AuthContext (status login admin)
├── components/     Layout (sidebar responsive), ProtectedRoute, ui.jsx
├── utils/          konstanta jenis dokumen, format tanggal, useAsync
├── pages/          Login, Ringkasan, Dokumen, Detail + Review
└── styles/         index.css
```

## Endpoint backend yang dipakai (khusus admin)

| Method | URL | Fungsi |
|---|---|---|
| POST | `/api/token/` | Login (respons berisi `user.is_staff`) |
| GET | `/api/v1/admin/stats/?weeks=8` | Statistik halaman Ringkasan |
| GET | `/api/v1/admin/documents/` | Daftar dokumen (`search`, `document_type`, `review_status`, `ordering`, `page`, `page_size`) |
| GET | `/api/v1/admin/documents/<id>/` | Detail dokumen + seluruh temuan |
| PATCH | `/api/v1/admin/documents/<id>/review/` | Simpan review (`review_status`, `corrected_score`, `review_note`, `rejected_findings`) |
