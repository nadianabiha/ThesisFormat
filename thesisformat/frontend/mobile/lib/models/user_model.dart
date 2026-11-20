class UserModel {
  const UserModel({
    required this.id,
    required this.name,
    required this.email,
    this.username = '',
  });

  final String id;
  final String name;
  final String email;

  /// Dipakai untuk login selain email. Akun lama memakai email sebagai
  /// username.
  final String username;

  /// Nama yang ditampilkan: username. Akun lama (username = email)
  /// memakai nama yang tersimpan, atau bagian depan email.
  String get displayName {
    if (username.isNotEmpty && !username.contains('@')) return username;
    if (name.trim().isNotEmpty && !name.contains('@')) return name.trim();
    return email.split('@').first;
  }

  factory UserModel.fromJson(Map<String, dynamic> json) => UserModel(
    id: (json['id'] ?? '').toString(),
    name: (json['name'] ?? '') as String,
    email: (json['email'] ?? '') as String,
    username: (json['username'] ?? '') as String,
  );

  Map<String, dynamic> toJson() => {
    'id': id,
    'name': name,
    'username': username,
    'email': email,
  };
}
