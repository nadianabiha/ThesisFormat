import 'package:flutter/foundation.dart';

import '../models/user_model.dart';

/// Menyimpan sesi pengguna yang telah diautentikasi oleh Django.
/// Akun dan password tidak disimpan di Flutter; akun tersimpan di PostgreSQL.
class AuthService extends ChangeNotifier {
  AuthService._();

  static final AuthService instance = AuthService._();

  UserModel? _currentUser;
  String? _accessToken;
  String? _refreshToken;

  UserModel? get currentUser => _currentUser;
  String? get accessToken => _accessToken;
  String? get refreshToken => _refreshToken;
  bool get isLoggedIn => _currentUser != null && _accessToken != null;

  void setSession({
    required UserModel user,
    required String accessToken,
    String? refreshToken,
  }) {
    _currentUser = user;
    _accessToken = accessToken;
    _refreshToken = refreshToken;
    notifyListeners();
  }

  /// Ganti access token yang kedaluwarsa dengan token baru dari
  /// /api/token/refresh/. Tidak memanggil notifyListeners karena
  /// data pengguna tidak berubah (layar tidak perlu dibangun ulang).
  void updateAccessToken(String accessToken, {String? refreshToken}) {
    _accessToken = accessToken;
    if (refreshToken != null && refreshToken.isNotEmpty) {
      _refreshToken = refreshToken;
    }
  }

  /// Dipanggil (sekali) saat sesi tidak bisa diperpanjang lagi.
  /// Diisi di main.dart untuk membuka halaman Login.
  VoidCallback? onSessionExpired;

  /// Sesi berakhir: hapus data login lalu beri tahu aplikasi.
  void expireSession() {
    // Abaikan jika sudah logout (mis. beberapa permintaan gagal bersamaan).
    if (_accessToken == null && _currentUser == null) return;
    logout();
    onSessionExpired?.call();
  }

  void logout() {
    _currentUser = null;
    _accessToken = null;
    _refreshToken = null;
    notifyListeners();
  }
}
