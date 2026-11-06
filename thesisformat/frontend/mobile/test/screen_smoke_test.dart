import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';

import 'package:aplikasi_mobile/screens/home_screen.dart';
import 'package:aplikasi_mobile/theme/app_theme.dart';

void main() {
  testWidgets('Home opens History, Upload, and Profile screens', (
    tester,
  ) async {
    await tester.binding.setSurfaceSize(const Size(1100, 900));
    addTearDown(() => tester.binding.setSurfaceSize(null));

    await tester.pumpWidget(
      MaterialApp(
        theme: AppTheme.lightTheme,
        darkTheme: AppTheme.darkTheme,
        home: const HomeScreen(),
      ),
    );
    await tester.pumpAndSettle();

    expect(find.text('Welcome'), findsOneWidget);

    await tester.tap(find.text('Documents').last);
    await tester.pumpAndSettle();
    expect(find.text('Document History'), findsOneWidget);

    await tester.tap(find.text('Profile').last);
    await tester.pumpAndSettle();
    expect(find.text('Profile'), findsWidgets);
    expect(find.text('App Theme'), findsOneWidget);

    await tester.tap(find.text('Home').last);
    await tester.pumpAndSettle();
    await tester.ensureVisible(find.text('Start review'));
    await tester.tap(find.text('Start review'));
    await tester.pumpAndSettle();

    expect(find.text('Review document'), findsOneWidget);
    expect(find.text('Document type'), findsOneWidget);
  });
}