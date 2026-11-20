import 'package:flutter/material.dart';

import '../services/api_service.dart';
import '../theme/app_theme.dart';
import '../widgets/auth_layout.dart';
import '../widgets/responsive.dart';
import '../widgets/ui_kit.dart';
import 'edit_profile_screen.dart' show validateUsername;

class RegisterScreen extends StatefulWidget {
  const RegisterScreen({super.key});
  @override
  State<RegisterScreen> createState() => _RegisterScreenState();
}

class _RegisterScreenState extends State<RegisterScreen> {
  final _formKey = GlobalKey<FormState>();
  final _username = TextEditingController();
  final _email = TextEditingController();
  final _password = TextEditingController();
  final _confirm = TextEditingController();
  bool _hidePassword = true;
  bool _hideConfirm = true;
  bool _submitting = false;

  @override
  void dispose() {
    _username.dispose();
    _email.dispose();
    _password.dispose();
    _confirm.dispose();
    super.dispose();
  }

  Future<void> _register() async {
    if (!_formKey.currentState!.validate() || _submitting) return;
    setState(() => _submitting = true);
    try {
      await const ApiService().register(
        username: _username.text,
        email: _email.text,
        password: _password.text,
      );
      if (!mounted) return;
      // Isi otomatis kolom login dengan username yang baru dibuat.
      Navigator.of(context).pop(_username.text.trim().toLowerCase());
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
      if (mounted) setState(() => _submitting = false);
    }
  }

  Widget _toggle(bool hidden, VoidCallback onTap) => IconButton(
    onPressed: onTap,
    icon: Icon(
      hidden ? Icons.visibility_outlined : Icons.visibility_off_outlined,
    ),
  );

  @override
  Widget build(BuildContext context) {
    final c = context.appColors;
    const label = TextStyle(fontWeight: FontWeight.w600, fontSize: 13);

    // Di desktop, ilustrasi tampil di panel kiri (AuthLayout).
    final showHeader = !context.isExpanded;

    return AuthLayout(
      appBar: AppBar(),
      icon: Icons.person_add_alt_1_rounded,
      form: Form(
        key: _formKey,
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            if (showHeader) ...[
              const Center(
                child: BlobIllustration(
                  size: 130,
                  icon: Icons.person_add_alt_1_rounded,
                  badgeIcon: Icons.add_rounded,
                ),
              ),
              const SizedBox(height: 16),
            ],
            Text(
              'Create an account',
              textAlign: TextAlign.center,
              style: TextStyle(
                color: c.textPrimary,
                fontSize: 24,
                fontWeight: FontWeight.w800,
              ),
            ),
            const SizedBox(height: 6),
            Text(
              'Sign up to start organizing your academic documents.',
              textAlign: TextAlign.center,
              style: TextStyle(color: c.textSecondary),
            ),
            const SizedBox(height: 24),
            const Text('Username', style: label),
            const SizedBox(height: 7),
            TextFormField(
              controller: _username,
              autocorrect: false,
              decoration: const InputDecoration(
                hintText: 'Choose a username',
                prefixIcon: Icon(Icons.person_outline_rounded),
              ),
              validator: validateUsername,
            ),            const SizedBox(height: 14),
            const Text('Email', style: label),
            const SizedBox(height: 7),
            TextFormField(
              controller: _email,
              keyboardType: TextInputType.emailAddress,
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
            const SizedBox(height: 14),
            const Text('Password', style: label),
            const SizedBox(height: 7),
            TextFormField(
              controller: _password,
              obscureText: _hidePassword,
              decoration: InputDecoration(
                hintText: 'At least 8 characters',
                prefixIcon: const Icon(Icons.lock_outline_rounded),
                suffixIcon: _toggle(
                  _hidePassword,
                  () => setState(() => _hidePassword = !_hidePassword),
                ),
              ),
              validator: (v) => v == null || v.length < 8
                  ? 'Password must be at least 8 characters.'
                  : null,
            ),
            const SizedBox(height: 14),
            const Text('Confirm password', style: label),
            const SizedBox(height: 7),
            TextFormField(
              controller: _confirm,
              obscureText: _hideConfirm,
              decoration: InputDecoration(
                hintText: 'Re-enter your password',
                prefixIcon: const Icon(Icons.lock_outline_rounded),
                suffixIcon: _toggle(
                  _hideConfirm,
                  () => setState(() => _hideConfirm = !_hideConfirm),
                ),
              ),
              validator: (v) =>
                  v != _password.text ? 'Passwords do not match.' : null,
            ),
            const SizedBox(height: 24),
            ElevatedButton(
              onPressed: _submitting ? null : _register,
              child: Text(_submitting ? 'Creating account...' : 'Sign up'),
            ),
            const SizedBox(height: 12),
            Center(
              child: Wrap(
                alignment: WrapAlignment.center,
                crossAxisAlignment: WrapCrossAlignment.center,
                children: [
                  Text(
                    'Already have an account?',
                    style: TextStyle(color: c.textSecondary, fontSize: 13),
                  ),
                  TextButton(
                    onPressed: () => Navigator.of(context).pop(),
                    child: const Text('Sign in'),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}
