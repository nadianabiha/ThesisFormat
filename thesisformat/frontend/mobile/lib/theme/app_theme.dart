import 'package:flutter/material.dart';

@immutable
class AppPalette extends ThemeExtension<AppPalette> {
  const AppPalette({
    required this.primary,
    required this.primaryDark,
    required this.primaryExtraDark,
    required this.primaryLight,
    required this.primarySoft,
    required this.background,
    required this.surface,
    required this.surfaceSecondary,
    required this.card,
    required this.border,
    required this.divider,
    required this.textPrimary,
    required this.textSecondary,
    required this.textMuted,
    required this.navUnselected,
    required this.onPrimary,
    required this.success,
    required this.successBackground,
    required this.warning,
    required this.warningBackground,
    required this.error,
    required this.errorBackground,
    required this.info,
    required this.infoBackground,
  });

  final Color primary, primaryDark, primaryExtraDark, primaryLight, primarySoft;
  final Color background, surface, surfaceSecondary, card, border, divider;
  final Color textPrimary, textSecondary, textMuted, navUnselected, onPrimary;
  final Color success, successBackground, warning, warningBackground;
  final Color error, errorBackground, info, infoBackground;
  Color get secondary => primaryExtraDark;
  Color get secondaryLight => surfaceSecondary;
  Color get accent => primaryExtraDark;
  Color get purple => background.computeLuminance() < 0.1 ? const Color(0xFFA78BFA) : const Color(0xFF8B5CF6);
  Color get purpleSoft => background.computeLuminance() < 0.1 ? const Color(0xFF302449) : const Color(0xFFF0EAFF);

  static const light = AppPalette(
    primary: Color(0xFF00FFFF),
    primaryDark: Color(0xFF00D9D9),
    primaryExtraDark: Color(0xFF00BABA),
    primaryLight: Color(0xFFB8FFFF),
    primarySoft: Color(0xFFDFFFFF),
    background: Color(0xFFF7FCFC),
    surface: Color(0xFFFFFFFF),
    surfaceSecondary: Color(0xFFF3FAFA),
    card: Color(0xFFFFFFFF),
    border: Color(0xFFD9EEEE),
    divider: Color(0xFFEAF2F2),
    textPrimary: Color(0xFF1F2937),
    textSecondary: Color(0xFF6B7280),
    textMuted: Color(0xFF9CA3AF),
    navUnselected: Color(0xFF9CA3AF),
    onPrimary: Color(0xFF1F2937),
    success: Color(0xFF22C55E),
    successBackground: Color(0xFFEAF9EF),
    warning: Color(0xFFF59E0B),
    warningBackground: Color(0xFFFFF3D6),
    error: Color(0xFFEF4444),
    errorBackground: Color(0xFFFDECEC),
    info: Color(0xFF8B5CF6),
    infoBackground: Color(0xFFF0EAFF),
  );

  static const dark = AppPalette(
    primary: Color(0xFF00FFFF),
    primaryDark: Color(0xFF00D9D9),
    primaryExtraDark: Color(0xFF00D9D9),
    primaryLight: Color(0xFF123B3B),
    primarySoft: Color(0xFF123B3B),
    background: Color(0xFF121212),
    surface: Color(0xFF1E1E1E),
    surfaceSecondary: Color(0xFF252525),
    card: Color(0xFF202020),
    border: Color(0xFF333333),
    divider: Color(0xFF2D2D2D),
    textPrimary: Color(0xFFF5F5F5),
    textSecondary: Color(0xFFB8B8B8),
    textMuted: Color(0xFF8A8A8A),
    navUnselected: Color(0xFF8A8A8A),
    onPrimary: Color(0xFF121212),
    success: Color(0xFF4ADE80),
    successBackground: Color(0xFF123A23),
    warning: Color(0xFFFBBF24),
    warningBackground: Color(0xFF3D2D12),
    error: Color(0xFFF87171),
    errorBackground: Color(0xFF3B1D1D),
    info: Color(0xFFA78BFA),
    infoBackground: Color(0xFF302449),
  );

