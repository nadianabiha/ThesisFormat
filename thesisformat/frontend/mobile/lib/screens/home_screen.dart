import 'package:flutter/material.dart';

import '../models/document_model.dart';
import '../services/api_service.dart';
import '../services/auth_service.dart';
import '../services/document_events.dart';
import '../theme/app_theme.dart';
import '../widgets/app_bottom_nav.dart';
import '../widgets/document_card.dart';
import '../widgets/responsive.dart';
import '../widgets/ui_kit.dart';
import 'history_screen.dart';
import 'login_screen.dart';
import 'profile_screen.dart';
import 'result_screen.dart';
import 'upload_screen.dart';

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  int _tab = 0;

  Future<void> _openUpload([String? type]) async {
    await Navigator.of(context).push(
      MaterialPageRoute<void>(builder: (_) => UploadScreen(initialType: type)),
    );

    if (mounted) {
      setState(() {});
    }
  }

  @override
  Widget build(BuildContext context) {
    return AnimatedBuilder(
      animation: AuthService.instance,
      builder: (context, _) {
        final welcomeName =
            AuthService.instance.currentUser?.displayName ?? '';

        final pages = [
          _Dashboard(
            key: ValueKey(
              '${AuthService.instance.currentUser?.email ?? ''}-$_tab',
            ),
            welcomeName: welcomeName,
            onUpload: _openUpload,
            onHistory: () => setState(() => _tab = 1),
            onProfile: () => setState(() => _tab = 2),
          ),
          const HistoryScreen(embedded: true),
          ProfileScreen(
            embedded: true,
            onLogout: () {
              AuthService.instance.logout();

              Navigator.of(context).pushAndRemoveUntil(
                MaterialPageRoute<void>(builder: (_) => const LoginScreen()),
                (_) => false,
              );
            },
          ),
        ];

        final size = context.screenSize;
        void select(int index) => setState(() => _tab = index);

        final content = MobileFrame(
          maxWidth: context.contentMaxWidth,
          child: IndexedStack(index: _tab, children: pages),
        );

        // HP: bottom nav. Tablet/desktop: navigasi di samping.
        if (size == ScreenSize.compact) {
          return Scaffold(
            body: SafeArea(bottom: false, child: content),
            bottomNavigationBar: AppBottomNav(
              selectedIndex: _tab,
              onSelected: select,
            ),
          );
        }

        return Scaffold(
          body: Row(
            children: [
              AppSideNav(
                selectedIndex: _tab,
                onSelected: select,
                extended: size == ScreenSize.expanded,
              ),
              Expanded(child: SafeArea(left: false, child: content)),
            ],
          ),
        );
      },
    );
  }
}

class _Dashboard extends StatefulWidget {
  const _Dashboard({
    super.key,
    required this.welcomeName,
    required this.onUpload,
    required this.onHistory,
    required this.onProfile,
  });

  final String welcomeName;
  final void Function([String? type]) onUpload;
  final VoidCallback onHistory;
  final VoidCallback onProfile;

  @override
  State<_Dashboard> createState() => _DashboardState();
}

class _DashboardState extends State<_Dashboard> {
  late Future<List<DocumentModel>> _historyFuture;

  @override
  void initState() {
    super.initState();
    _loadHistory();
    DocumentEvents.instance.addListener(_onDocumentsChanged);
  }

  @override
  void dispose() {
    DocumentEvents.instance.removeListener(_onDocumentsChanged);
    super.dispose();
  }

  // Dipanggil setelah upload berhasil: muat ulang dokumen terbaru.
  void _onDocumentsChanged() {
    if (!mounted) return;
    setState(_loadHistory);
  }

  void _loadHistory() {
    _historyFuture = const ApiService().getDocumentHistory();
    // Error tetap ditampilkan oleh FutureBuilder; ignore() mencegah
    // "unhandled exception" jika layar sudah ditutup sebelum selesai.
    _historyFuture.ignore();
  }

