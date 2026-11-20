import 'package:flutter/material.dart';

import '../models/audit_result.dart';
import '../theme/app_theme.dart';
import 'ui_kit.dart';

class FindingCard extends StatelessWidget {
  const FindingCard({super.key, required this.finding});

  final Finding finding;

  @override
  Widget build(BuildContext context) {
    final c = context.appColors;
    final type = finding.type.toLowerCase();
    final (color, background, icon, label) = switch (type) {
      'error' => (c.error, c.errorBackground, Icons.close_rounded, 'Error'),
      'success' => (c.success, c.successBackground, Icons.check_rounded, 'Passed'),
      _ => (c.warning, c.warningBackground, Icons.priority_high_rounded, 'Warning'),
    };
    // Temuan AI yang gagal menampilkan tingkat kesalahannya.
    final severityLabel = switch (finding.severity) {
      'ringan' => 'Minor',
      'sedang' => 'Moderate',
      'berat' => 'Major',
      _ => null,
    };
    final badge = type == 'error' && severityLabel != null
        ? '$severityLabel error'
        : label;

    return SoftCard(
      padding: const EdgeInsets.all(14),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Container(
            width: 40,
            height: 40,
            decoration: BoxDecoration(color: background, shape: BoxShape.circle),
            child: Icon(icon, color: color, size: 20),
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Expanded(
                      child: Text(
                        finding.title,
                        style: TextStyle(
                          color: c.textPrimary,
                          fontWeight: FontWeight.w700,
                          fontSize: 13.5,
                        ),
                      ),
                    ),
                    const SizedBox(width: 8),
                    Container(
                      padding: const EdgeInsets.symmetric(
                        horizontal: 8,
                        vertical: 3,
                      ),
                      decoration: BoxDecoration(
                        color: background,
                        borderRadius: BorderRadius.circular(20),
                      ),
                      child: Text(
                        badge,
                        style: TextStyle(
                          color: color,
                          fontSize: 10,
                          fontWeight: FontWeight.w700,
                        ),
                      ),
                    ),
                  ],
                ),
                if (finding.location.isNotEmpty) ...[
                  const SizedBox(height: 3),
                  Row(
                    children: [
                      Icon(Icons.place_outlined, size: 12, color: c.textMuted),
                      const SizedBox(width: 3),
                      Expanded(
                        child: Text(
                          finding.location,
                          style: TextStyle(color: c.textMuted, fontSize: 11),
                        ),
                      ),
                    ],
                  ),
                ],
                const SizedBox(height: 7),
                Text(
                  finding.detail,
                  style: TextStyle(
                    color: c.textSecondary,
                    fontSize: 12.5,
                    height: 1.45,
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}
