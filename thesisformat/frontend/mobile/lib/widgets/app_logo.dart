import 'package:flutter/material.dart';

/// Logo ThesisFormat: tumpukan halaman dengan kaca pembesar dan kilau AI.
/// Sumber desain: assets/images/logo.png (sama dengan ikon aplikasi).
class AppLogo extends StatelessWidget {
  const AppLogo({super.key, this.size = 40});

  final double size;

  @override
  Widget build(BuildContext context) => Image.asset(
    'assets/images/logo.png',
    width: size,
    height: size,
    filterQuality: FilterQuality.medium,
    semanticLabel: 'ThesisFormat',
  );
}
