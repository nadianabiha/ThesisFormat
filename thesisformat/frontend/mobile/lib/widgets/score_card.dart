import 'package:flutter/material.dart';

import '../theme/app_theme.dart';
import 'ui_kit.dart';

/// Kartu skor kecil (aspek fisik / semantik).
/// [score] null berarti skor belum tersedia.
class ScoreCard extends StatelessWidget {
  const ScoreCard({
    super.key,
    required this.title,
    required this.score,
    this.icon = Icons.insights_rounded,
    this.color,
    this.weight,
  });

  final String title;
  final int? score;
  final IconData icon;
  final Color? color;

  /// Bobot dalam skor akhir, mis. "40%".
  final String? weight;

  @override
  Widget build(BuildContext context) {
    final c = context.appColors;
    final accent = color ?? c.primaryDark;
    final value = score?.clamp(0, 100);

    return SoftCard(
      padding: const EdgeInsets.all(14),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Container(
                width: 32,
                height: 32,
                decoration: BoxDecoration(
                  color: accent.withValues(alpha: c.isDark ? .2 : .12),
                  borderRadius: BorderRadius.circular(10),
                ),
                child: Icon(icon, color: accent, size: 18),
              ),
              const Spacer(),
              if (weight != null)
                Text(
                  weight!,
                  style: TextStyle(
                    color: c.textMuted,
                    fontSize: 11,
                    fontWeight: FontWeight.w600,
                  ),
                ),
            ],
          ),
          const SizedBox(height: 12),
          Text(
            title,
            maxLines: 1,
            overflow: TextOverflow.ellipsis,
            style: TextStyle(color: c.textSecondary, fontSize: 12),
          ),
          const SizedBox(height: 4),
          Text.rich(
            TextSpan(
              children: [
                TextSpan(
                  text: value == null ? '—' : '$value',
                  style: TextStyle(
                    color: c.textPrimary,
                    fontWeight: FontWeight.w800,
                    fontSize: 22,
                  ),
                ),
                if (value != null)
                  TextSpan(
                    text: ' /100',
                    style: TextStyle(color: c.textMuted, fontSize: 11),
                  ),
              ],
            ),
          ),
          const SizedBox(height: 10),
          if (value == null)
            Text(
              'Skor belum tersedia',
              style: TextStyle(color: c.textMuted, fontSize: 11),
            )
          else
            ClipRRect(
              borderRadius: BorderRadius.circular(8),
              child: LinearProgressIndicator(
                value: value / 100,
                minHeight: 6,
                color: accent,
                backgroundColor: c.surfaceSecondary,
              ),
            ),
        ],
      ),
    );
  }
}
