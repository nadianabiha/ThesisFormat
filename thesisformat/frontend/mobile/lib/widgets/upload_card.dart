import 'package:flutter/material.dart';
import 'package:file_picker/file_picker.dart';
import '../theme/app_theme.dart';

class UploadCard extends StatelessWidget {
  const UploadCard({super.key, required this.file, required this.onPick, required this.onRemove});
  final PlatformFile? file;
  final VoidCallback onPick;
  final VoidCallback onRemove;

  String _size(int bytes) => bytes < 1024 * 1024
      ? '${(bytes / 1024).toStringAsFixed(0)} KB'
      : '${(bytes / (1024 * 1024)).toStringAsFixed(1)} MB';

  @override
  Widget build(BuildContext context) {
    if (file == null) {
      return Card(child: Padding(padding: const EdgeInsets.all(22), child: Column(children: [
        Container(width: 58, height: 58, decoration: BoxDecoration(color: context.appColors.primarySoft, shape: BoxShape.circle), child: Icon(Icons.cloud_upload_outlined, color: context.appColors.primaryDark, size: 29)),
        const SizedBox(height: 14),
        const Text('Choose a PDF or DOCX file', style: TextStyle(fontWeight: FontWeight.w700)),
        const SizedBox(height: 5),
        Text('Maximum 20 MB', style: TextStyle(color: context.appColors.textSecondary, fontSize: 12)),
        const SizedBox(height: 17),
        OutlinedButton.icon(onPressed: onPick, icon: const Icon(Icons.attach_file_rounded), label: const Text('Choose file')),
      ])));
    }
    return Card(child: Padding(padding: const EdgeInsets.all(14), child: Row(children: [
      Container(width: 42, height: 42, decoration: BoxDecoration(color: context.appColors.successBackground, shape: BoxShape.circle), child: Icon(Icons.check_circle_outline_rounded, color: context.appColors.success)),
      const SizedBox(width: 11),
      Expanded(child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
        Text(file!.name, maxLines: 1, overflow: TextOverflow.ellipsis, style: const TextStyle(fontWeight: FontWeight.w700)),
        const SizedBox(height: 4),
        Text('${file!.extension!.toUpperCase()} · ${_size(file!.size)}', style: TextStyle(color: context.appColors.textSecondary, fontSize: 11)),
      ])),
      IconButton(tooltip: 'Replace file', onPressed: onPick, icon: const Icon(Icons.swap_horiz_rounded)),
      IconButton(tooltip: 'Remove file', onPressed: onRemove, icon: const Icon(Icons.close_rounded)),
    ])));
  }
}
