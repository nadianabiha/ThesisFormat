import 'package:file_picker/file_picker.dart';
import 'package:flutter/material.dart';
import '../theme/app_theme.dart';
import 'processing_screen.dart';
import '../widgets/upload_card.dart';
import '../services/api_service.dart';

class UploadScreen extends StatefulWidget {
  const UploadScreen({super.key});
  @override
  State<UploadScreen> createState() => _UploadScreenState();
}

class _UploadScreenState extends State<UploadScreen> {
  String? _type;
  PlatformFile? _file;
  String? _error;
  bool _isUploading = false;

  String _documentTypeId(String label) => switch (label) {
    'Thesis' => 'skripsi',
    'Proposal' => 'proposal',
    'Research Paper' => 'karya_tulis_ilmiah',
    'Research Report' => 'laporan_penelitian',
    _ => label,
  };

  Future<void> _pickFile() async {
    final result = await FilePicker.platform.pickFiles(type: FileType.custom, allowedExtensions: const ['pdf', 'docx'], withData: true);
    if (!mounted || result == null || result.files.isEmpty) return;
    final file = result.files.single;
    final ext = file.extension?.toLowerCase();
    if (ext != 'pdf' && ext != 'docx') {
      setState(() => _error = 'Choose a PDF or DOCX file.');
      ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Choose a PDF or DOCX file.')));
      return;
    }
    if (file.size > 20 * 1024 * 1024) {
      setState(() => _error = 'The file exceeds the 20 MB limit.');
      ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('The maximum file size is 20 MB.')));
      return;
    }
    setState(() { _file = file; _error = null; });
  }

  @override
  Widget build(BuildContext context) => Scaffold(
    appBar: AppBar(title: const Text('Review document')),
    body: SafeArea(child: ListView(padding: const EdgeInsets.fromLTRB(20, 8, 20, 24), children: [
      Text('Choose the document you want to review.', style: TextStyle(color: context.appColors.textSecondary)),
      const SizedBox(height: 24),
      const Text('Document type', style: TextStyle(fontWeight: FontWeight.w700, fontSize: 14)),
      const SizedBox(height: 11),
      Wrap(spacing: 8, runSpacing: 7, children: ['Thesis', 'Proposal', 'Research Paper', 'Research Report'].map((type) => ChoiceChip(label: Text(type, style: TextStyle(color: _type == _documentTypeId(type) ? context.appColors.primaryExtraDark : context.appColors.textPrimary, fontWeight: FontWeight.w600)), selected: _type == _documentTypeId(type), onSelected: (_) => setState(() => _type = _documentTypeId(type)))).toList()),
      const SizedBox(height: 24),
      const Text('Document file', style: TextStyle(fontWeight: FontWeight.w700, fontSize: 14)),
      const SizedBox(height: 11),
      UploadCard(file: _file, onPick: _pickFile, onRemove: () => setState(() => _file = null)),
      if (_error != null) Padding(padding: const EdgeInsets.only(top: 10), child: Text(_error!, style: TextStyle(color: context.appColors.error, fontSize: 12))),
      const SizedBox(height: 18),
      Card(color: context.appColors.purpleSoft, child: Padding(padding: EdgeInsets.all(14), child: Row(children: [Icon(Icons.lock_outline_rounded, color: context.appColors.purple, size: 18), SizedBox(width: 9), Expanded(child: Text('Scanned documents and images are not supported yet.', style: TextStyle(color: context.appColors.textSecondary, fontSize: 12)))]))),
      const SizedBox(height: 22),
      ElevatedButton.icon(
        onPressed: _type == null || _file == null || _isUploading
            ? null
            : () async {
                final file = _file!;

                if (file.bytes == null) {
                  setState(() {
                    _error = 'File tidak dapat dibaca. Silakan pilih ulang.';
                  });
                  return;
                }

                setState(() {
                  _isUploading = true;
                  _error = null;
                });

                try {
                  final doc = await const ApiService().uploadDocument(
                    fileName: file.name,
                    bytes: file.bytes!,
                    documentType: _type!,
                  );

                  if (!context.mounted) return;

                  Navigator.of(context).push(
                    MaterialPageRoute<void>(
                      builder: (_) => ProcessingScreen(document: doc),
                    ),
                  );
                } catch (e) {
                  if (!mounted) return;

                  setState(() {
                    _error = 'Upload gagal: $e';
                  });
                } finally {
                  if (mounted) {
                    setState(() => _isUploading = false);
                  }
                }
              },
        icon: _isUploading
            ? const SizedBox(
                width: 18,
                height: 18,
                child: CircularProgressIndicator(strokeWidth: 2),
              )
            : const Icon(Icons.fact_check_outlined),
        label: Text(_isUploading ? 'Uploading...' : 'Start review'),
      ),
    ])),
  );
}
