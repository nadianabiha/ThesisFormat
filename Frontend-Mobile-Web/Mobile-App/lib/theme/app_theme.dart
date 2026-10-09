import 'package:flutter/material.dart';

class AppColors {
  static const primary = Color(0xFF0C7E83);
  static const primaryDark = Color(0xFF052F48);
  static const primaryLight = Color(0xFFE2F8F5);
  static const secondary = Color(0xFF50D3CA);
  static const secondaryLight = Color(0xFFE5FAF7);
  static const accent = Color(0xFFFFCF3D);
  static const background = Color(0xFFF5FAFA);
  static const surface = Color(0xFFFFFFFF);
  static const textPrimary = Color(0xFF183241);
  static const textSecondary = Color(0xFF627782);
  static const border = Color(0xFFDCE8E8);
  static const success = Color(0xFF22C55E);
  static const successBackground = Color(0xFFECFDF3);
  static const warning = Color(0xFFF59E0B);
  static const warningBackground = Color(0xFFFFF7E6);
  static const error = Color(0xFFEF4444);
  static const errorBackground = Color(0xFFFEF2F2);
  static const info = Color(0xFF3B82F6);
  static const infoBackground = Color(0xFFEFF6FF);
}

class AppTheme {
  static ThemeData get light {
    final scheme = ColorScheme.fromSeed(seedColor: AppColors.primary, brightness: Brightness.light)
        .copyWith(primary: AppColors.primary, onPrimary: Colors.white, secondary: AppColors.secondary, onSecondary: Colors.white, surface: AppColors.surface, onSurface: AppColors.textPrimary, onSurfaceVariant: AppColors.textSecondary, error: AppColors.error);
    return ThemeData(
      useMaterial3: true,
      colorScheme: scheme,
      scaffoldBackgroundColor: AppColors.background,
      textTheme: Typography.material2021().black.apply(bodyColor: AppColors.textPrimary, displayColor: AppColors.textPrimary),
      appBarTheme: const AppBarTheme(backgroundColor: AppColors.background, foregroundColor: AppColors.textPrimary, elevation: 0, centerTitle: false, titleTextStyle: TextStyle(color: AppColors.textPrimary, fontSize: 20, fontWeight: FontWeight.w700)),
      cardTheme: CardThemeData(color: AppColors.surface, elevation: 0, margin: EdgeInsets.zero, shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16), side: const BorderSide(color: AppColors.border))),
      inputDecorationTheme: InputDecorationTheme(filled: true, fillColor: AppColors.surface, hintStyle: const TextStyle(color: AppColors.textSecondary), contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 15), border: OutlineInputBorder(borderRadius: BorderRadius.circular(14), borderSide: const BorderSide(color: AppColors.border)), enabledBorder: OutlineInputBorder(borderRadius: BorderRadius.circular(14), borderSide: const BorderSide(color: AppColors.border)), focusedBorder: OutlineInputBorder(borderRadius: BorderRadius.circular(14), borderSide: const BorderSide(color: AppColors.primary, width: 1.5))),
      elevatedButtonTheme: ElevatedButtonThemeData(style: ElevatedButton.styleFrom(backgroundColor: AppColors.primary, foregroundColor: Colors.white, minimumSize: const Size.fromHeight(52), textStyle: const TextStyle(fontSize: 15, fontWeight: FontWeight.w700), shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(14)))),
      outlinedButtonTheme: OutlinedButtonThemeData(style: OutlinedButton.styleFrom(foregroundColor: AppColors.primary, minimumSize: const Size.fromHeight(48), side: const BorderSide(color: AppColors.border), shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(14)))),
      navigationBarTheme: NavigationBarThemeData(backgroundColor: Colors.white, indicatorColor: AppColors.primaryLight, height: 70, labelTextStyle: WidgetStateProperty.resolveWith((s) => TextStyle(fontSize: 11, fontWeight: s.contains(WidgetState.selected) ? FontWeight.w700 : FontWeight.w500, color: s.contains(WidgetState.selected) ? AppColors.primary : AppColors.textSecondary))),
      chipTheme: ChipThemeData(backgroundColor: Colors.white, selectedColor: AppColors.primaryLight, side: const BorderSide(color: AppColors.border), shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)), labelStyle: const TextStyle(fontSize: 12)),
      progressIndicatorTheme: const ProgressIndicatorThemeData(color: AppColors.primary, linearTrackColor: AppColors.secondaryLight),
      snackBarTheme: SnackBarThemeData(behavior: SnackBarBehavior.floating, shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12))),
    );
  }
}