  Future<void> _refreshHistory() async {
    setState(_loadHistory);

    try {
      await _historyFuture;
    } catch (_) {
      // Pesan error ditampilkan oleh FutureBuilder.
    }
  }

  void _openResult(DocumentModel document) {
    Navigator.of(context).push(
      MaterialPageRoute<void>(builder: (_) => ResultScreen(document: document)),
    );
  }

  Future<void> _openLatestResult() async {
    try {
      final documents = await _historyFuture;

      if (!mounted) return;

      if (documents.isEmpty) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Belum ada dokumen yang diunggah.')),
        );
        return;
      }

      _openResult(documents.first);
    } catch (error) {
      if (!mounted) return;

      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Gagal mengambil dokumen: $error')),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    final greeting = _Greeting(
      name: widget.welcomeName,
      onProfile: widget.onProfile,
    );

    final startSection = Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        _HeroBanner(onStart: () => widget.onUpload()),
      ],
    );

    final reviewSection = _reviewSection(context);

    return RefreshIndicator(
      onRefresh: _refreshHistory,
      child: LayoutBuilder(
        builder: (context, constraints) {
          // Lebar >= 900: dua kolom (desktop). Selain itu satu kolom.
          final wide = constraints.maxWidth >= 900;

          return ListView(
            physics: const AlwaysScrollableScrollPhysics(),
            padding: EdgeInsets.fromLTRB(
              wide ? 32 : 22,
              wide ? 28 : 20,
              wide ? 32 : 22,
              24,
            ),
            children: [
              greeting,
              SizedBox(height: wide ? 26 : 22),
              if (wide)
                Row(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Expanded(flex: 6, child: startSection),
                    const SizedBox(width: 28),
                    Expanded(flex: 5, child: reviewSection),
                  ],
                )
              else ...[
                startSection,
                const SizedBox(height: 22),
                reviewSection,
              ],
            ],
          );
        },
      ),
    );
  }

  Widget _reviewSection(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        SectionHeader(
          title: 'Latest Review',
          action: 'View result',
          onTap: _openLatestResult,
        ),
        const SizedBox(height: 8),

        FutureBuilder<List<DocumentModel>>(
          future: _historyFuture,
          builder: (context, snapshot) {
            if (snapshot.connectionState == ConnectionState.waiting) {
              return const SoftCard(
                padding: EdgeInsets.all(28),
                child: Center(child: CircularProgressIndicator()),
              );
            }

            if (snapshot.hasError) {
              return EmptyState(
                icon: Icons.cloud_off_rounded,
                message: 'Gagal memuat dokumen terbaru.',
                buttonText: 'Coba lagi',
                onPressed: () => setState(_loadHistory),
              );
            }

            final documents = snapshot.data ?? [];

            if (documents.isEmpty) {
              return const EmptyState(
                icon: Icons.upload_file_rounded,
                message: 'Belum ada dokumen. Silakan unggah dokumen.',
              );
            }

            return _LatestReviewCard(
              document: documents.first,
              onTap: () => _openResult(documents.first),
            );
          },
        ),

        const SizedBox(height: 22),

        SectionHeader(
          title: 'Recent Documents',
          action: 'View all',
          onTap: widget.onHistory,
        ),
        const SizedBox(height: 8),

        FutureBuilder<List<DocumentModel>>(
          future: _historyFuture,
          builder: (context, snapshot) {
            if (snapshot.connectionState == ConnectionState.waiting) {
              return const SizedBox.shrink();
            }

            if (snapshot.hasError) {
              return EmptyState(
                icon: Icons.cloud_off_rounded,
                message: 'Riwayat gagal dimuat.',
                buttonText: 'Coba lagi',
                onPressed: () => setState(_loadHistory),
              );
            }

            final documents = snapshot.data ?? [];

            if (documents.length <= 1) {
              return const EmptyState(
                icon: Icons.folder_open_rounded,
                message: 'Belum ada riwayat dokumen lain.',
              );
            }

            // Tablet: 2 kolom; HP & kolom kanan desktop: 1 kolom.
            return ResponsiveWrapGrid(
              minItemWidth: 300,
              maxColumns: 2,
              spacing: 10,
              children: [
                for (final document in documents.skip(1).take(4))
                  DocumentCard(
                    document: document,
                    onTap: () => _openResult(document),
                  ),
              ],
            );
          },
        ),
      ],
    );
  }
}

