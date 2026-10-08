import 'package:flutter/material.dart';
import '../models/document_model.dart';
import '../theme/app_theme.dart';

class DocumentCard extends StatelessWidget {
  const DocumentCard({super.key, required this.document, required this.onTap});
  final DocumentModel document;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    final statusColor = document.score >= 90 ? AppColors.success : document.score >= 75 ? AppColors.info : AppColors.warning;
    final statusBackground = document.score >= 90 ? AppColors.successBackground : document.score >= 75 ? AppColors.infoBackground : AppColors.warningBackground;
    return Card(child: InkWell(
      borderRadius: BorderRadius.circular(16),
      onTap: onTap,
      child: Padding(padding: const EdgeInsets.all(15), child: Row(children: [
        Container(width: 42, height: 42, decoration: BoxDecoration(color: AppColors.primaryLight, borderRadius: BorderRadius.circular(13)), child: const Icon(Icons.description_outlined, color: AppColors.primary)),
        const SizedBox(width: 12),
        Expanded(child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
          Text(document.fileName, maxLines: 1, overflow: TextOverflow.ellipsis, style: const TextStyle(fontSize: 13, fontWeight: FontWeight.w700)),
          const SizedBox(height: 4),
          Text('${document.displayDocumentType} · ${document.uploadDate}', style: const TextStyle(color: AppColors.textSecondary, fontSize: 11)),
          const SizedBox(height: 7),
          Container(padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4), decoration: BoxDecoration(color: statusBackground, borderRadius: BorderRadius.circular(8)), child: Text(document.displayStatus, style: TextStyle(color: statusColor, fontSize: 10, fontWeight: FontWeight.w700))),
        ])),
        const SizedBox(width: 8),
        Column(crossAxisAlignment: CrossAxisAlignment.end, children: [
          Text(document.score.toString(), style: const TextStyle(color: AppColors.primary, fontSize: 21, fontWeight: FontWeight.w800)),
          const Text('SCORE', style: TextStyle(color: AppColors.textSecondary, fontSize: 9, letterSpacing: .7)),
        ]),
        const Icon(Icons.chevron_right_rounded, color: AppColors.textSecondary),
      ])),
    ));
  }
}
