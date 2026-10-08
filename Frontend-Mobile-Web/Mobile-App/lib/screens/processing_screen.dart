import 'package:flutter/material.dart';
import '../models/document_model.dart';
import '../theme/app_theme.dart';
import 'result_screen.dart';

class ProcessingScreen extends StatefulWidget {
  const ProcessingScreen({super.key, required this.document});
  final ThesisDocument document;
  @override
  State<ProcessingScreen> createState() => _ProcessingScreenState();
}

class _ProcessingScreenState extends State<ProcessingScreen> {
  int _stage = 0;
  @override
  void initState() { super.initState(); _run(); }

  Future<void> _run() async {
    for (var i = 1; i <= 5; i++) {
      await Future<void>.delayed(const Duration(milliseconds: 700));
      if (!mounted) return;
      setState(() => _stage = i);
    }
    if (!mounted) return;
    Navigator.of(context).pushReplacement(MaterialPageRoute<void>(builder: (_) => ResultScreen(document: widget.document)));
  }

  @override
  Widget build(BuildContext context) {
    const labels = ['Document uploaded', 'Reading document format', 'Reviewing structure and content', 'Preparing the score', 'Preparing your results'];
    return Scaffold(appBar: AppBar(title: const Text('Review')), body: Center(child: SingleChildScrollView(padding: const EdgeInsets.all(24), child: ConstrainedBox(constraints: const BoxConstraints(maxWidth: 460), child: Column(children: [
      const SizedBox(height: 30),
      SizedBox(width: 84, height: 84, child: CircularProgressIndicator(value: _stage == 5 ? 1 : null, strokeWidth: 7, backgroundColor: AppColors.secondaryLight)),
      const SizedBox(height: 28),
      const Text('Reviewing your document', textAlign: TextAlign.center, style: TextStyle(color: AppColors.textPrimary, fontSize: 22, fontWeight: FontWeight.w800)),
      const SizedBox(height: 8),
      const Text('This may take a few moments.', textAlign: TextAlign.center, style: TextStyle(color: AppColors.textSecondary)),
      const SizedBox(height: 12),
      Text(widget.document.name, textAlign: TextAlign.center, style: const TextStyle(color: AppColors.primary, fontWeight: FontWeight.w600)),
      const SizedBox(height: 30),
      Card(child: Padding(padding: const EdgeInsets.all(16), child: Column(children: List.generate(labels.length, (i) {
        final done = i < _stage;
        final active = i == _stage && _stage < labels.length;
        return Padding(padding: const EdgeInsets.symmetric(vertical: 10), child: Row(children: [
          Icon(done ? Icons.check_circle_rounded : active ? Icons.radio_button_checked_rounded : Icons.circle_outlined, color: done ? AppColors.success : active ? AppColors.secondary : AppColors.border, size: 20),
          const SizedBox(width: 11),
          Expanded(child: Text(labels[i], style: TextStyle(color: done || active ? AppColors.textPrimary : AppColors.textSecondary, fontWeight: active ? FontWeight.w600 : FontWeight.w400))),
        ]));
      })))),
    ])))));
  }
}
