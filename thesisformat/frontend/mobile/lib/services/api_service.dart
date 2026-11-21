import 'dart:convert';

import 'package:flutter/foundation.dart';
import 'package:http/http.dart' as http;

import '../models/audit_result.dart';
import '../models/document_model.dart';
import '../models/user_model.dart';
import 'auth_service.dart';
import 'document_events.dart';

/// API client untuk backend Django.
class ApiService {
  const ApiService();

  /// Alamat backend. Bawaan 127.0.0.1 hanya untuk pengembangan di laptop.
  /// Saat build untuk HP/server, WAJIB diisi alamat server, contoh:
  ///   flutter build apk --dart-define=API_BASE_URL=http://103.151.63.84
  /// Tanpa ini, aplikasi di HP mencari backend di HP itu sendiri.
  static const String baseUrl = String.fromEnvironment(
    'API_BASE_URL',
    defaultValue: 'http://127.0.0.1:8000',
  );

  /// Login dengan username ATAU email ([identifier]).
  Future<Map<String, dynamic>> login({
    required String identifier,
    required String password,
  }) async {
    final response = await http.post(
      Uri.parse('$baseUrl/api/token/'),
      headers: const {'Content-Type': 'application/json'},
      body: jsonEncode({
        'username': identifier.trim(),
        'password': password,
      }),
    );

    final data = _decodeResponse(response);
    final userJson = data['user'];

    if (userJson is! Map<String, dynamic>) {
      throw const ApiException(
        'Login berhasil tetapi data pengguna tidak dikirim oleh backend.',
      );
    }

    final user = UserModel.fromJson(userJson);
    final access = data['access']?.toString();

    if (access == null || access.isEmpty) {
      throw const ApiException(
        'Token akses tidak ditemukan dari backend.',
      );
    }

    AuthService.instance.setSession(
      user: user,
      accessToken: access,
      refreshToken: data['refresh']?.toString(),
    );

    return {
      ...data,
      'user': user.toJson(),
    };
  }

  Future<Map<String, dynamic>> register({
    required String username,
    required String email,
    required String password,
  }) async {
    final response = await http.post(
      Uri.parse('$baseUrl/api/users/register/'),
      headers: const {'Content-Type': 'application/json'},
      body: jsonEncode({
        'username': username.trim().toLowerCase(),
        'email': email.trim().toLowerCase(),
        'password': password,
      }),
    );

    final data = _decodeResponse(response);

    return {
      'id': (data['id'] ?? '').toString(),
      'username': (data['username'] ?? username.trim().toLowerCase()).toString(),
      'email': (data['email'] ?? email.trim().toLowerCase()).toString(),
    };
  }

  /// Mengunggah dokumen ke backend Django dan menyimpan hasil pemeriksaan.
  Future<DocumentModel> uploadDocument({
    required String fileName,
    required List<int> bytes,
    required String documentType,
  }) async {
    final token = AuthService.instance.accessToken;

    if (token == null || token.isEmpty) {
      throw const ApiException(
        'Silakan login kembali sebelum mengunggah dokumen.',
      );
    }

    // Permintaan multipart hanya bisa dikirim sekali, jadi dibuat ulang
    // setiap kali dikirim (mis. setelah token diperbarui).
    final response = await _sendAuthorized((authHeaders) async {
      final request = http.MultipartRequest(
        'POST',
        Uri.parse('$baseUrl/api/v1/documents/upload/'),
      );

      request.headers.addAll(authHeaders);
      request.fields['title'] = fileName;
      // ID jenis dokumen sudah sama dengan backend (lihat document_type.dart).
      request.fields['document_type'] = documentType;

      request.files.add(
        http.MultipartFile.fromBytes(
          'file',
          bytes,
          filename: fileName,
        ),
      );

      return http.Response.fromStream(await request.send());
    });
    final data = _decodeResponse(response);

    final rawDocument = data['document'];

    if (rawDocument is! Map<String, dynamic>) {
      throw const ApiException(
        'Backend tidak mengirim data dokumen yang diharapkan.',
      );
    }

    // Skor dan temuan dihitung oleh backend (lihat scoring.py).
    // Flutter hanya menampilkan hasilnya.
    final rawResult = data['result'] ?? rawDocument['result'];

    if (rawResult is! Map) {
      throw const ApiException(
        'Backend tidak mengirim hasil pemeriksaan (field "result").',
      );
    }

    final result = AuditResult.fromJson(
      Map<String, dynamic>.from(rawResult),
    );

    debugPrint(
      'SKOR: total=${result.totalScore} format=${result.formatScore} '
      'semantik=${result.semanticScore} temuan=${result.findings.length}',
    );

    final document = DocumentModel.fromJson({
      ...rawDocument,
      'result': Map<String, dynamic>.from(rawResult),
      'score': result.totalScore,
      'size_bytes': bytes.length,
    });

    // Beri tahu Home dan Riwayat agar memuat ulang daftar dokumen.
    DocumentEvents.instance.documentsChanged();

    return document;
  }