  @override
  AppPalette copyWith({
    Color? primary,
    Color? primaryDark,
    Color? primaryExtraDark,
    Color? primaryLight,
    Color? primarySoft,
    Color? background,
    Color? surface,
    Color? surfaceSecondary,
    Color? card,
    Color? border,
    Color? divider,
    Color? textPrimary,
    Color? textSecondary,
    Color? textMuted,
    Color? navUnselected,
    Color? onPrimary,
    Color? success,
    Color? successBackground,
    Color? warning,
    Color? warningBackground,
    Color? error,
    Color? errorBackground,
    Color? info,
    Color? infoBackground,
  }) => AppPalette(
    primary: primary ?? this.primary,
    primaryDark: primaryDark ?? this.primaryDark,
    primaryExtraDark: primaryExtraDark ?? this.primaryExtraDark,
    primaryLight: primaryLight ?? this.primaryLight,
    primarySoft: primarySoft ?? this.primarySoft,
    background: background ?? this.background,
    surface: surface ?? this.surface,
    surfaceSecondary: surfaceSecondary ?? this.surfaceSecondary,
    card: card ?? this.card,
    border: border ?? this.border,
    divider: divider ?? this.divider,
    textPrimary: textPrimary ?? this.textPrimary,
    textSecondary: textSecondary ?? this.textSecondary,
    textMuted: textMuted ?? this.textMuted,
    navUnselected: navUnselected ?? this.navUnselected,
    onPrimary: onPrimary ?? this.onPrimary,
    success: success ?? this.success,
    successBackground: successBackground ?? this.successBackground,
    warning: warning ?? this.warning,
    warningBackground: warningBackground ?? this.warningBackground,
    error: error ?? this.error,
    errorBackground: errorBackground ?? this.errorBackground,
    info: info ?? this.info,
    infoBackground: infoBackground ?? this.infoBackground,
  );

  @override
  AppPalette lerp(ThemeExtension<AppPalette>? other, double t) {
    if (other is! AppPalette) return this;
    return AppPalette(
      primary: Color.lerp(primary, other.primary, t)!,
      primaryDark: Color.lerp(primaryDark, other.primaryDark, t)!,
      primaryExtraDark: Color.lerp(
        primaryExtraDark,
        other.primaryExtraDark,
        t,
      )!,
      primaryLight: Color.lerp(primaryLight, other.primaryLight, t)!,
      primarySoft: Color.lerp(primarySoft, other.primarySoft, t)!,
      background: Color.lerp(background, other.background, t)!,
      surface: Color.lerp(surface, other.surface, t)!,
      surfaceSecondary: Color.lerp(
        surfaceSecondary,
        other.surfaceSecondary,
        t,
      )!,
      card: Color.lerp(card, other.card, t)!,
      border: Color.lerp(border, other.border, t)!,
      divider: Color.lerp(divider, other.divider, t)!,
      textPrimary: Color.lerp(textPrimary, other.textPrimary, t)!,
      textSecondary: Color.lerp(textSecondary, other.textSecondary, t)!,
      textMuted: Color.lerp(textMuted, other.textMuted, t)!,
      navUnselected: Color.lerp(navUnselected, other.navUnselected, t)!,
      onPrimary: Color.lerp(onPrimary, other.onPrimary, t)!,
      success: Color.lerp(success, other.success, t)!,
      successBackground: Color.lerp(
        successBackground,
        other.successBackground,
        t,
      )!,
      warning: Color.lerp(warning, other.warning, t)!,
      warningBackground: Color.lerp(
        warningBackground,
        other.warningBackground,
        t,
      )!,
      error: Color.lerp(error, other.error, t)!,
      errorBackground: Color.lerp(errorBackground, other.errorBackground, t)!,
      info: Color.lerp(info, other.info, t)!,
      infoBackground: Color.lerp(infoBackground, other.infoBackground, t)!,
    );
  }
}

extension AppPaletteContext on BuildContext {
  AppPalette get appColors =>
      Theme.of(this).extension<AppPalette>() ?? AppPalette.light;
}

class AppTheme {
  static ThemeData get lightTheme => _build(AppPalette.light, Brightness.light);
  static ThemeData get darkTheme => _build(AppPalette.dark, Brightness.dark);
  static ThemeData get light => lightTheme;

