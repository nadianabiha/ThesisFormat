import 'package:flutter/material.dart';

import '../models/document_model.dart';
import '../theme/app_theme.dart';
import '../widgets/ui_kit.dart';
import 'result_screen.dart';

class ProcessingScreen extends StatefulWidget {
  const ProcessingScreen({super.key, required this.document});
  final ThesisDocument document;
  @override
  State<ProcessingScreen> createState() => _ProcessingScreenState();
}

class _ProcessingScreenState extends State<ProcessingScreen> {
  static const _labels = [
    'Document uploaded',
    'Reading document format',
    'Reviewing structure and content',
    'Preparing the score',
    'Preparing your results',
  ];

  int _stage = 0;

  @override
  void initState() {
    super.initState();
    _run();
  }

  Future<void> _run() async {
    for (var i = 1; i <= _labels.length; i++) {
      await Future<void>.delayed(const Duration(milliseconds: 700));
      if (!mounted) return;
      setState(() => _stage = i);
    }
    if (!mounted) return;
    Navigator.of(context).pushReplacement(
      MaterialPageRoute<void>(
        builder: (_) => ResultScreen(document: widget.document),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final c = context.appColors;

    return Scaffold(
      appBar: AppBar(title: const Text('Review')),
      body: SafeArea(
        child: MobileFrame(
          maxWidth: 460,
          child: ListView(
            padding: const EdgeInsets.fromLTRB(24, 8, 24, 24),
            children: [
              const Center(
                child: BlobIllustration(
                  size: 180,
                  icon: Icons.manage_search_rounded,
                  badgeIcon: Icons.hourglass_top_rounded,
                ),
              ),
              const SizedBox(height: 20),
              Text(
                'Reviewing your document',
                textAlign: TextAlign.center,
                style: TextStyle(
                  color: c.textPrimary,
                  fontSize: 22,
                  fontWeight: FontWeight.w800,
                ),
              ),
              const SizedBox(height: 6),
              Text(
                'This may take a few moments.',
                textAlign: TextAlign.center,
                style: TextStyle(color: c.textSecondary),
              ),
              const SizedBox(height: 10),
              Center(
                child: Container(
                  padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                  decoration: BoxDecoration(
                    color: c.primarySoft,
                    borderRadius: BorderRadius.circular(20),
                  ),
                  child: Text(
                    widget.document.name,
                    maxLines: 1,
                    overflow: TextOverflow.ellipsis,
                    style: TextStyle(
                      color: c.primaryExtraDark,
                      fontWeight: FontWeight.w600,
                      fontSize: 12,
                    ),
                  ),
                ),
              ),
              const SizedBox(height: 22),
              ClipRRect(
                borderRadius: BorderRadius.circular(10),
                child: LinearProgressIndicator(
                  value: _stage / _labels.length,
                  minHeight: 8,
                ),
              ),
              const SizedBox(height: 18),
              SoftCard(
                padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
                child: Column(
                  children: List.generate(_labels.length, (i) {
                    final done = i < _stage;
                    final active = i == _stage && _stage < _labels.length;
                    return Padding(
                      padding: const EdgeInsets.symmetric(vertical: 10),
                      child: Row(
                        children: [
                          AnimatedContainer(
                            duration: const Duration(milliseconds: 250),
                            width: 28,
                            height: 28,
                            decoration: BoxDecoration(
                              color: done
                                  ? c.success
                                  : active
                                      ? c.primarySoft
                                      : c.surfaceSecondary,
                              shape: BoxShape.circle,
                            ),
                            alignment: Alignment.center,
                            child: done
                                ? const Icon(
                                    Icons.check_rounded,
                                    size: 16,
                                    color: Colors.white,
                                  )
                                : Text(
                                    '${i + 1}',
                                    style: TextStyle(
                                      color: active
                                          ? c.primaryExtraDark
                                          : c.textMuted,
                                      fontWeight: FontWeight.w700,
                                      fontSize: 12,
                                    ),
                                  ),
                          ),
                          const SizedBox(width: 12),
                          Expanded(
                            child: Text(
                              _labels[i],
                              style: TextStyle(
                                color: done || active
                                    ? c.textPrimary
                                    : c.textSecondary,
                                fontWeight:
                                    active ? FontWeight.w700 : FontWeight.w500,
                                fontSize: 13.5,
                              ),
                            ),
                          ),
                          if (active)
                            const SizedBox(
                              width: 16,
                              height: 16,
                              child: CircularProgressIndicator(strokeWidth: 2),
                            ),
                        ],
                      ),
                    );
                  }),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
