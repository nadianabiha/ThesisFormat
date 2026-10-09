import 'package:flutter/foundation.dart';
import '../models/user_model.dart';

/// In-memory mock authentication. Accounts and the active session reset on app restart.
class AuthService extends ChangeNotifier {
  AuthService._();

  static final AuthService instance = AuthService._();

  final Map<String, _MockAccount> _accounts = {};
  int _nextId = 1;
  UserModel? _currentUser;

  UserModel? get currentUser => _currentUser;
  bool get isLoggedIn => _currentUser != null;

  UserModel register({
    required String name,
    required String email,
    required String password,
  }) {
    final normalizedEmail = email.trim().toLowerCase();
    if (_accounts.containsKey(normalizedEmail)) {
      throw const AuthException('This email is already registered.');
    }
    final user = UserModel(
      id: (_nextId++).toString(),
      name: name.trim(),
      email: email.trim(),
    );
    _accounts[normalizedEmail] = _MockAccount(user: user, password: password);
    return user;
  }

  UserModel login({required String email, required String password}) {
    final account = _accounts[email.trim().toLowerCase()];
    if (account == null || account.password != password) {
      throw const AuthException('The email or password does not match a registered account.');
    }
    _currentUser = account.user;
    notifyListeners();
    return account.user;
  }

  void logout() {
    _currentUser = null;
    notifyListeners();
  }

  // TODO: Ganti mock user dengan data user dari Django REST API.
  // TODO: Simpan JWT access token ketika backend Person 1 tersedia.
  // TODO: Ambil user profile dari response login atau endpoint profile.
}

class _MockAccount {
  const _MockAccount({required this.user, required this.password});
  final UserModel user;
  final String password;
}

class AuthException implements Exception {
  const AuthException(this.message);
  final String message;

  @override
  String toString() => message;
}
