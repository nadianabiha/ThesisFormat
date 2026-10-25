import 'package:flutter/material.dart';

import '../theme/app_theme.dart';
import '../services/auth_service.dart';
import '../services/theme_controller.dart';

class ProfileScreen extends StatelessWidget {
  const ProfileScreen({super.key, this.embedded = false, this.onLogout});
  final bool embedded;
  final VoidCallback? onLogout;
  void _info(BuildContext context, String text) =>
      ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(text)));

  @override
  Widget build(BuildContext context) {
    final user = AuthService.instance.currentUser;
    final isDarkMode = ThemeController.instance.isDarkMode;
    final initial = user == null || user.name.trim().isEmpty
        ? '?'
        : user.name.trim().substring(0, 1).toUpperCase();
    final children = [
      Center(
        child: Column(
          children: [
            Container(
              width: 92,
              height: 92,
              decoration: BoxDecoration(
                color: context.appColors.purpleSoft,
                shape: BoxShape.circle,
              ),
              alignment: Alignment.center,
              child: Text(
                initial,
                style: TextStyle(
                  color: context.appColors.purple,
                  fontWeight: FontWeight.w800,
                  fontSize: 34,
                ),
              ),
            ),
            const SizedBox(height: 14),
            Text(
              user?.name ?? '',
              style: const TextStyle(fontSize: 20, fontWeight: FontWeight.w800),
            ),
            const SizedBox(height: 4),
            Text(
              user?.email ?? '',
              style: TextStyle(
                color: context.appColors.textSecondary,
                fontSize: 13,
              ),
            ),
          ],
        ),
      ),
      const SizedBox(height: 25),
      Card(
        child: Column(
          children: [
            SwitchListTile(
              secondary: Icon(
                isDarkMode ? Icons.dark_mode : Icons.light_mode,
                color: context.appColors.warning,
              ),
              title: const Text('App Theme'),
              subtitle: Text(isDarkMode ? 'Dark Mode' : 'Light Mode'),
              value: isDarkMode,
              onChanged: (enabled) async {
                await ThemeController.instance.setDarkMode(enabled);
              },
            ),
            const Divider(height: 1, indent: 54),
            _ProfileAction(
              icon: Icons.edit_outlined,
              label: 'Edit Profile',
              onTap: () => _info(
                context,
                'Profile editing will be available when accounts are connected.',
              ),
            ),
            const Divider(height: 1, indent: 54),
            _ProfileAction(
              icon: Icons.lock_outline_rounded,
              label: 'Change Password',
              onTap: () => _info(
                context,
                'Password changes will be available when accounts are connected.',
              ),
            ),
            const Divider(height: 1, indent: 54),
            _ProfileAction(
              icon: Icons.info_outline_rounded,
              label: 'About the App',
              onTap: () => showAboutDialog(
                context: context,
                applicationName: 'ThesisFormat',
                applicationVersion: '1.0.0',
                applicationLegalese: 'Academic writing assistant.',
              ),
            ),
          ],
        ),
      ),
      const SizedBox(height: 16),
      OutlinedButton.icon(
        onPressed: onLogout ?? () => _info(context, 'You have signed out.'),
        icon: const Icon(Icons.logout_rounded),
        style: OutlinedButton.styleFrom(
          foregroundColor: context.appColors.error,
          side: BorderSide(color: context.appColors.error),
        ),
        label: const Text('Sign out'),
      ),
      const SizedBox(height: 20),
      Center(
        child: Text(
          'ThesisFormat · Version 1.0.0',
          style: TextStyle(
            color: context.appColors.textSecondary,
            fontSize: 11,
          ),
        ),
      ),
    ];
    if (embedded) {
      return ListView(
        padding: const EdgeInsets.fromLTRB(20, 28, 20, 24),
        children: [
          const Text(
            'Profile',
            style: TextStyle(fontSize: 22, fontWeight: FontWeight.w800),
          ),
          const SizedBox(height: 24),
          ...children,
        ],
      );
    }
    return Scaffold(
      appBar: AppBar(title: const Text('Profile')),
      body: ListView(padding: const EdgeInsets.all(20), children: children),
    );
  }
}

class _ProfileAction extends StatelessWidget {
  const _ProfileAction({
    required this.icon,
    required this.label,
    required this.onTap,
  });
  final IconData icon;
  final String label;
  final VoidCallback onTap;
  @override
  Widget build(BuildContext context) {
    final color = label == 'Edit Profile' || label == 'About the App'
        ? context.appColors.purple
        : context.appColors.primaryExtraDark;
    return ListTile(
      leading: Icon(icon, color: color),
      title: Text(
        label,
        style: const TextStyle(fontWeight: FontWeight.w600, fontSize: 14),
      ),
      trailing: Icon(
        Icons.chevron_right_rounded,
        color: context.appColors.textSecondary,
      ),
      onTap: onTap,
    );
  }
}