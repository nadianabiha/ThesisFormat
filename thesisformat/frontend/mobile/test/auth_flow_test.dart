import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:aplikasi_mobile/main.dart';

void main() {
  testWidgets('Login and register forms are reachable', (tester) async {
    await tester.pumpWidget(const ThesisFormatApp());

    expect(find.text('Welcome back'), findsOneWidget);
    expect(find.byType(TextFormField), findsNWidgets(2));

    final signUpLink = find.text('Sign up').first;
    await tester.ensureVisible(signUpLink);
    await tester.tap(signUpLink);
    await tester.pumpAndSettle();

    expect(find.text('Create an account'), findsOneWidget);
    expect(find.byType(TextFormField), findsNWidgets(4));

    final signInLink = find.text('Sign in').last;
    await tester.ensureVisible(signInLink);
    await tester.pumpAndSettle();
    await tester.tap(signInLink);
    await tester.pumpAndSettle();
    expect(find.text('Welcome back'), findsOneWidget);
  });
}