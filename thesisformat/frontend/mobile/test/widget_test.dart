import 'package:flutter_test/flutter_test.dart';
import 'package:aplikasi_mobile/main.dart';

void main() {
  testWidgets('Login screen is shown on launch', (tester) async {
    await tester.pumpWidget(const ThesisFormatApp());
    expect(find.text('ThesisFormat'), findsOneWidget);
    expect(find.text('Sign in'), findsOneWidget);
  });
}
