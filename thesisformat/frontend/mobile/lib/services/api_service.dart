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

  /// Mengunggah dokumen ke backend Django.
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

    final backendType = switch (documentType) {
      'skripsi' || 'thesis' => 'skripsi',
      'proposal' => 'proposal',
      _ => 'laporan',
    };

    final request = http.MultipartRequest(
      'POST',
      Uri.parse('$baseUrl/api/v1/documents/upload/'),
    );

    request.headers['Authorization'] = 'Bearer $token';
    request.fields['title'] = fileName;
    request.fields['document_type'] = backendType;

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

    final jalurA = data['jalur_a'] is Map
        ? Map<String, dynamic>.from(data['jalur_a'] as Map)
        : <String, dynamic>{};

    final summaryA = jalurA['summary'] is Map
        ? Map<String, dynamic>.from(jalurA['summary'] as Map)
        : <String, dynamic>{};

    final jalurB = data['jalur_b'] is Map
        ? Map<String, dynamic>.from(data['jalur_b'] as Map)
        : <String, dynamic>{};

    final summaryB = jalurB['summary'] is Map
        ? Map<String, dynamic>.from(jalurB['summary'] as Map)
        : <String, dynamic>{};

    return DocumentModel(
      id: int.tryParse('${rawDocument['id'] ?? ''}'),
      fileName:
          '${rawDocument['title'] ?? rawDocument['file_name'] ?? fileName}',
      documentType: '${rawDocument['document_type'] ?? backendType}',
      uploadDate:
          '${rawDocument['uploaded_at'] ?? DateTime.now().toIso8601String()}',
      status: '${rawDocument['status'] ?? 'uploaded'}',
      sizeBytes: bytes.length,
      findingsCount:
          ((summaryA['total'] as num?)?.toInt() ?? 0) +
          ((summaryB['total'] as num?)?.toInt() ?? 0),
    );
  }

  /// Mengambil hasil pemeriksaan.
  /// Belum terhubung ke endpoint detail hasil Django.
  Future<AuditResult> getDocumentResult(int documentId) async {
    return AuditResult.demo;
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

    // DEBUG: periksa respons yang dikirim Django.
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