  /// Mengambil hasil pemeriksaan satu dokumen dari Django.
  Future<AuditResult> getDocumentResult(int documentId) async {
    final token = AuthService.instance.accessToken;

    if (token == null || token.isEmpty) {
      throw const ApiException(
        'Silakan login kembali untuk melihat hasil dokumen.',
      );
    }

    final response = await _sendAuthorized(
      (authHeaders) => http.get(
        Uri.parse('$baseUrl/api/v1/documents/$documentId/result/'),
        headers: {...authHeaders, 'Accept': 'application/json'},
      ),
    );

    return AuditResult.fromJson(_decodeResponse(response));
  }

  /// Cek ulang dokumen yang sudah diunggah (tanpa unggah ulang).
  /// [documentType] opsional untuk mengganti jenis dokumen. Hasil lama
  /// di server ditimpa.
  Future<AuditResult> recheckDocument(
    int documentId, {
    String? documentType,
  }) async {
    final response = await _sendAuthorized(
      (authHeaders) => http
          .post(
            Uri.parse('$baseUrl/api/v1/documents/$documentId/recheck/'),
            headers: {...authHeaders, 'Content-Type': 'application/json'},
            body: jsonEncode({
              'document_type': ?documentType,
            }),
          )
          // Pemeriksaan AI bisa sampai sekitar 2,5 menit.
          .timeout(const Duration(minutes: 4)),
    );

    final result = AuditResult.fromJson(_decodeResponse(response));
    DocumentEvents.instance.documentsChanged();
    return result;
  }

  /// Mengambil riwayat dokumen dari Django.
  Future<List<DocumentModel>> getDocumentHistory() async {
    final token = AuthService.instance.accessToken;

    if (token == null || token.isEmpty) {
      debugPrint('HISTORY ERROR: Token akses tidak ditemukan.');

      throw const ApiException(
        'Silakan login kembali untuk melihat riwayat dokumen.',
      );
    }

    final uri = Uri.parse('$baseUrl/api/v1/documents/history/');

    debugPrint('HISTORY URL: $uri');

    final response = await _sendAuthorized(
      (authHeaders) => http.get(
        uri,
        headers: {...authHeaders, 'Accept': 'application/json'},
      ),
    );

    debugPrint('HISTORY STATUS: ${response.statusCode}');
    debugPrint('HISTORY BODY: ${response.body}');

    final data = _decodeResponse(response);
    final rawDocuments = data['documents'] ?? data['results'];

    if (rawDocuments is! List) {
      throw const ApiException(
        'Format data riwayat dari backend tidak sesuai.',
      );
    }

    final documents = rawDocuments
        .whereType<Map>()
        .map(
          (item) => DocumentModel.fromJson(
            Map<String, dynamic>.from(item),
          ),
        )
        .toList();

    debugPrint('HISTORY JUMLAH DOKUMEN: ${documents.length}');

    for (final document in documents) {
      debugPrint(
        'HISTORY DOCUMENT: ${document.fileName}, SCORE: ${document.score}',
      );
    }

    return documents;
  }

  Future<Map<String, dynamic>> getProfile() async {
    return AuthService.instance.currentUser?.toJson() ??
        <String, dynamic>{};
  }

  /// Simpan perubahan profil (username & email) ke backend,
  /// lalu perbarui data pengguna yang sedang login.
  Future<UserModel> updateProfile({
    required String username,
    required String email,
  }) async {
    final response = await _sendAuthorized(
      (authHeaders) => http.patch(
        Uri.parse('$baseUrl/api/users/me/'),
        headers: {...authHeaders, 'Content-Type': 'application/json'},
        body: jsonEncode({
          'username': username.trim(),
          'email': email.trim().toLowerCase(),
        }),
      ),
    );

    final user = UserModel.fromJson(_decodeResponse(response));
    AuthService.instance.updateUser(user);
    return user;
  }

  /// Ganti password akun yang sedang login.
  Future<void> changePassword({
    required String currentPassword,
    required String newPassword,
  }) async {
    final response = await _sendAuthorized(
      (authHeaders) => http.post(
        Uri.parse('$baseUrl/api/users/me/password/'),
        headers: {...authHeaders, 'Content-Type': 'application/json'},
        body: jsonEncode({
          'current_password': currentPassword,
          'new_password': newPassword,
        }),
      ),
    );
    _decodeResponse(response);
  }

  // ---------------------------------------------------------------
  // Perpanjangan sesi otomatis
  // ---------------------------------------------------------------
  // Access token berlaku 30 menit. Jika backend menjawab 401 (token
  // kedaluwarsa), minta access token baru memakai refresh token
  // (berlaku 7 hari) lalu ulangi permintaan. Pengguna tidak perlu
  // login ulang selama aplikasi masih terbuka.

