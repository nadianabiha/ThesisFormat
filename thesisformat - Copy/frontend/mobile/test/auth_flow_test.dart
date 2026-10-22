import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:aplikasi_mobile/main.dart';

Future<void> registerAccount(WidgetTester tester, {
  required String name,
  required String email,
  required String password,
}) async {
  await tester.ensureVisible(find.text('Sign up').first);
  await tester.tap(find.text('Sign up').first);
  await tester.pumpAndSettle();
  final fields = find.byType(TextFormField);
  await tester.enterText(fields.at(0), name);
  await tester.enterText(fields.at(1), email);
  await tester.enterText(fields.at(2), password);
  await tester.enterText(fields.at(3), password);
  await tester.ensureVisible(find.widgetWithText(ElevatedButton, 'Sign up'));
  await tester.tap(find.widgetWithText(ElevatedButton, 'Sign up'));
  await tester.pumpAndSettle();
}

Future<void> login(WidgetTester tester, String password) async {
  final fields = find.byType(TextFormField);
  await tester.enterText(fields.at(1), password);
  await tester.tap(find.widgetWithText(ElevatedButton, 'Sign in'));
  await tester.pumpAndSettle();
}

void main() {
  testWidgets('registered users get their own Home and Profile session', (tester) async {
    await tester.pumpWidget(const ThesisFormatApp());

    await registerAccount(tester, name: 'Nadia Nabiha Dziqra', email: 'nadia@gmail.com', password: 'rahasia1');
    expect(find.text('nadia@gmail.com'), findsOneWidget);
    await login(tester, 'rahasia1');

    expect(find.text('Welcome, Nadia'), findsOneWidget);
    await tester.tap(find.byIcon(Icons.person_outline_rounded));
    await tester.pumpAndSettle();
    expect(find.text('Nadia Nabiha Dziqra'), findsOneWidget);
    expect(find.text('nadia@gmail.com'), findsOneWidget);
    expect(find.text('N'), findsOneWidget);

    await tester.ensureVisible(find.widgetWithText(OutlinedButton, 'Sign out'));
    await tester.tap(find.widgetWithText(OutlinedButton, 'Sign out'));
    await tester.pumpAndSettle();
    expect(find.text('Welcome back'), findsOneWidget);

    await registerAccount(tester, name: 'Aisyah Putri', email: 'aisyah@gmail.com', password: 'rahasia2');
    await login(tester, 'rahasia2');
    expect(find.text('Welcome, Aisyah'), findsOneWidget);
  });
}
