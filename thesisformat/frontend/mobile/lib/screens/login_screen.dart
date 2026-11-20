import 'package:flutter/material.dart';

import '../services/api_service.dart';
import '../theme/app_theme.dart';
import '../widgets/auth_layout.dart';
import '../widgets/responsive.dart';
import '../widgets/ui_kit.dart';
import 'home_screen.dart';
import 'register_screen.dart';

class LoginScreen extends StatefulWidget {
  const LoginScreen({super.key});
  @override
  State<LoginScreen> createState() => _LoginScreenState();
}

class _LoginScreenState extends State<LoginScreen> {
  final _formKey = GlobalKey<FormState>();
  final _identifier = TextEditingController();
  final _password = TextEditingController();
  bool _obscure = true;
  bool _submitting = false;

  @override
  void dispose() {
    _identifier.dispose();
    _password.dispose();
    super.dispose();
  }

  Future<void> _login() async {
    if (!_formKey.currentState!.validate() || _submitting) return;
    setState(() => _submitting = true);
    try {
      await const ApiService().login(
        identifier: _identifier.text,
        password: _password.text,
      );
      if (!mounted) return;
      ScaffoldMessenger.of(context).hideCurrentSnackBar();
      Navigator.of(context).pushReplacement(
        MaterialPageRoute<void>(builder: (_) => const HomeScreen()),
      );
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

  Future<void> _openRegister() async {
    final identifier = await Navigator.of(context).push<String>(
      MaterialPageRoute<String>(builder: (_) => const RegisterScreen()),
    );
    if (!mounted || identifier == null) return;
    _identifier.text = identifier;
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(
        content: Text('Account created successfully. Please sign in.'),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final c = context.appColors;
    const label = TextStyle(fontWeight: FontWeight.w600, fontSize: 13);

    // Di desktop, logo & ilustrasi tampil di panel kiri (AuthLayout).
    final showHeader = !context.isExpanded;

    return AuthLayout(
      form: Form(
        key: _formKey,
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            if (showHeader) ...[
              const Center(child: BlobIllustration(size: 150)),
              const SizedBox(height: 6),
              Text(
                'ThesisFormat',
                textAlign: TextAlign.center,
                style: TextStyle(
                  color: c.primaryExtraDark,
                  fontSize: 17,
                  fontWeight: FontWeight.w800,
                ),
              ),
              const SizedBox(height: 18),
            ],
            Text(
              'Welcome back',
              textAlign: TextAlign.center,
              style: TextStyle(
                color: c.textPrimary,
                fontSize: 24,
                fontWeight: FontWeight.w800,
              ),
            ),
            const SizedBox(height: 6),
            Text(
              'Sign in to continue reviewing your documents.',
              textAlign: TextAlign.center,
              style: TextStyle(color: c.textSecondary, height: 1.5),
            ),
            const SizedBox(height: 26),
            const Text('Username or email', style: label),
            const SizedBox(height: 8),
            TextFormField(
              controller: _identifier,
              keyboardType: TextInputType.emailAddress,
              autocorrect: false,
              decoration: const InputDecoration(
                hintText: 'Username or email',
                prefixIcon: Icon(Icons.person_outline_rounded),
              ),
              validator: (v) => v == null || v.trim().isEmpty
                  ? 'Username or email is required.'
                  : null,
            ),
            const SizedBox(height: 16),
            const Text('Password', style: label),
            const SizedBox(height: 8),
            TextFormField(
              controller: _password,
              obscureText: _obscure,
              decoration: InputDecoration(
                hintText: 'Enter your password',
                prefixIcon: const Icon(Icons.lock_outline_rounded),
                suffixIcon: IconButton(
                  onPressed: () => setState(() => _obscure = !_obscure),
                  icon: Icon(
                    _obscure
                        ? Icons.visibility_outlined
                        : Icons.visibility_off_outlined,
                  ),
                ),
              ),
              validator: (v) =>
                  v == null || v.isEmpty ? 'Password is required.' : null,
              onFieldSubmitted: (_) => _login(),
            ),
            Align(
              alignment: Alignment.centerRight,
              child: TextButton(
                onPressed: () => ScaffoldMessenger.of(context).showSnackBar(
                  const SnackBar(
                    content: Text(
                      'Contact your campus administrator for account support.',
                    ),
                  ),
                ),
                child: const Text('Forgot password?'),
              ),
            ),
            const SizedBox(height: 8),
            ElevatedButton(
              onPressed: _submitting ? null : _login,
              child: Text(_submitting ? 'Signing in...' : 'Sign in'),
            ),
            const SizedBox(height: 18),
            Wrap(
              alignment: WrapAlignment.center,
              crossAxisAlignment: WrapCrossAlignment.center,
              children: [
                Text(
                  'No account yet?',
                  style: TextStyle(color: c.textSecondary, fontSize: 13),
                ),
                TextButton(
                  onPressed: _openRegister,
                  child: const Text('Sign up'),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }
}