class _Greeting extends StatelessWidget {
  const _Greeting({required this.name, required this.onProfile});

  final String name;
  final VoidCallback onProfile;

  @override
  Widget build(BuildContext context) {
    final c = context.appColors;
    final initial = name.isEmpty ? '?' : name.substring(0, 1).toUpperCase();

    return Row(
      children: [
        Expanded(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                'Welcome',
                style: TextStyle(color: c.textSecondary, fontSize: 14),
              ),
              const SizedBox(height: 2),
              Text(
                name.isEmpty ? 'Mahasiswa' : name,
                maxLines: 1,
                overflow: TextOverflow.ellipsis,
                style: TextStyle(
                  color: c.textPrimary,
                  fontSize: 24,
                  fontWeight: FontWeight.w800,
                  letterSpacing: -.3,
                ),
              ),
            ],
          ),
        ),
        _RoundIconButton(
          icon: Icons.notifications_none_rounded,
          tooltip: 'Notifications',
          onTap: () {
            ScaffoldMessenger.of(context).showSnackBar(
              const SnackBar(content: Text('You have no new notifications.')),
            );
          },
        ),
        const SizedBox(width: 10),
        Tooltip(
          message: 'Profile',
          child: InkWell(
            customBorder: const CircleBorder(),
            onTap: onProfile,
            child: Container(
              width: 46,
              height: 46,
              decoration: BoxDecoration(
                color: c.warningBackground,
                shape: BoxShape.circle,
                border: Border.all(color: c.surface, width: 3),
              ),
              alignment: Alignment.center,
              child: Text(
                initial,
                style: TextStyle(
                  color: c.warning,
                  fontWeight: FontWeight.w800,
                  fontSize: 18,
                ),
              ),
            ),
          ),
        ),
      ],
    );
  }
}

class _RoundIconButton extends StatelessWidget {
  const _RoundIconButton({
    required this.icon,
    required this.onTap,
    required this.tooltip,
  });

  final IconData icon;
  final VoidCallback onTap;
  final String tooltip;

  @override
  Widget build(BuildContext context) {
    final c = context.appColors;
    return Tooltip(
      message: tooltip,
      child: Material(
        color: c.card,
        shape: CircleBorder(
          side: BorderSide(color: c.isDark ? c.border : c.divider),
        ),
        child: InkWell(
          customBorder: const CircleBorder(),
          onTap: onTap,
          child: SizedBox(
            width: 44,
            height: 44,
            child: Icon(icon, color: c.textPrimary, size: 22),
          ),
        ),
      ),
    );
  }
}

class _HeroBanner extends StatelessWidget {
  const _HeroBanner({required this.onStart});

  final VoidCallback onStart;

