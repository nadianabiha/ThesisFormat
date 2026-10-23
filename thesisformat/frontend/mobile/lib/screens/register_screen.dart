import 'package:flutter/material.dart';
import '../theme/app_theme.dart';
import '../services/api_service.dart';

class RegisterScreen extends StatefulWidget {
  const RegisterScreen({super.key});
  @override
  State<RegisterScreen> createState() => _RegisterScreenState();
}

class _RegisterScreenState extends State<RegisterScreen> {
  final _formKey = GlobalKey<FormState>();
  final _name = TextEditingController();
  final _email = TextEditingController();
  final _password = TextEditingController();
  final _confirm = TextEditingController();
  bool _hidePassword = true;
  bool _hideConfirm = true;
  bool _submitting = false;

  @override
  void dispose() {
    _name.dispose();
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
        name: _name.text,
        email: _email.text,
        password: _password.text,
      );
      if (!mounted) return;
      Navigator.of(context).pop(_email.text.trim());
    } on ApiException catch (error) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text(error.message)),
      );
    } catch (error) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Tidak dapat terhubung ke backend: $error')),
      );
    } finally {
      if (mounted) setState(() => _submitting = false);
    }
  }

  @override
  Widget build(BuildContext context) => Scaffold(
    appBar: AppBar(),
    body: SafeArea(child: Center(child: SingleChildScrollView(
      padding: const EdgeInsets.fromLTRB(24, 0, 24, 24),
      child: ConstrainedBox(constraints: const BoxConstraints(maxWidth: 430), child: Form(key: _formKey, child: Column(crossAxisAlignment: CrossAxisAlignment.stretch, children: [
        Center(child: Container(width: 60, height: 60, decoration: BoxDecoration(color: context.appColors.primarySoft, borderRadius: BorderRadius.circular(19)), child: Icon(Icons.person_add_alt_1_rounded, color: context.appColors.primaryDark, size: 30))),
        const SizedBox(height: 17),
        Text('Create an account', textAlign: TextAlign.center, style: TextStyle(color: context.appColors.textPrimary, fontSize: 25, fontWeight: FontWeight.w800)),
        const SizedBox(height: 6),
        Text('Sign up to start organizing your academic documents.', textAlign: TextAlign.center, style: TextStyle(color: context.appColors.textSecondary)),
        const SizedBox(height: 27),
        const Text('Full name', style: TextStyle(fontWeight: FontWeight.w600, fontSize: 13)),
        const SizedBox(height: 7),
        TextFormField(controller: _name, textCapitalization: TextCapitalization.words, decoration: const InputDecoration(hintText: 'Your name', prefixIcon: Icon(Icons.person_outline_rounded)), validator: (v) => v == null || v.trim().isEmpty ? 'Name is required.' : null),
        const SizedBox(height: 14),
        const Text('Email', style: TextStyle(fontWeight: FontWeight.w600, fontSize: 13)),
        const SizedBox(height: 7),
        TextFormField(controller: _email, keyboardType: TextInputType.emailAddress, decoration: const InputDecoration(hintText: 'name@example.com', prefixIcon: Icon(Icons.mail_outline_rounded)), validator: (v) => v == null || v.trim().isEmpty ? 'Email is required.' : !v.contains('@') ? 'Enter a valid email address.' : null),
        const SizedBox(height: 14),
        const Text('Password', style: TextStyle(fontWeight: FontWeight.w600, fontSize: 13)),
        const SizedBox(height: 7),
        TextFormField(controller: _password, obscureText: _hidePassword, decoration: InputDecoration(hintText: 'At least 6 characters', prefixIcon: const Icon(Icons.lock_outline_rounded), suffixIcon: IconButton(onPressed: () => setState(() => _hidePassword = !_hidePassword), icon: Icon(_hidePassword ? Icons.visibility_outlined : Icons.visibility_off_outlined))), validator: (v) => v == null || v.length < 8 ? 'Password must be at least 8 characters.' : null),
        const SizedBox(height: 14),
        const Text('Confirm password', style: TextStyle(fontWeight: FontWeight.w600, fontSize: 13)),
        const SizedBox(height: 7),
        TextFormField(controller: _confirm, obscureText: _hideConfirm, decoration: InputDecoration(hintText: 'Re-enter your password', prefixIcon: const Icon(Icons.lock_outline_rounded), suffixIcon: IconButton(onPressed: () => setState(() => _hideConfirm = !_hideConfirm), icon: Icon(_hideConfirm ? Icons.visibility_outlined : Icons.visibility_off_outlined))), validator: (v) => v != _password.text ? 'Passwords do not match.' : null),
        const SizedBox(height: 22),
        ElevatedButton(onPressed: _submitting ? null : _register, child: Text(_submitting ? 'Creating account...' : 'Sign up')),
        const SizedBox(height: 12),
        Center(child: Wrap(alignment: WrapAlignment.center, crossAxisAlignment: WrapCrossAlignment.center, children: [
          Text('Already have an account?', style: TextStyle(color: context.appColors.textSecondary, fontSize: 13)),
          TextButton(onPressed: () => Navigator.of(context).pop(), child: const Text('Sign in')),
        ])),
Center(child: Text('Your account will be saved securely by the backend.', textAlign: TextAlign.center, style: TextStyle(color: context.appColors.textSecondary, fontSize: 11))),
      ]))),
    ))),
  );
}
