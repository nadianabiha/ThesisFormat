import 'package:flutter/material.dart';

import '../services/api_service.dart';
import '../services/auth_service.dart';
import '../theme/app_theme.dart';
import '../widgets/ui_kit.dart';

final _usernamePattern = RegExp(r'^[a-zA-Z0-9_.]{3,30}$');

/// Aturan username (sama dengan backend): 3–30 karakter, huruf, angka,
/// titik, atau garis bawah. Tidak boleh memakai "@" agar tidak tertukar
/// dengan email saat login.
String? validateUsername(String? value) {
  final v = value?.trim() ?? '';
  if (v.isEmpty) return 'Username is required.';
  if (!_usernamePattern.hasMatch(v)) {
    return '3–30 characters: letters, numbers, dot, or underscore.';
  }
  return null;
}

/// Halaman ubah profil: username dan email.
class EditProfileScreen extends StatefulWidget {
  const EditProfileScreen({super.key});

  @override
  State<EditProfileScreen> createState() => _EditProfileScreenState();
}

class _EditProfileScreenState extends State<EditProfileScreen> {
  final _formKey = GlobalKey<FormState>();
  late final TextEditingController _username;
  late final TextEditingController _email;
  late final String _originalUsername;
  bool _saving = false;

  @override
  void initState() {
    super.initState();
    final user = AuthService.instance.currentUser;
    _originalUsername = user?.username ?? '';
    _username = TextEditingController(text: _originalUsername);
    _email = TextEditingController(text: user?.email ?? '');
  }

  @override
  void dispose() {
    _username.dispose();
    _email.dispose();
    super.dispose();
  }

  Future<void> _save() async {
    if (!_formKey.currentState!.validate() || _saving) return;
    setState(() => _saving = true);
    try {
      await const ApiService().updateProfile(
        username: _username.text,
        email: _email.text,
      );
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Profile updated.')),
      );
      Navigator.of(context).pop();
    } on SessionExpiredException {
      // Halaman Login dibuka otomatis (lihat main.dart).
    } on ApiException catch (error) {
      if (!mounted) return;
      ScaffoldMessenger.of(context)
          .showSnackBar(SnackBar(content: Text(error.message)));
    } catch (error) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Tidak dapat terhubung ke backend: $error')),
      );
    } finally {
      if (mounted) setState(() => _saving = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    final c = context.appColors;
    const label = TextStyle(fontWeight: FontWeight.w600, fontSize: 13);
    final initial = _username.text.trim().isEmpty
        ? '?'
        : _username.text.trim().substring(0, 1).toUpperCase();

    return Scaffold(
      appBar: AppBar(title: const Text('Edit Profile')),
      body: MobileFrame(
        maxWidth: 560,
        child: Form(
          key: _formKey,
          child: ListView(
            padding: const EdgeInsets.fromLTRB(22, 8, 22, 28),
            children: [
              Center(
                child: Container(
                  width: 84,
                  height: 84,
                  decoration: BoxDecoration(
                    gradient: c.heroGradient,
                    shape: BoxShape.circle,
                    border: Border.all(color: c.surface, width: 4),
                  ),
                  alignment: Alignment.center,
                  child: Text(
                    initial,
                    style: const TextStyle(
                      color: Colors.white,
                      fontSize: 32,
                      fontWeight: FontWeight.w800,
                    ),
                  ),
                ),
              ),
              const SizedBox(height: 22),
              SoftCard(
                padding: const EdgeInsets.all(18),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.stretch,
                  children: [
                    const Text('Username', style: label),
                    const SizedBox(height: 7),
                    TextFormField(
                      controller: _username,
                      autocorrect: false,
                      onChanged: (_) => setState(() {}),
                      decoration: const InputDecoration(
                        hintText: 'Choose a username',
                        prefixIcon: Icon(Icons.person_outline_rounded),
                      ),
                      // Akun lama memakai email sebagai username: boleh
                      // disimpan apa adanya selama tidak diubah.
                      validator: (v) =>
                          v?.trim() == _originalUsername && v!.isNotEmpty
                          ? null
                          : validateUsername(v),
                    ),
                    const SizedBox(height: 6),
                    Text(
                      'You can sign in with this username or your email.',
                      style: TextStyle(color: c.textMuted, fontSize: 12),
                    ),
                    const SizedBox(height: 14),
                    const Text('Email', style: label),
                    const SizedBox(height: 7),
                    TextFormField(
                      controller: _email,
                      keyboardType: TextInputType.emailAddress,
                      autocorrect: false,
                      decoration: const InputDecoration(
                        hintText: 'name@example.com',
                        prefixIcon: Icon(Icons.mail_outline_rounded),
                      ),
                      validator: (v) => v == null || v.trim().isEmpty
                          ? 'Email is required.'
                          : !v.contains('@')
                          ? 'Enter a valid email address.'
                          : null,
                    ),
                  ],
                ),
              ),
              const SizedBox(height: 22),
              ElevatedButton(
                onPressed: _saving ? null : _save,
                child: Text(_saving ? 'Saving...' : 'Save changes'),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
