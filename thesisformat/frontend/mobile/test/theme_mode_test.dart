import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:shared_preferences/shared_preferences.dart';

import 'package:aplikasi_mobile/screens/profile_screen.dart';
import 'package:aplikasi_mobile/services/theme_controller.dart';
import 'package:aplikasi_mobile/theme/app_theme.dart';

Widget _themeTestApp() => AnimatedBuilder(
  animation: ThemeController.instance,
  builder: (context, _) => MaterialApp(
    theme: AppTheme.lightTheme,
    darkTheme: AppTheme.darkTheme,
    themeMode: ThemeController.instance.themeMode,
    home: const ProfileScreen(),
  ),
);

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();

  testWidgets('Profile theme switch updates and persists the selected mode', (
    tester,
  ) async {
    SharedPreferences.setMockInitialValues({});
    await ThemeController.instance.load();

    await tester.pumpWidget(_themeTestApp());

    expect(find.text('Light Mode'), findsOneWidget);
    expect(
      tester.widget<MaterialApp>(find.byType(MaterialApp)).themeMode,
      ThemeMode.light,
    );

    await tester.tap(find.byType(SwitchListTile));
    await tester.pumpAndSettle();

    expect(find.text('Dark Mode'), findsOneWidget);
    expect(
      tester.widget<MaterialApp>(find.byType(MaterialApp)).themeMode,
      ThemeMode.dark,
    );
    var preferences = await SharedPreferences.getInstance();
    expect(preferences.getString('theme_mode'), 'dark');

    await ThemeController.instance.load();
    expect(ThemeController.instance.themeMode, ThemeMode.dark);

    await tester.tap(find.byType(SwitchListTile));
    await tester.pumpAndSettle();
    expect(find.text('Light Mode'), findsOneWidget);

    preferences = await SharedPreferences.getInstance();
    expect(preferences.getString('theme_mode'), 'light');
  });
}