import 'package:flutter/material.dart';

import '../services/api_service.dart';
import '../theme/app_theme.dart';
import '../widgets/ui_kit.dart';

/// Halaman ganti password: password saat ini, password baru, konfirmasi.
class ChangePasswordScreen extends StatefulWidget {
  const ChangePasswordScreen({super.key});

  @override
  State<ChangePasswordScreen> createState() => _ChangePasswordScreenState();
}

class _ChangePasswordScreenState extends State<ChangePasswordScreen> {
  final _formKey = GlobalKey<FormState>();
  final _current = TextEditingController();
  final _new = TextEditingController();
  final _confirm = TextEditingController();
  bool _hideCurrent = true;
  bool _hideNew = true;
  bool _hideConfirm = true;
  bool _saving = false;

  @override
  void dispose() {
    _current.dispose();
    _new.dispose();
    _confirm.dispose();
    super.dispose();
  }

  Future<void> _save() async {
    if (!_formKey.currentState!.validate() || _saving) return;
    setState(() => _saving = true);
    try {
      await const ApiService().changePassword(
        currentPassword: _current.text,
        newPassword: _new.text,
      );
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Password changed.')),
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

  Widget _passwordField({
    required String label,
    required String hint,
    required TextEditingController controller,
    required bool hidden,
    required VoidCallback onToggle,
    required String? Function(String?) validator,
  }) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        Text(
          label,
          style: const TextStyle(fontWeight: FontWeight.w600, fontSize: 13),
        ),
        const SizedBox(height: 7),
        TextFormField(
          controller: controller,
          obscureText: hidden,
          decoration: InputDecoration(
            hintText: hint,
            prefixIcon: const Icon(Icons.lock_outline_rounded),
            suffixIcon: IconButton(
              onPressed: onToggle,
              icon: Icon(
                hidden
                    ? Icons.visibility_outlined
                    : Icons.visibility_off_outlined,
              ),
            ),
          ),
          validator: validator,
        ),
      ],
    );
  }

  @override
  Widget build(BuildContext context) {
    final c = context.appColors;

    return Scaffold(
      appBar: AppBar(title: const Text('Change Password')),
      body: MobileFrame(
        maxWidth: 560,
        child: Form(
          key: _formKey,
          child: ListView(
            padding: const EdgeInsets.fromLTRB(22, 8, 22, 28),
            children: [
              SoftCard(
                padding: const EdgeInsets.all(18),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.stretch,
                  children: [
                    _passwordField(
                      label: 'Current password',
                      hint: 'Enter your current password',
                      controller: _current,
                      hidden: _hideCurrent,
                      onToggle: () =>
                          setState(() => _hideCurrent = !_hideCurrent),
                      validator: (v) => v == null || v.isEmpty
                          ? 'Current password is required.'
                          : null,
                    ),
                    const SizedBox(height: 14),
                    _passwordField(
                      label: 'New password',
                      hint: 'At least 8 characters',
                      controller: _new,
                      hidden: _hideNew,
                      onToggle: () => setState(() => _hideNew = !_hideNew),
                      validator: (v) => v == null || v.length < 8
                          ? 'Password must be at least 8 characters.'
                          : v == _current.text
                          ? 'New password must be different.'
                          : null,
                    ),
                    const SizedBox(height: 14),
                    _passwordField(
                      label: 'Confirm new password',
                      hint: 'Re-enter your new password',
                      controller: _confirm,
                      hidden: _hideConfirm,
                      onToggle: () =>
                          setState(() => _hideConfirm = !_hideConfirm),
                      validator: (v) =>
                          v != _new.text ? 'Passwords do not match.' : null,
                    ),
                    const SizedBox(height: 10),
                    Text(
                      'Use this new password the next time you log in.',
                      style: TextStyle(color: c.textMuted, fontSize: 12),
                    ),
                  ],
                ),
              ),
              const SizedBox(height: 22),
              ElevatedButton(
                onPressed: _saving ? null : _save,
                child: Text(_saving ? 'Saving...' : 'Change password'),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
