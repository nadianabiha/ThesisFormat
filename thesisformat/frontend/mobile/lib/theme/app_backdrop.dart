import 'package:flutter/material.dart';

import 'app_theme.dart';

/// Latar belakang semua halaman: gradasi "mesh" tosca–navy–kuning
/// dengan motif titik yang memudar (sama seperti dashboard web).
///
/// Dipasang otomatis di setiap halaman lewat [BackdropPageTransitionsBuilder],
/// sehingga Scaffold cukup memakai latar transparan.
class AppBackdrop extends StatelessWidget {
  const AppBackdrop({super.key, required this.child});

  final Widget child;

  @override
  Widget build(BuildContext context) {
    final c = context.appColors;
    final dark = c.isDark;

    Widget glow(Alignment center, Color color, double alpha, double radius) {
      return Positioned.fill(
        child: DecoratedBox(
          decoration: BoxDecoration(
            gradient: RadialGradient(
              center: center,
              radius: radius,
              colors: [
                color.withValues(alpha: alpha),
                color.withValues(alpha: 0),
              ],
            ),
          ),
        ),
      );
    }

    return Stack(
      children: [
        Positioned.fill(child: ColoredBox(color: c.background)),
        glow(const Alignment(-1.1, -1.05), c.primary, dark ? .22 : .75, 1.1),
        glow(const Alignment(1.2, -0.75), c.heroEnd, dark ? .45 : .35, 0.9),
        glow(const Alignment(0.6, 1.1), c.warning, dark ? .10 : .40, 0.8),
        glow(const Alignment(-1.1, 0.95), c.primary, dark ? .14 : .40, 0.8),
        Positioned.fill(
          child: RepaintBoundary(
            child: CustomPaint(
              painter: _DotsPainter(
                (dark ? Colors.white : c.primaryDark).withValues(
                  alpha: dark ? .07 : .13,
                ),
              ),
            ),
          ),
        ),
        Positioned.fill(child: child),
      ],
    );
  }
}

/// Motif titik yang memudar dari kiri atas ke kanan bawah.
class _DotsPainter extends CustomPainter {
  _DotsPainter(this.color);

  final Color color;

  @override
  void paint(Canvas canvas, Size size) {
    const gap = 22.0;
    final paint = Paint();
    final diagonal = size.width + size.height;
    for (var y = gap / 2; y < size.height; y += gap) {
      for (var x = gap / 2; x < size.width; x += gap) {
        // 0 di pojok kiri atas, 1 di pojok kanan bawah.
        final t = (x + y) / diagonal;
        final fade = t < .45 ? 1 - t * 1.45 : (.75 - t).clamp(0, .3) / .3 * .35;
        if (fade <= 0.02) continue;
        paint.color = color.withValues(alpha: color.a * fade);
        canvas.drawCircle(Offset(x, y), 1.4, paint);
      }
    }
  }

  @override
  bool shouldRepaint(_DotsPainter oldDelegate) => oldDelegate.color != color;
}

/// Membungkus setiap halaman dengan [AppBackdrop] tanpa mengubah animasi
/// perpindahan halaman bawaan platform.
class BackdropPageTransitionsBuilder extends PageTransitionsBuilder {
  const BackdropPageTransitionsBuilder(this.inner);

  final PageTransitionsBuilder inner;

  @override
  Widget buildTransitions<T>(
    PageRoute<T> route,
    BuildContext context,
    Animation<double> animation,
    Animation<double> secondaryAnimation,
    Widget child,
  ) {
    return inner.buildTransitions<T>(
      route,
      context,
      animation,
      secondaryAnimation,
      AppBackdrop(child: child),
    );
  }
}
