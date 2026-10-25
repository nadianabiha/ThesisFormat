import 'package:flutter/material.dart';
import '../models/audit_result.dart';
import '../theme/app_theme.dart';

class FindingCard extends StatelessWidget {
  const FindingCard({super.key, required this.finding});
  final Finding finding;

  @override
  Widget build(BuildContext context) {
    final type = finding.type.toLowerCase();
    final color = type == 'error' ? context.appColors.error : type == 'success' ? context.appColors.success : context.appColors.warning;
    final background = type == 'error' ? context.appColors.errorBackground : type == 'success' ? context.appColors.successBackground : context.appColors.warningBackground;
    final icon = type == 'error' ? Icons.error_outline_rounded : type == 'success' ? Icons.check_circle_outline_rounded : Icons.warning_amber_rounded;
    return Card(child: Padding(padding: const EdgeInsets.all(15), child: Row(crossAxisAlignment: CrossAxisAlignment.start, children: [
      Container(width: 38, height: 38, decoration: BoxDecoration(color: background, borderRadius: BorderRadius.circular(12)), child: Icon(icon, color: color, size: 20)),
      const SizedBox(width: 11),
      Expanded(child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
        Text(type.toUpperCase(), style: TextStyle(color: color, fontWeight: FontWeight.w800, fontSize: 9, letterSpacing: .7)),
        const SizedBox(height: 4),
        Text(finding.title, style: const TextStyle(fontWeight: FontWeight.w700, fontSize: 13)),
        const SizedBox(height: 4),
        Text(finding.location, style: TextStyle(color: context.appColors.textSecondary, fontSize: 11)),
        const SizedBox(height: 7),
        Text(finding.detail, style: TextStyle(color: context.appColors.textSecondary, fontSize: 12, height: 1.4)),
      ])),
    ])));
  }
}
