import 'package:file_picker/file_picker.dart';
import 'package:flutter/material.dart';

import '../models/document_type.dart';
import '../services/api_service.dart';
import '../theme/app_theme.dart';
import '../widgets/responsive.dart';
import '../widgets/ui_kit.dart';
import '../widgets/upload_card.dart';
import 'processing_screen.dart';

class UploadScreen extends StatefulWidget {
  const UploadScreen({super.key, this.initialType});

  /// Jenis dokumen yang langsung terpilih (dari kartu jenis di Home).
  final String? initialType;

  @override
  State<UploadScreen> createState() => _UploadScreenState();
}

class _UploadScreenState extends State<UploadScreen> {
  String? _type;
  PlatformFile? _file;
  String? _error;
  bool _isUploading = false;

  @override
  void initState() {
    super.initState();
    _type = widget.initialType;
  }

  Future<void> _pickFile() async {
    final result = await FilePicker.platform.pickFiles(
      type: FileType.custom,
      allowedExtensions: const ['pdf', 'docx'],
      withData: true,
    );
    if (!mounted || result == null || result.files.isEmpty) return;
    final file = result.files.single;
    final ext = file.extension?.toLowerCase();
    if (ext != 'pdf' && ext != 'docx') {
      setState(() => _error = 'Choose a PDF or DOCX file.');
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Choose a PDF or DOCX file.')),
      );
      return;
    }
    if (file.size > 20 * 1024 * 1024) {
      setState(() => _error = 'The file exceeds the 20 MB limit.');
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('The maximum file size is 20 MB.')),
      );
      return;
    }
    setState(() {
      _file = file;
      _error = null;
    });
  }

  Future<void> _submit() async {
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

      if (!mounted) return;

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
  }

  @override
  Widget build(BuildContext context) {
    final c = context.appColors;
    final ready = _type != null && _file != null && !_isUploading;
    const label = TextStyle(fontWeight: FontWeight.w800, fontSize: 15);

    final size = context.screenSize;
    final wide = size == ScreenSize.expanded;

    // Langkah 1: pilih jenis dokumen.
    final typeStep = <Widget>[
      Row(
        children: [
          const _StepBadge(number: 1),
          const SizedBox(width: 8),
          Text('Document type', style: label.copyWith(color: c.textPrimary)),
        ],
      ),
      const SizedBox(height: 12),
      GridView.builder(
        shrinkWrap: true,
        physics: const NeverScrollableScrollPhysics(),
        padding: EdgeInsets.zero,
        gridDelegate: SliverGridDelegateWithFixedCrossAxisCount(
          // Tablet: 3 kolom. HP & kolom kiri desktop: 2 kolom.
          crossAxisCount: size == ScreenSize.medium ? 3 : 2,
          mainAxisExtent: 66,
          crossAxisSpacing: 10,
          mainAxisSpacing: 10,
        ),
        itemCount: DocumentType.all.length,
        itemBuilder: (context, index) {
          final type = DocumentType.all[index];
          return _TypeTile(
            type: type,
            selected: _type == type.id,
            onTap: () => setState(() => _type = type.id),
          );
        },
      ),
    ];

    final intro = Text(
      'Choose the document type, then upload your file.',
      style: TextStyle(color: c.textSecondary, fontSize: 13),
    );

    // Langkah 2: pilih file dan mulai review.
    final fileStep = <Widget>[
      Row(
        children: [
          const _StepBadge(number: 2),
          const SizedBox(width: 8),
          Text('Document file', style: label.copyWith(color: c.textPrimary)),
        ],
      ),
      const SizedBox(height: 12),
      UploadCard(
        file: _file,
        onPick: _pickFile,
        onRemove: () => setState(() => _file = null),
      ),
      if (_error != null)
        Padding(
          padding: const EdgeInsets.only(top: 10),
          child: Text(_error!, style: TextStyle(color: c.error, fontSize: 12)),
        ),
      const SizedBox(height: 16),
      SoftCard(
        color: c.warningBackground,
        padding: const EdgeInsets.all(14),
        child: Row(
          children: [
            Icon(Icons.info_outline_rounded, color: c.warning, size: 20),
            const SizedBox(width: 10),
            Expanded(
              child: Text(
                'Scanned documents and images are not supported yet. '
                'Use DOCX for the most complete format check.',
                style: TextStyle(
                  color: c.textPrimary,
                  fontSize: 12,
                  height: 1.4,
                ),
              ),
            ),
          ],
        ),
      ),
      const SizedBox(height: 24),
      ElevatedButton.icon(
        onPressed: ready ? _submit : null,
        icon: _isUploading
            ? SizedBox(
                width: 18,
                height: 18,
                child: CircularProgressIndicator(
                  strokeWidth: 2,
                  color: c.onPrimary,
                ),
              )
            : const Icon(Icons.fact_check_outlined),
        label: Text(_isUploading ? 'Uploading...' : 'Start review'),
      ),
    ];

    return Scaffold(
      appBar: AppBar(title: const Text('Review document')),
      body: SafeArea(
        child: MobileFrame(
          maxWidth: wide ? 1100 : context.contentMaxWidth,
          child: ListView(
            padding: EdgeInsets.fromLTRB(wide ? 32 : 22, 4, wide ? 32 : 22, 24),
            children: [
              intro,
              const SizedBox(height: 20),
              if (wide)
                // Desktop: langkah 1 di kiri, langkah 2 di kanan.
                Row(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.stretch,
                        children: typeStep,
                      ),
                    ),
                    const SizedBox(width: 32),
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.stretch,
                        children: fileStep,
                      ),
                    ),
                  ],
                )
              else ...[
                ...typeStep,
                const SizedBox(height: 24),
                ...fileStep,
              ],
            ],
          ),
        ),
      ),
    );
  }
}

class _StepBadge extends StatelessWidget {
  const _StepBadge({required this.number});

  final int number;

  @override
  Widget build(BuildContext context) {
    final c = context.appColors;
    return Container(
      width: 24,
      height: 24,
      decoration: BoxDecoration(color: c.primarySoft, shape: BoxShape.circle),
      alignment: Alignment.center,
      child: Text(
        '$number',
        style: TextStyle(
          color: c.primaryExtraDark,
          fontWeight: FontWeight.w800,
          fontSize: 12,
        ),
      ),
    );
  }
}

class _TypeTile extends StatelessWidget {
  const _TypeTile({
    required this.type,
    required this.selected,
    required this.onTap,
  });

  final DocumentType type;
  final bool selected;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    final c = context.appColors;
    final style = DocTypeStyle.of(context, type.id);

    return Semantics(
      selected: selected,
      button: true,
      child: SoftCard(
        radius: 18,
        onTap: onTap,
        color: selected ? style.background(context) : null,
        borderColor: selected ? style.color : null,
        padding: const EdgeInsets.symmetric(horizontal: 10),
        child: Row(
          children: [
            DocTypeIcon(type: type.id, size: 38),
            const SizedBox(width: 10),
            Expanded(
              child: Text(
                type.label,
                maxLines: 2,
                overflow: TextOverflow.ellipsis,
                style: TextStyle(
                  color: c.textPrimary,
                  fontSize: 12,
                  fontWeight: selected ? FontWeight.w700 : FontWeight.w600,
                  height: 1.25,
                ),
              ),
            ),
            if (selected)
              Icon(Icons.check_circle_rounded, color: style.color, size: 18),
          ],
        ),
      ),
    );
  }
}
