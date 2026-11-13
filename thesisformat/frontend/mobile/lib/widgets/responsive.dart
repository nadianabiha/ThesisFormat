import 'package:flutter/material.dart';

/// Ukuran layar (breakpoint):
/// - compact  : HP, lebar < 600
/// - medium   : tablet, 600 - 1023
/// - expanded : desktop / tablet landscape, >= 1024
enum ScreenSize { compact, medium, expanded }

extension ResponsiveContext on BuildContext {
  ScreenSize get screenSize {
    final width = MediaQuery.sizeOf(this).width;
    if (width < 600) return ScreenSize.compact;
    if (width < 1024) return ScreenSize.medium;
    return ScreenSize.expanded;
  }

  bool get isCompact => screenSize == ScreenSize.compact;
  bool get isExpanded => screenSize == ScreenSize.expanded;

  /// Lebar maksimum konten untuk halaman biasa.
  double get contentMaxWidth => switch (screenSize) {
    ScreenSize.compact => 560,
    ScreenSize.medium => 760,
    ScreenSize.expanded => 1200,
  };
}

/// Grid yang jumlah kolomnya mengikuti lebar yang tersedia.
/// Tinggi tiap item mengikuti isinya, jadi aman untuk teks panjang.
class ResponsiveWrapGrid extends StatelessWidget {
  const ResponsiveWrapGrid({
    super.key,
    required this.children,
    this.minItemWidth = 300,
    this.maxColumns = 3,
    this.spacing = 12,
  });

  final List<Widget> children;
  final double minItemWidth;
  final int maxColumns;
  final double spacing;

  @override
  Widget build(BuildContext context) {
    return LayoutBuilder(
      builder: (context, constraints) {
        final width = constraints.maxWidth;
        final columns = ((width + spacing) / (minItemWidth + spacing))
            .floor()
            .clamp(1, maxColumns);

        if (columns == 1) {
          return Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              for (var i = 0; i < children.length; i++) ...[
                if (i > 0) SizedBox(height: spacing),
                children[i],
              ],
            ],
          );
        }

        final itemWidth = (width - spacing * (columns - 1)) / columns;
        return Wrap(
          spacing: spacing,
          runSpacing: spacing,
          children: [
            for (final child in children)
              SizedBox(width: itemWidth, child: child),
          ],
        );
      },
    );
  }
}
