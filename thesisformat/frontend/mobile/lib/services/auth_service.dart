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

  void logout() {
    _currentUser = null;
    _accessToken = null;
    _refreshToken = null;
    notifyListeners();
  }
}
