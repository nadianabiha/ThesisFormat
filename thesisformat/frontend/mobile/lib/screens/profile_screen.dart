import 'package:flutter/material.dart';

import '../services/auth_service.dart';
import '../services/theme_controller.dart';
import '../theme/app_theme.dart';
import '../widgets/responsive.dart';
import '../widgets/ui_kit.dart';
import 'change_password_screen.dart';
import 'edit_profile_screen.dart';
import '../widgets/app_logo.dart';

class ProfileScreen extends StatelessWidget {
  const ProfileScreen({super.key, this.embedded = false, this.onLogout});
  final bool embedded;
  final VoidCallback? onLogout;
  void _info(BuildContext context, String text) =>
      ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(text)));

  @override
  Widget build(BuildContext context) => ListenableBuilder(
    listenable: AuthService.instance,
    builder: (context, _) => _build(context),
  );

  Widget _build(BuildContext context) {
    final c = context.appColors;
    final user = AuthService.instance.currentUser;
    final isDarkMode = ThemeController.instance.isDarkMode;
    final displayName = user?.displayName ?? '';
    final initial = displayName.isEmpty
        ? '?'
        : displayName.substring(0, 1).toUpperCase();

    // Kartu profil (nama, email).
    final headerCard = SoftCard(
      gradient: c.heroGradient,
      radius: 24,
      padding: const EdgeInsets.all(20),
      child: Row(
        children: [
          Container(
            width: 64,
            height: 64,
            decoration: BoxDecoration(
              color: Colors.white,
              shape: BoxShape.circle,
              border: Border.all(
                color: Colors.white.withValues(alpha: .4),
                width: 4,
              ),
            ),
            alignment: Alignment.center,
            child: Text(
              initial,
              style: TextStyle(
                color: c.heroEnd,
                fontWeight: FontWeight.w800,
                fontSize: 26,
              ),
            ),
          ),
          const SizedBox(width: 16),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  displayName,
                  maxLines: 1,
                  overflow: TextOverflow.ellipsis,
                  style: const TextStyle(
                    color: Colors.white,
                    fontSize: 18,
                    fontWeight: FontWeight.w800,
                  ),
                ),
                const SizedBox(height: 4),
                Text(
                  user?.email ?? '',
                  maxLines: 1,
                  overflow: TextOverflow.ellipsis,
                  style: TextStyle(
                    color: Colors.white.withValues(alpha: .85),
                    fontSize: 13,
                  ),
                ),
                const SizedBox(height: 8),
                Container(
                  padding: const EdgeInsets.symmetric(
                    horizontal: 10,
                    vertical: 4,
                  ),
                  decoration: BoxDecoration(
                    color: Colors.white.withValues(alpha: .2),
                    borderRadius: BorderRadius.circular(20),
                  ),
                  child: const Text(
                    'Mahasiswa',
                    style: TextStyle(
                      color: Colors.white,
                      fontSize: 11,
                      fontWeight: FontWeight.w600,
                    ),
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );

    // Pengaturan aplikasi.
    final settings = <Widget>[
      Padding(
        padding: const EdgeInsets.only(left: 4, bottom: 10),
        child: Text(
          'Settings',
          style: TextStyle(
            color: c.textSecondary,
            fontSize: 13,
            fontWeight: FontWeight.w700,
          ),
        ),
      ),
      SoftCard(
        padding: const EdgeInsets.symmetric(vertical: 6),
        child: Column(
          children: [
            SwitchListTile(
              secondary: _IconBubble(
                icon: isDarkMode
                    ? Icons.dark_mode_rounded
                    : Icons.light_mode_rounded,
                color: c.warning,
              ),
              title: const Text(
                'App Theme',
                style: TextStyle(fontWeight: FontWeight.w600, fontSize: 14),
              ),
              subtitle: Text(isDarkMode ? 'Dark Mode' : 'Light Mode'),
              value: isDarkMode,
              onChanged: (enabled) async {
                await ThemeController.instance.setDarkMode(enabled);
              },
            ),
            _divider(c),
            _ProfileAction(
              icon: Icons.edit_outlined,
              color: c.primaryDark,
              label: 'Edit Profile',
              onTap: () => Navigator.of(context).push(
                MaterialPageRoute<void>(
                  builder: (_) => const EditProfileScreen(),
                ),
              ),
            ),
            _divider(c),
            _ProfileAction(
              icon: Icons.lock_outline_rounded,
              color: c.info,
              label: 'Change Password',
              onTap: () => Navigator.of(context).push(
                MaterialPageRoute<void>(
                  builder: (_) => const ChangePasswordScreen(),
                ),
              ),
            ),
            _divider(c),
            _ProfileAction(
              icon: Icons.info_outline_rounded,
              color: c.success,
              label: 'About the App',
              onTap: () => showAboutDialog(
                context: context,
                applicationName: 'ThesisFormat',
                applicationVersion: '1.0.0',
                applicationIcon: const AppLogo(size: 52),
                applicationLegalese: 'Academic writing assistant.',
              ),
            ),
          ],
        ),
      ),
    ];

    // Tombol keluar & versi aplikasi.
    final footer = <Widget>[
      OutlinedButton.icon(
        onPressed: onLogout ?? () => _info(context, 'You have logged out.'),
        icon: const Icon(Icons.logout_rounded),
        style: OutlinedButton.styleFrom(
          foregroundColor: c.error,
          side: BorderSide(color: c.error),
        ),
        label: const Text('Logout'),
      ),
      const SizedBox(height: 18),
      Center(
        child: Text(
          'ThesisFormat · Version 1.0.0',
          style: TextStyle(color: c.textMuted, fontSize: 11),
        ),
      ),
    ];

    // Lebar >= 900: kartu profil di kiri, pengaturan di kanan.
    Widget layout(double width) {
      if (width >= 900) {
        return Row(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [headerCard, const SizedBox(height: 20), ...footer],
              ),
            ),
            const SizedBox(width: 28),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: settings,
              ),
            ),
          ],
        );
      }
      return Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          headerCard,
          const SizedBox(height: 22),
          ...settings,
          const SizedBox(height: 20),
          ...footer,
        ],
      );
    }

    if (embedded) {
      return LayoutBuilder(
        builder: (context, constraints) {
          final wide = constraints.maxWidth >= 900;
          return ListView(
            padding: EdgeInsets.fromLTRB(
              wide ? 32 : 22,
              wide ? 28 : 20,
              wide ? 32 : 22,
              24,
            ),
            children: [
              Text(
                'Profile',
                style: TextStyle(
                  color: c.textPrimary,
                  fontSize: 24,
                  fontWeight: FontWeight.w800,
                  letterSpacing: -.3,
                ),
              ),
              const SizedBox(height: 18),
              layout(constraints.maxWidth - (wide ? 64 : 44)),
            ],
          );
        },
      );
    }
    return Scaffold(
      appBar: AppBar(title: const Text('Profile')),
      body: MobileFrame(
        maxWidth: context.contentMaxWidth,
        child: LayoutBuilder(
          builder: (context, constraints) => ListView(
            padding: const EdgeInsets.fromLTRB(22, 6, 22, 24),
            children: [layout(constraints.maxWidth - 44)],
          ),
        ),
      ),
    );
  }

  Widget _divider(AppPalette c) =>
      Divider(height: 1, indent: 68, endIndent: 16, color: c.divider);
}

class _IconBubble extends StatelessWidget {
  const _IconBubble({required this.icon, required this.color});

  final IconData icon;
  final Color color;

  @override
  Widget build(BuildContext context) => Container(
    width: 38,
    height: 38,
    decoration: BoxDecoration(
      color: color.withValues(alpha: context.appColors.isDark ? .2 : .12),
      borderRadius: BorderRadius.circular(12),
    ),
    child: Icon(icon, color: color, size: 20),
  );
}

class _ProfileAction extends StatelessWidget {
  const _ProfileAction({
    required this.icon,
    required this.color,
    required this.label,
    required this.onTap,
  });
  final IconData icon;
  final Color color;
  final String label;
  final VoidCallback onTap;
  @override
  Widget build(BuildContext context) {
    return ListTile(
      leading: _IconBubble(icon: icon, color: color),
      title: Text(
        label,
        style: const TextStyle(fontWeight: FontWeight.w600, fontSize: 14),
      ),
      trailing: Icon(
        Icons.chevron_right_rounded,
        color: context.appColors.textMuted,
      ),
      onTap: onTap,
    );
  }
}