  static ThemeData _build(AppPalette palette, Brightness brightness) {
    final scheme = ColorScheme(
      brightness: brightness,
      primary: palette.primaryDark,
      onPrimary: palette.onPrimary,
      primaryContainer: palette.primarySoft,
      onPrimaryContainer: palette.textPrimary,
      secondary: palette.primaryExtraDark,
      onSecondary: palette.onPrimary,
      secondaryContainer: palette.primarySoft,
      onSecondaryContainer: palette.textPrimary,
      error: palette.error,
      onError: palette.onPrimary,
      surface: palette.surface,
      onSurface: palette.textPrimary,
      onSurfaceVariant: palette.textSecondary,
      outline: palette.border,
      outlineVariant: palette.divider,
      shadow: Colors.black,
      scrim: Colors.black,
      inverseSurface: palette.textPrimary,
      onInverseSurface: palette.surface,
      inversePrimary: palette.primaryDark,
      surfaceTint: palette.primaryDark,
    );
    final textTheme = brightness == Brightness.light
        ? Typography.material2021().black
        : Typography.material2021().white;

    return ThemeData(
      useMaterial3: true,
      brightness: brightness,
      colorScheme: scheme,
      extensions: <ThemeExtension<dynamic>>[palette],
      scaffoldBackgroundColor: palette.background,
      dividerColor: palette.divider,
      hintColor: palette.textMuted,
      iconTheme: IconThemeData(color: palette.textSecondary),
      textTheme: textTheme.apply(
        bodyColor: palette.textPrimary,
        displayColor: palette.textPrimary,
      ),
      appBarTheme: AppBarTheme(
        backgroundColor: palette.background,
        foregroundColor: palette.textPrimary,
        elevation: 0,
        centerTitle: false,
        titleTextStyle: TextStyle(
          color: palette.textPrimary,
          fontSize: 20,
          fontWeight: FontWeight.w700,
        ),
      ),
      cardTheme: CardThemeData(
        color: palette.card,
        elevation: brightness == Brightness.dark ? 0 : 1,
        shadowColor: Colors.black.withValues(alpha: .08),
        margin: EdgeInsets.zero,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(18),
          side: BorderSide(color: palette.border),
        ),
      ),
      inputDecorationTheme: InputDecorationTheme(
        filled: true,
        fillColor: brightness == Brightness.dark
            ? palette.surfaceSecondary
            : palette.surface,
        hintStyle: TextStyle(color: palette.textMuted),
        contentPadding: const EdgeInsets.symmetric(
          horizontal: 16,
          vertical: 15,
        ),
        border: OutlineInputBorder(
          borderRadius: BorderRadius.circular(14),
          borderSide: BorderSide(color: palette.border),
        ),
        enabledBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(14),
          borderSide: BorderSide(color: palette.border),
        ),
        focusedBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(14),
          borderSide: BorderSide(color: palette.primaryDark, width: 1.5),
        ),
      ),
      elevatedButtonTheme: ElevatedButtonThemeData(
        style: ElevatedButton.styleFrom(
          backgroundColor: palette.primaryDark,
          foregroundColor: palette.onPrimary,
          minimumSize: const Size.fromHeight(52),
          textStyle: const TextStyle(fontSize: 15, fontWeight: FontWeight.w700),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(14),
          ),
        ),
      ),
      outlinedButtonTheme: OutlinedButtonThemeData(
        style: OutlinedButton.styleFrom(
          foregroundColor: palette.primaryExtraDark,
          minimumSize: const Size.fromHeight(48),
          side: BorderSide(color: palette.border),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(14),
          ),
        ),
      ),
      textButtonTheme: TextButtonThemeData(
        style: TextButton.styleFrom(foregroundColor: palette.primaryExtraDark),
      ),
      navigationBarTheme: NavigationBarThemeData(
        backgroundColor: palette.surface,
        indicatorColor: palette.primarySoft,
        height: 70,
        iconTheme: WidgetStateProperty.resolveWith(
          (states) => IconThemeData(
            color: states.contains(WidgetState.selected)
                ? palette.primaryExtraDark
                : palette.navUnselected,
          ),
        ),
        labelTextStyle: WidgetStateProperty.resolveWith(
          (states) => TextStyle(
            fontSize: 11,
            fontWeight: states.contains(WidgetState.selected)
                ? FontWeight.w700
                : FontWeight.w500,
            color: states.contains(WidgetState.selected)
                ? palette.textPrimary
                : palette.navUnselected,
          ),
        ),
      ),
      chipTheme: ChipThemeData(
        backgroundColor: palette.surface,
        selectedColor: palette.primarySoft,
        side: BorderSide(color: palette.border),
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
        labelStyle: TextStyle(color: palette.textPrimary, fontSize: 12),
        secondaryLabelStyle: TextStyle(color: palette.onPrimary, fontSize: 12),
      ),
      switchTheme: SwitchThemeData(
        thumbColor: WidgetStateProperty.resolveWith(
          (states) => states.contains(WidgetState.selected)
              ? palette.onPrimary
              : palette.textMuted,
        ),
        trackColor: WidgetStateProperty.resolveWith(
          (states) => states.contains(WidgetState.selected)
              ? palette.primary
              : palette.surfaceSecondary,
        ),
      ),
      dialogTheme: DialogThemeData(
        backgroundColor: palette.surface,
        titleTextStyle: TextStyle(
          color: palette.textPrimary,
          fontSize: 20,
          fontWeight: FontWeight.w700,
        ),
        contentTextStyle: TextStyle(color: palette.textSecondary),
      ),
      progressIndicatorTheme: ProgressIndicatorThemeData(
        color: palette.primaryDark,
        linearTrackColor: palette.primaryLight,
      ),
      snackBarTheme: SnackBarThemeData(
        backgroundColor: palette.card,
        contentTextStyle: TextStyle(color: palette.textPrimary),
        behavior: SnackBarBehavior.floating,
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      ),
    );
  }
}
