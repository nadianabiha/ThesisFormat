import 'package:flutter/material.dart';
import '../services/api_service.dart';
import '../theme/app_theme.dart';
import 'home_screen.dart';
import 'register_screen.dart';

class LoginScreen extends StatefulWidget {
  const LoginScreen({super.key});
  @override
  State<LoginScreen> createState() => _LoginScreenState();
}

class _LoginScreenState extends State<LoginScreen> {
  final _formKey = GlobalKey<FormState>();
  final _email = TextEditingController();
  final _password = TextEditingController();
  bool _obscure = true;
  bool _submitting = false;

  @override
  void dispose() {
    _email.dispose();
    _password.dispose();
    super.dispose();
  }

  Future<void> _login() async {
    if (!_formKey.currentState!.validate() || _submitting) return;
    setState(() => _submitting = true);
    try {
      await const ApiService().login(
        email: _email.text,
        password: _password.text,
      );
      if (!mounted) return;
      ScaffoldMessenger.of(context).hideCurrentSnackBar();
      Navigator.of(context).pushReplacement(
        MaterialPageRoute<void>(builder: (_) => const HomeScreen()),
      );
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

  Future<void> _openRegister() async {
    final email = await Navigator.of(context).push<String>(MaterialPageRoute<String>(builder: (_) => const RegisterScreen()));
    if (!mounted || email == null) return;
    _email.text = email;
    ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Account created successfully. Please sign in.')));
  }

  @override
  Widget build(BuildContext context) => Scaffold(
    body: SafeArea(child: Center(child: SingleChildScrollView(
      padding: const EdgeInsets.all(24),
      child: ConstrainedBox(constraints: const BoxConstraints(maxWidth: 430), child: Form(key: _formKey, child: Column(crossAxisAlignment: CrossAxisAlignment.stretch, children: [
        Center(child: Container(width: 68, height: 68, decoration: BoxDecoration(color: context.appColors.primarySoft, borderRadius: BorderRadius.circular(22)), child: Icon(Icons.auto_stories_rounded, color: context.appColors.primaryDark, size: 34))),
        const SizedBox(height: 18),
        Text('ThesisFormat', textAlign: TextAlign.center, style: TextStyle(color: context.appColors.textPrimary, fontSize: 28, fontWeight: FontWeight.w800)),
        const SizedBox(height: 5),
        const SizedBox(height: 38),
        Text('Welcome back', style: TextStyle(color: context.appColors.textPrimary, fontSize: 22, fontWeight: FontWeight.w800)),
        const SizedBox(height: 6),
        Text('Sign in to continue reviewing your documents.', style: TextStyle(color: context.appColors.textSecondary, height: 1.5)),
        const SizedBox(height: 24),
        const Text('Email', style: TextStyle(fontWeight: FontWeight.w600, fontSize: 13)),
        const SizedBox(height: 8),
        TextFormField(controller: _email, keyboardType: TextInputType.emailAddress, decoration: const InputDecoration(hintText: 'name@example.com', prefixIcon: Icon(Icons.mail_outline_rounded)), validator: (v) => v == null || v.trim().isEmpty ? 'Email is required.' : null),
        const SizedBox(height: 17),
        const Text('Password', style: TextStyle(fontWeight: FontWeight.w600, fontSize: 13)),
        const SizedBox(height: 8),
        TextFormField(controller: _password, obscureText: _obscure, decoration: InputDecoration(hintText: 'Enter your password', prefixIcon: const Icon(Icons.lock_outline_rounded), suffixIcon: IconButton(onPressed: () => setState(() => _obscure = !_obscure), icon: Icon(_obscure ? Icons.visibility_outlined : Icons.visibility_off_outlined))), validator: (v) => v == null || v.isEmpty ? 'Password is required.' : null, onFieldSubmitted: (_) => _login()),
        Align(alignment: Alignment.centerRight, child: TextButton(onPressed: () => ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Contact your campus administrator for account support.'))), child: const Text('Forgot password?'))),
        const SizedBox(height: 12),
        ElevatedButton(onPressed: _submitting ? null : _login, child: Text(_submitting ? 'Signing in...' : 'Sign in')),
        const SizedBox(height: 18),
Text('Use the email and password registered with ThesisFormat.', textAlign: TextAlign.center, style: TextStyle(color: context.appColors.textSecondary, fontSize: 12)),
        const SizedBox(height: 14),
        Row(mainAxisAlignment: MainAxisAlignment.center, children: [
          Text('No account yet?', style: TextStyle(color: context.appColors.textSecondary, fontSize: 13)),
          TextButton(onPressed: _openRegister, child: const Text('Sign up')),
        ]),
      ]))),
    ))),
  );
}
