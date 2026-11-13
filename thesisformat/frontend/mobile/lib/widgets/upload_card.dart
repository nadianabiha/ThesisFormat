import 'package:file_picker/file_picker.dart';
import 'package:flutter/material.dart';

import '../theme/app_theme.dart';
import 'ui_kit.dart';

class UploadCard extends StatelessWidget {
  const UploadCard({
    super.key,
    required this.file,
    required this.onPick,
    required this.onRemove,
  });

  final PlatformFile? file;
  final VoidCallback onPick;
  final VoidCallback onRemove;

  String _size(int bytes) => bytes < 1024 * 1024
      ? '${(bytes / 1024).toStringAsFixed(0)} KB'
      : '${(bytes / (1024 * 1024)).toStringAsFixed(1)} MB';

  @override
  Widget build(BuildContext context) {
    final c = context.appColors;

    if (file == null) {
      return SoftCard(
        onTap: onPick,
        color: c.primarySoft,
        borderColor: c.primaryLight,
        padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 24),
        child: Column(
          children: [
            Container(
              width: 60,
              height: 60,
              decoration: BoxDecoration(color: c.card, shape: BoxShape.circle),
              child: Icon(
                Icons.cloud_upload_rounded,
                color: c.primaryDark,
                size: 30,
              ),
            ),
            const SizedBox(height: 14),
            Text(
              'Choose a PDF or DOCX file',
              style: TextStyle(
                color: c.textPrimary,
                fontWeight: FontWeight.w700,
              ),
            ),
            const SizedBox(height: 5),
            Text(
              'Maximum 20 MB',
              style: TextStyle(color: c.textSecondary, fontSize: 12),
            ),
            const SizedBox(height: 16),
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 18, vertical: 9),
              decoration: BoxDecoration(
                color: c.card,
                borderRadius: BorderRadius.circular(30),
              ),
              child: Row(
                mainAxisSize: MainAxisSize.min,
                children: [
                  Icon(
                    Icons.attach_file_rounded,
                    size: 17,
                    color: c.primaryDark,
                  ),
                  const SizedBox(width: 6),
                  Text(
                    'Choose file',
                    style: TextStyle(
                      color: c.primaryExtraDark,
                      fontWeight: FontWeight.w700,
                      fontSize: 13,
                    ),
                  ),
                ],
              ),
            ),
          ],
        ),
      );
    }

    final ext = (file!.extension ?? '').toUpperCase();

    return SoftCard(
      padding: const EdgeInsets.fromLTRB(14, 12, 6, 12),
      child: Row(
        children: [
          Container(
            width: 46,
            height: 46,
            decoration: BoxDecoration(
              color: ext == 'PDF' ? c.errorBackground : c.primarySoft,
              borderRadius: BorderRadius.circular(14),
            ),
            alignment: Alignment.center,
            child: Text(
              ext,
              style: TextStyle(
                color: ext == 'PDF' ? c.error : c.primaryDark,
                fontWeight: FontWeight.w800,
                fontSize: 11,
              ),
            ),
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  file!.name,
                  maxLines: 1,
                  overflow: TextOverflow.ellipsis,
                  style: TextStyle(
                    color: c.textPrimary,
                    fontWeight: FontWeight.w700,
                  ),
                ),
                const SizedBox(height: 4),
                Row(
                  children: [
                    Icon(
                      Icons.check_circle_rounded,
                      size: 13,
                      color: c.success,
                    ),
                    const SizedBox(width: 4),
                    Text(
                      'Ready · ${_size(file!.size)}',
                      style: TextStyle(color: c.textSecondary, fontSize: 11.5),
                    ),
                  ],
                ),
              ],
            ),
          ),
          IconButton(
            tooltip: 'Replace file',
            onPressed: onPick,
            icon: const Icon(Icons.swap_horiz_rounded),
          ),
          IconButton(
            tooltip: 'Remove file',
            onPressed: onRemove,
            icon: const Icon(Icons.close_rounded),
          ),
        ],
      ),
    );
  }
}