  /// Penukaran token yang sedang berjalan. Dipakai bersama agar
  /// beberapa permintaan yang kedaluwarsa bersamaan hanya memicu
  /// satu kali penukaran.
  static Future<bool>? _refreshing;

  /// Kirim permintaan yang butuh login. [send] menerima header
  /// Authorization dan bisa dipanggil dua kali (sebelum & sesudah
  /// token diperbarui), jadi harus membuat permintaan baru setiap kali.
  Future<http.Response> _sendAuthorized(
    Future<http.Response> Function(Map<String, String> authHeaders) send,
  ) async {
    final token = AuthService.instance.accessToken;
    if (token == null || token.isEmpty) {
      throw const SessionExpiredException();
    }

    final response = await send({'Authorization': 'Bearer $token'});
    if (response.statusCode != 401) return response;

    // Token kedaluwarsa: tukar dengan yang baru, lalu coba sekali lagi.
    final refreshed = await _refreshAccessToken();
    final newToken = AuthService.instance.accessToken;
    if (!refreshed || newToken == null) {
      AuthService.instance.expireSession();
      throw const SessionExpiredException();
    }

    final retried = await send({'Authorization': 'Bearer $newToken'});
    if (retried.statusCode == 401) {
      AuthService.instance.expireSession();
      throw const SessionExpiredException();
    }
    return retried;
  }

  static Future<bool> _refreshAccessToken() {
    return _refreshing ??= _requestNewAccessToken().whenComplete(() {
      _refreshing = null;
    });
  }

  /// true  = token baru berhasil didapat.
  /// false = refresh token ditolak backend (sesi benar-benar berakhir).
  /// Error koneksi tidak ditangkap di sini, agar pengguna TIDAK
  /// dikeluarkan hanya karena internet sedang putus.
  static Future<bool> _requestNewAccessToken() async {
    final refresh = AuthService.instance.refreshToken;
    if (refresh == null || refresh.isEmpty) return false;

    final response = await http.post(
      Uri.parse('$baseUrl/api/token/refresh/'),
      headers: const {'Content-Type': 'application/json'},
      body: jsonEncode({'refresh': refresh}),
    );

    if (response.statusCode != 200) return false;

    final dynamic data;
    try {
      data = jsonDecode(response.body);
    } on FormatException {
      return false;
    }
    final access = data is Map ? data['access']?.toString() : null;
    if (access == null || access.isEmpty) return false;

    // Pengguna sudah logout saat penukaran berlangsung: jangan pakai token.
    if (AuthService.instance.refreshToken != refresh) return false;

    AuthService.instance.updateAccessToken(
      access,
      // Diisi backend jika ROTATE_REFRESH_TOKENS diaktifkan.
      refreshToken: data['refresh']?.toString(),
    );
    return true;
  }

  Map<String, dynamic> _decodeResponse(http.Response response) {
    dynamic decoded;

    try {
      decoded = response.body.isEmpty
          ? <String, dynamic>{}
          : jsonDecode(response.body);
    } on FormatException {
      throw ApiException(
        'Respons backend tidak valid (HTTP ${response.statusCode}).',
      );
    }

    if (response.statusCode >= 200 && response.statusCode < 300) {
      if (decoded is Map<String, dynamic>) {
        return decoded;
      }

      throw const ApiException(
        'Format respons backend tidak sesuai.',
      );
    }

    throw ApiException(
      _extractError(decoded, response.statusCode),
    );
  }

  String _extractError(dynamic body, int statusCode) {
    if (body is Map<String, dynamic>) {
      final detail = body['detail'];

      if (detail != null) {
        return detail.toString();
      }

      final messages = <String>[];

      body.forEach((key, value) {
        if (value is List) {
          messages.add('$key: ${value.join(' ')}');
        } else if (value is Map) {
          messages.add('$key: ${value.values.join(' ')}');
        } else {
          messages.add('$key: $value');
        }
      });

      if (messages.isNotEmpty) {
        return messages.join('\n');
      }
    }

    if (statusCode == 401) {
      return 'Sesi login berakhir atau token tidak valid. Silakan login kembali.';
    }

    if (statusCode == 403) {
      return 'Akses ditolak oleh backend (HTTP 403).';
    }

    return 'Permintaan gagal (HTTP $statusCode).';
  }
}

class ApiException implements Exception {
  const ApiException(this.message);

  final String message;

  @override
  String toString() => message;
}

/// Sesi login berakhir dan tidak bisa diperpanjang; pengguna
/// diarahkan ke halaman Login (lihat main.dart).
class SessionExpiredException extends ApiException {
  const SessionExpiredException()
      : super('Sesi login berakhir. Silakan login kembali.');
}
