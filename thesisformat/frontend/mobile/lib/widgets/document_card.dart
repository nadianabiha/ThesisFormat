import 'package:flutter/material.dart';

import '../models/document_model.dart';
import '../theme/app_theme.dart';
import 'ui_kit.dart';

class DocumentCard extends StatelessWidget {
  const DocumentCard({super.key, required this.document, required this.onTap});

  final DocumentModel document;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    final c = context.appColors;
    final score = document.score.clamp(0, 100);
    final completed = document.status == 'completed';

    return SoftCard(
      onTap: onTap,
      padding: const EdgeInsets.all(14),
      child: Row(
        children: [
          DocTypeIcon(type: document.documentType),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  document.fileName,
                  maxLines: 1,
                  overflow: TextOverflow.ellipsis,
                  style: TextStyle(
                    color: c.textPrimary,
                    fontSize: 14,
                    fontWeight: FontWeight.w700,
                  ),
                ),
                const SizedBox(height: 4),
                Text(
                  '${document.displayDocumentType} · ${document.uploadDate}',
                  maxLines: 1,
                  overflow: TextOverflow.ellipsis,
                  style: TextStyle(color: c.textSecondary, fontSize: 11.5),
                ),
                const SizedBox(height: 8),
                Wrap(
                  spacing: 8,
                  runSpacing: 4,
                  crossAxisAlignment: WrapCrossAlignment.center,
                  children: [
                    Container(
                      padding: const EdgeInsets.symmetric(
                        horizontal: 9,
                        vertical: 4,
                      ),
                      decoration: BoxDecoration(
                        color: completed
                            ? scoreBackground(context, score)
                            : c.surfaceSecondary,
                        borderRadius: BorderRadius.circular(20),
                      ),
                      child: Text(
                        document.displayStatus,
                        style: TextStyle(
                          color: completed
                              ? scoreColor(context, score)
                              : c.textSecondary,
                          fontSize: 10.5,
                          fontWeight: FontWeight.w700,
                        ),
                      ),
                    ),
                    if (document.findingsCount > 0)
                      Text.rich(
                        TextSpan(
                          children: [
                            WidgetSpan(
                              alignment: PlaceholderAlignment.middle,
                              child: Padding(
                                padding: const EdgeInsets.only(right: 3),
                                child: Icon(
                                  Icons.flag_outlined,
                                  size: 13,
                                  color: c.textMuted,
                                ),
                              ),
                            ),
                            TextSpan(text: '${document.findingsCount} findings'),
                          ],
                        ),
                        style: TextStyle(color: c.textMuted, fontSize: 11),
                      ),
                  ],
                ),
              ],
            ),
          ),
          const SizedBox(width: 10),
          ScoreRing(score: score, size: 50, stroke: 5, caption: null),
        ],
      ),
    );
  }
}
