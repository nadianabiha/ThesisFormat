import 'package:flutter/material.dart';

import '../theme/app_theme.dart';
import 'responsive.dart';
import 'ui_kit.dart';

/// Tata letak halaman Login/Register.
/// - HP & tablet: form saja di tengah.
/// - Desktop: panel ilustrasi di kiri, form di kanan.
class AuthLayout extends StatelessWidget {
  const AuthLayout({
    super.key,
    required this.form,
    this.icon = Icons.verified_user_rounded,
    this.appBar,
  });

  /// Isi form. Di desktop, header (logo & ilustrasi) disembunyikan oleh
  /// halaman pemanggil karena sudah tampil di panel kiri.
  final Widget form;
  final IconData icon;
  final PreferredSizeWidget? appBar;

  @override
  Widget build(BuildContext context) {
    final formArea = Center(
      child: SingleChildScrollView(
        padding: const EdgeInsets.fromLTRB(24, 16, 24, 24),
        child: ConstrainedBox(
          constraints: const BoxConstraints(maxWidth: 430),
          child: form,
        ),
      ),
    );

    if (!context.isExpanded) {
      return Scaffold(
        appBar: appBar,
        body: SafeArea(child: formArea),
      );
    }

    return Scaffold(
      appBar: appBar,
      body: SafeArea(
        child: Row(
          children: [
            Expanded(
              child: Padding(
                padding: const EdgeInsets.all(20),
                child: _AuthPanel(icon: icon),
              ),
            ),
            Expanded(child: formArea),
          ],
        ),
      ),
    );
  }
}

class _AuthPanel extends StatelessWidget {
  const _AuthPanel({required this.icon});

  final IconData icon;

  @override
  Widget build(BuildContext context) {
    final c = context.appColors;
    const features = [
      (
        Icons.straighten_rounded,
        'Format check: font, spacing, alignment, margins',
      ),
      (Icons.psychology_alt_outlined, 'AI content review across 7 aspects'),
      (
        Icons.school_outlined,
        '6 document types from the Polinela writing guide',
      ),
    ];

    return Container(
      decoration: BoxDecoration(
        gradient: c.heroGradient,
        borderRadius: BorderRadius.circular(32),
      ),
      padding: const EdgeInsets.all(40),
      child: Center(
        child: SingleChildScrollView(
          child: ConstrainedBox(
            constraints: const BoxConstraints(maxWidth: 440),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Row(
                  children: [
                    Icon(
                      Icons.auto_stories_rounded,
                      color: Colors.white,
                      size: 24,
                    ),
                    SizedBox(width: 8),
                    Text(
                      'ThesisFormat',
                      style: TextStyle(
                        color: Colors.white,
                        fontSize: 18,
                        fontWeight: FontWeight.w800,
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 28),
                Center(
                  child: BlobIllustration(
                    size: 220,
                    icon: icon,
                    blobColor: Colors.white.withValues(alpha: .22),
                  ),
                ),
                const SizedBox(height: 28),
                const Text(
                  'Check your thesis format before your next advising session.',
                  style: TextStyle(
                    color: Colors.white,
                    fontSize: 24,
                    fontWeight: FontWeight.w800,
                    height: 1.3,
                  ),
                ),
                const SizedBox(height: 18),
                for (final (featureIcon, text) in features)
                  Padding(
                    padding: const EdgeInsets.only(bottom: 10),
                    child: Row(
                      children: [
                        Container(
                          width: 30,
                          height: 30,
                          decoration: BoxDecoration(
                            color: Colors.white.withValues(alpha: .2),
                            shape: BoxShape.circle,
                          ),
                          child: Icon(
                            featureIcon,
                            color: Colors.white,
                            size: 16,
                          ),
                        ),
                        const SizedBox(width: 10),
                        Expanded(
                          child: Text(
                            text,
                            style: TextStyle(
                              color: Colors.white.withValues(alpha: .92),
                              fontSize: 13.5,
                            ),
                          ),
                        ),
                      ],
                    ),
                  ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}
