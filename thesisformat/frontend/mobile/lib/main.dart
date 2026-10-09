import 'package:flutter/material.dart';
import 'theme/app_theme.dart';
import 'screens/login_screen.dart';

void main() => runApp(const ThesisFormatApp());

class ThesisFormatApp extends StatelessWidget {
  const ThesisFormatApp({super.key});

  @override
  Widget build(BuildContext context) => MaterialApp(
    title: 'ThesisFormat',
    debugShowCheckedModeBanner: false,
    theme: AppTheme.light,
    home: const LoginScreen(),
  );
}
