import 'package:flutter/material.dart';
import '../theme/app_theme.dart';

class ScoreCard extends StatelessWidget {
  const ScoreCard({super.key, required this.title, required this.score});
  final String title;
  final int score;

  @override
  Widget build(BuildContext context) => Card(child: Padding(
    padding: const EdgeInsets.all(13),
    child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
      Text(title, style: TextStyle(color: context.appColors.textSecondary, fontSize: 11)),
      const SizedBox(height: 8),
      Text('$score/100', style: TextStyle(color: context.appColors.purple, fontWeight: FontWeight.w800, fontSize: 18)),
      const SizedBox(height: 8),
      ClipRRect(borderRadius: BorderRadius.circular(8), child: LinearProgressIndicator(value: score / 100, minHeight: 6, color: context.appColors.purple)),
    ]),
  ));
}
