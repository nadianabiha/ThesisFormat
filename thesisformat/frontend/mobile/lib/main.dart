import 'package:flutter/material.dart';

import 'theme/app_theme.dart';
import 'screens/login_screen.dart';
import 'services/theme_controller.dart';

Future<void> main() async {
  WidgetsFlutterBinding.ensureInitialized();
  await ThemeController.instance.load();
  runApp(const ThesisFormatApp());
}

class ThesisFormatApp extends StatelessWidget {
  const ThesisFormatApp({super.key});

  @override
  Widget build(BuildContext context) => AnimatedBuilder(
    animation: ThemeController.instance,
    builder: (context, _) => MaterialApp(
      title: 'ThesisFormat',
      debugShowCheckedModeBanner: false,
      theme: AppTheme.lightTheme,
      darkTheme: AppTheme.darkTheme,
      themeMode: ThemeController.instance.themeMode,
      home: const LoginScreen(),
    ),
  );
}
