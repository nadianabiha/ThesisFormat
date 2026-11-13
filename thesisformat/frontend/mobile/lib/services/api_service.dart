import 'dart:convert';

import 'package:flutter/foundation.dart';
import 'package:http/http.dart' as http;

import '../models/audit_result.dart';
import '../models/document_model.dart';
import '../models/user_model.dart';
import 'auth_service.dart';

/// API client untuk backend Django.
class ApiService {
  const ApiService();

  static const String baseUrl = String.fromEnvironment(
    'API_BASE_URL',
    defaultValue: 'http://127.0.0.1:8000',
  );

  Future<Map<String, dynamic>> login({
    required String email,
    required String password,
  }) async {
    final response = await http.post(
      Uri.parse('$baseUrl/api/token/'),
      headers: const {'Content-Type': 'application/json'},
      body: jsonEncode({
        'username': email.trim().toLowerCase(),
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
    required String name,
    required String email,
    required String password,
  }) async {
    final response = await http.post(
      Uri.parse('$baseUrl/api/users/register/'),
      headers: const {'Content-Type': 'application/json'},
      body: jsonEncode({
        'name': name.trim(),
        'email': email.trim().toLowerCase(),
        'password': password,
      }),
    );

    final data = _decodeResponse(response);

    return {
      'id': (data['id'] ?? '').toString(),
      'name': (data['name'] ?? name.trim()).toString(),
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

    final request = http.MultipartRequest(
      'POST',
      Uri.parse('$baseUrl/api/v1/documents/upload/'),
    );

    request.headers['Authorization'] = 'Bearer $token';
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

    final streamedResponse = await request.send();
    final response = await http.Response.fromStream(streamedResponse);
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

    final response = await http.get(
      Uri.parse('$baseUrl/api/v1/documents/$documentId/result/'),
      headers: {
        'Authorization': 'Bearer $token',
        'Accept': 'application/json',
      },
    );

    return AuditResult.fromJson(_decodeResponse(response));
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

    final response = await http.get(
      uri,
      headers: {
        'Authorization': 'Bearer $token',
        'Accept': 'application/json',
      },
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