  @override
  Widget build(BuildContext context) {
    final c = context.appColors;
    final width = MediaQuery.sizeOf(context).width;
    final textScale = MediaQuery.textScalerOf(context).scale(1);
    final double illustrationSize = width < 340 || textScale > 1.2
        ? 0
        : width < 400
        ? 88
        : 116;

    return SoftCard(
      gradient: c.heroGradient,
      radius: 24,
      padding: EdgeInsets.fromLTRB(20, 20, illustrationSize > 0 ? 8 : 20, 20),
      onTap: onStart,
      child: Row(
        children: [
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Text(
                  'Check your document format',
                  style: TextStyle(
                    color: Colors.white,
                    fontSize: 18,
                    fontWeight: FontWeight.w800,
                    height: 1.25,
                  ),
                ),
                const SizedBox(height: 6),
                Text(
                  'Upload a PDF or DOCX and get a score based on the Polinela writing guide.',
                  style: TextStyle(
                    color: Colors.white.withValues(alpha: .88),
                    fontSize: 12,
                    height: 1.45,
                  ),
                ),
                const SizedBox(height: 16),
                Container(
                  padding: const EdgeInsets.symmetric(
                    horizontal: 16,
                    vertical: 10,
                  ),
                  decoration: BoxDecoration(
                    color: c.accent,
                    borderRadius: BorderRadius.circular(30),
                  ),
                  child: Row(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      Flexible(
                        child: Text(
                          'Start review',
                          maxLines: 1,
                          overflow: TextOverflow.ellipsis,
                          style: TextStyle(
                            color: c.navOnSelected,
                            fontWeight: FontWeight.w700,
                            fontSize: 13,
                          ),
                        ),
                      ),
                      const SizedBox(width: 6),
                      Icon(
                        Icons.arrow_forward_rounded,
                        color: c.navOnSelected,
                        size: 16,
                      ),
                    ],
                  ),
                ),
              ],
            ),
          ),
          // Ilustrasi menyesuaikan lebar layar; disembunyikan di HP sempit.
          if (illustrationSize > 0)
            BlobIllustration(
              size: illustrationSize,
              blobColor: Colors.white.withValues(alpha: .22),
            ),
        ],
      ),
    );
  }
}

class _LatestReviewCard extends StatelessWidget {
  const _LatestReviewCard({required this.document, required this.onTap});

  final DocumentModel document;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    final c = context.appColors;
    final style = DocTypeStyle.of(context, document.documentType);
    final score = document.score.clamp(0, 100);

    return SoftCard(
      onTap: onTap,
      radius: 24,
      padding: const EdgeInsets.all(18),
      child: Row(
        children: [
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Container(
                  padding: const EdgeInsets.symmetric(
                    horizontal: 10,
                    vertical: 5,
                  ),
                  decoration: BoxDecoration(
                    color: style.background(context),
                    borderRadius: BorderRadius.circular(20),
                  ),
                  child: Row(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      Icon(style.icon, size: 13, color: style.color),
                      const SizedBox(width: 5),
                      Flexible(
                        child: Text(
                          document.displayDocumentType,
                          maxLines: 1,
                          overflow: TextOverflow.ellipsis,
                          style: TextStyle(
                            color: style.color,
                            fontSize: 11,
                            fontWeight: FontWeight.w700,
                          ),
                        ),
                      ),
                    ],
                  ),
                ),
                const SizedBox(height: 10),
                Text(
                  document.name,
                  maxLines: 2,
                  overflow: TextOverflow.ellipsis,
                  style: TextStyle(
                    color: c.textPrimary,
                    fontSize: 15,
                    fontWeight: FontWeight.w800,
                    height: 1.3,
                  ),
                ),
                const SizedBox(height: 6),
                Row(
                  children: [
                    Icon(Icons.schedule_rounded, size: 13, color: c.textMuted),
                    const SizedBox(width: 4),
                    Text(
                      document.date,
                      style: TextStyle(color: c.textSecondary, fontSize: 11.5),
                    ),
                  ],
                ),
                const SizedBox(height: 4),
                Row(
                  children: [
                    Icon(Icons.flag_outlined, size: 13, color: c.warning),
                    const SizedBox(width: 4),
                    Text(
                      document.isIncomplete
                          ? 'Content check incomplete'
                          : '${document.findingsCount} items need attention',
                      style: TextStyle(color: c.textSecondary, fontSize: 11.5),
                    ),
                  ],
                ),
              ],
            ),
          ),
          const SizedBox(width: 14),
          ScoreRing(
            score: document.isIncomplete ? null : score,
            size: 92,
            stroke: 9,
          ),
        ],
      ),
    );
  }
}
