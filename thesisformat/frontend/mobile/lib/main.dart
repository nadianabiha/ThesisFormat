import 'package:flutter/material.dart';

import 'theme/app_theme.dart';
import 'screens/login_screen.dart';
import 'services/auth_service.dart';
import 'services/theme_controller.dart';

/// Dipakai untuk berpindah halaman & menampilkan pesan dari luar widget
/// (mis. saat sesi login berakhir di tengah pemakaian).
final navigatorKey = GlobalKey<NavigatorState>();
final scaffoldMessengerKey = GlobalKey<ScaffoldMessengerState>();

/// Sesi tidak bisa diperpanjang lagi: kembali ke halaman Login.
void handleSessionExpired() {
  navigatorKey.currentState?.pushAndRemoveUntil(
    MaterialPageRoute<void>(builder: (_) => const LoginScreen()),
    (_) => false,
  );
  scaffoldMessengerKey.currentState
    ?..hideCurrentSnackBar()
    ..showSnackBar(
      const SnackBar(
        content: Text('Sesi login berakhir. Silakan login kembali.'),
      ),
    );
}

Future<void> main() async {
  WidgetsFlutterBinding.ensureInitialized();
  await ThemeController.instance.load();
  runApp(const ThesisFormatApp());
}

class ThesisFormatApp extends StatelessWidget {
  const ThesisFormatApp({super.key});

  @override
  Widget build(BuildContext context) {
    AuthService.instance.onSessionExpired = handleSessionExpired;

    return AnimatedBuilder(
      animation: ThemeController.instance,
      builder: (context, _) => MaterialApp(
        title: 'ThesisFormat',
        debugShowCheckedModeBanner: false,
        navigatorKey: navigatorKey,
        scaffoldMessengerKey: scaffoldMessengerKey,
        theme: AppTheme.lightTheme,
        darkTheme: AppTheme.darkTheme,
        themeMode: ThemeController.instance.themeMode,
        home: const LoginScreen(),
      ),
    );
  }
}
