import 'dart:convert';

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;
import 'package:http/testing.dart';

import 'package:aplikasi_mobile/main.dart';
import 'package:aplikasi_mobile/models/user_model.dart';
import 'package:aplikasi_mobile/services/api_service.dart';
import 'package:aplikasi_mobile/services/auth_service.dart';

const _user = UserModel(id: '1', name: 'Siti', email: 'siti@test.id');

http.Response _json(Object body, int status) => http.Response(
      jsonEncode(body),
      status,
      headers: {'content-type': 'application/json'},
    );

/// Backend palsu: access token "lama" ditolak (401), "baru" diterima.
class FakeBackend {
  FakeBackend({this.refreshStatus = 200, this.refreshThrows = false});

  final int refreshStatus;
  final bool refreshThrows;
  int refreshCalls = 0;
  final List<String> authHeaders = [];

  Future<http.Response> handle(http.Request request) async {
    final path = request.url.path;

    if (path == '/api/token/refresh/') {
      refreshCalls++;
      // Beri jeda agar permintaan bersamaan sempat menunggu penukaran yang sama.
      await Future<void>.delayed(const Duration(milliseconds: 20));
      if (refreshThrows) throw http.ClientException('Internet putus');
      final body = jsonDecode(request.body) as Map<String, dynamic>;
      expect(body['refresh'], 'refresh-token');
      return refreshStatus == 200
          ? _json({'access': 'baru'}, 200)
          : _json({'detail': 'Token is invalid or expired'}, refreshStatus);
    }

    final auth = request.headers['Authorization'] ?? '';
    authHeaders.add(auth);
    if (auth != 'Bearer baru') {
      return _json({'detail': 'Given token not valid for any token type'}, 401);
    }

    if (path == '/api/v1/documents/history/') {
      return _json({'documents': <Object>[], 'count': 0}, 200);
    }
    if (path == '/api/v1/documents/upload/') {
      expect(request.headers['content-type'], startsWith('multipart/form-data'));
      expect(request.body, contains('isi-dokumen'));
      return _json({
        'document': {
          'id': 7,
          'title': 'a.docx',
          'file_name': 'a.docx',
          'document_type': 'pkl',
          'status': 'completed',
          'upload_date': '2026-11-13T00:00:00Z',
        },
        'result': {
          'total_score': 80,
          'format_score': 80,
          'semantic_score': 80,
          'findings': <Object>[],
        },
      }, 201);
    }
    return _json({'detail': 'Not found'}, 404);
  }
}

void main() {
  late int expiredCalls;

  setUp(() {
    expiredCalls = 0;
    AuthService.instance.logout();
    AuthService.instance.setSession(
      user: _user,
      accessToken: 'lama',
      refreshToken: 'refresh-token',
    );
    AuthService.instance.onSessionExpired = () => expiredCalls++;
  });

  Future<T> withBackend<T>(FakeBackend backend, Future<T> Function() body) {
    return http.runWithClient(body, () => MockClient(backend.handle));
  }

  test('token kedaluwarsa ditukar otomatis lalu permintaan diulang', () async {
    final backend = FakeBackend();
    final docs = await withBackend(
      backend,
      () => const ApiService().getDocumentHistory(),
    );

    expect(docs, isEmpty);
    expect(backend.refreshCalls, 1);
    expect(backend.authHeaders, ['Bearer lama', 'Bearer baru']);
    expect(AuthService.instance.accessToken, 'baru');
    expect(AuthService.instance.currentUser, isNotNull);
    expect(expiredCalls, 0);
  });

  test('beberapa permintaan bersamaan hanya menukar token sekali', () async {
    final backend = FakeBackend();
    await withBackend(backend, () {
      return Future.wait([
        const ApiService().getDocumentHistory(),
        const ApiService().getDocumentHistory(),
        const ApiService().getDocumentHistory(),
      ]);
    });

    expect(backend.refreshCalls, 1);
    expect(AuthService.instance.accessToken, 'baru');
  });

  test('upload (multipart) dikirim ulang setelah token diperbarui', () async {
    final backend = FakeBackend();
    final doc = await withBackend(
      backend,
      () => const ApiService().uploadDocument(
        fileName: 'a.docx',
        bytes: utf8.encode('isi-dokumen'),
        documentType: 'pkl',
      ),
    );

    expect(doc.id, 7);
    expect(doc.score, 80);
    expect(backend.authHeaders, ['Bearer lama', 'Bearer baru']);
  });

  test('refresh token ditolak: sesi berakhir dan pengguna dikeluarkan', () async {
    final backend = FakeBackend(refreshStatus: 401);

    await expectLater(
      withBackend(backend, () => const ApiService().getDocumentHistory()),
      throwsA(isA<SessionExpiredException>()),
    );
    expect(AuthService.instance.currentUser, isNull);
    expect(AuthService.instance.accessToken, isNull);
    expect(expiredCalls, 1);
  });

  test('beberapa permintaan gagal bersamaan hanya memicu satu kali keluar', () async {
    final backend = FakeBackend(refreshStatus: 401);
    final results = await withBackend(backend, () {
      return Future.wait([
        const ApiService().getDocumentHistory().then<Object?>((v) => v, onError: (Object e) => e),
        const ApiService().getDocumentHistory().then<Object?>((v) => v, onError: (Object e) => e),
      ]);
    });

    expect(results, everyElement(isA<SessionExpiredException>()));
    expect(backend.refreshCalls, 1);
    expect(expiredCalls, 1);
  });

  test('internet putus saat menukar token: pengguna TIDAK dikeluarkan', () async {
    final backend = FakeBackend(refreshThrows: true);

    await expectLater(
      withBackend(backend, () => const ApiService().getDocumentHistory()),
      throwsA(isA<http.ClientException>()),
    );
    expect(AuthService.instance.currentUser, isNotNull);
    expect(AuthService.instance.refreshToken, 'refresh-token');
    expect(expiredCalls, 0);
  });

  testWidgets('sesi berakhir membuka halaman Login dengan pesan', (tester) async {
    await tester.pumpWidget(const ThesisFormatApp());
    navigatorKey.currentState!.push(
      MaterialPageRoute<void>(
        builder: (_) => const Scaffold(body: Text('Halaman lain')),
      ),
    );
    await tester.pumpAndSettle();
    expect(find.text('Halaman lain'), findsOneWidget);

    AuthService.instance.expireSession();
    await tester.pumpAndSettle();

    expect(find.text('Halaman lain'), findsNothing);
    expect(find.text('Welcome back'), findsOneWidget);
    expect(find.text('Sesi login berakhir. Silakan login kembali.'), findsOneWidget);
  });
}
