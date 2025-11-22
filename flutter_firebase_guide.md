# Flutter + Firebase Grundgerüst für Hausmeister-App

Dieses Dokument fasst eine einfache Basis-Struktur für eine Flutter-App mit Firebase (Authentication + Firestore) zusammen. Die Erklärungen sind in einfachen Worten gehalten.

## 1) Sinnvolle Projektstruktur

```
lib/
  main.dart                // Einstiegspunkt, Firebase-Init, Routing
  app.dart                 // MaterialApp, Routen-Setup
  services/
    firebase_service.dart  // Firebase-Initialisierung, Auth-Wrapper
  models/
    customer.dart          // Datenmodell Kunde
    job.dart               // Datenmodell Auftrag
  screens/
    auth/
      login_screen.dart    // Login/Registrierung
    home/home_screen.dart  // nach Login: Tabs/Navigation
    customers/
      customer_list_screen.dart // Liste der Kunden
    jobs/
      job_list_screen.dart      // Liste der Aufträge mit Filter
      job_calendar_screen.dart  // einfache Terminübersicht (nach Datum sortiert)
  widgets/
    job_status_filter.dart // kleiner Filter-Widget für offen/erledigt
```

**Warum so?**
- `models` trennt die Datenklassen von der UI.
- `screens` enthält jeweils ganze Bildschirmseiten.
- `widgets` enthält kleinere, wiederverwendbare Teile.
- `services` sammelt alles rund um Firebase, damit der Rest des Codes sauber bleibt.

## 2) pubspec.yaml (Ausschnitt)

```yaml
dependencies:
  flutter:
    sdk: flutter
  firebase_core: ^3.1.1
  firebase_auth: ^5.1.2
  cloud_firestore: ^5.1.0
  provider: ^6.1.2        # einfache State-Verwaltung
  intl: ^0.19.0           # Datumsformatierung für die Terminliste
```

## 3) Beispiel `main.dart`

```dart
import 'package:flutter/material.dart';
import 'package:firebase_core/firebase_core.dart';
import 'package:firebase_auth/firebase_auth.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  await Firebase.initializeApp();
  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Hausmeister App',
      theme: ThemeData(primarySwatch: Colors.blue),
      home: const AuthGate(),
    );
  }
}

class AuthGate extends StatelessWidget {
  const AuthGate({super.key});

  @override
  Widget build(BuildContext context) {
    return StreamBuilder<User?>(
      stream: FirebaseAuth.instance.authStateChanges(),
      builder: (context, snapshot) {
        if (snapshot.connectionState == ConnectionState.waiting) {
          return const Scaffold(
            body: Center(child: CircularProgressIndicator()),
          );
        }
        if (snapshot.hasData) {
          return const HomeScreen();
        }
        return const LoginScreen();
      },
    );
  }
}

class LoginScreen extends StatefulWidget {
  const LoginScreen({super.key});

  @override
  State<LoginScreen> createState() => _LoginScreenState();
}

class _LoginScreenState extends State<LoginScreen> {
  final emailController = TextEditingController();
  final passwordController = TextEditingController();
  bool isLogin = true;
  String? error;

  Future<void> _submit() async {
    setState(() => error = null);
    try {
      if (isLogin) {
        await FirebaseAuth.instance.signInWithEmailAndPassword(
          email: emailController.text,
          password: passwordController.text,
        );
      } else {
        await FirebaseAuth.instance.createUserWithEmailAndPassword(
          email: emailController.text,
          password: passwordController.text,
        );
      }
    } on FirebaseAuthException catch (e) {
      setState(() => error = e.message);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text(isLogin ? 'Login' : 'Registrieren')),
      body: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          children: [
            TextField(
              controller: emailController,
              decoration: const InputDecoration(labelText: 'E-Mail'),
            ),
            const SizedBox(height: 12),
            TextField(
              controller: passwordController,
              obscureText: true,
              decoration: const InputDecoration(labelText: 'Passwort'),
            ),
            if (error != null) ...[
              const SizedBox(height: 8),
              Text(error!, style: const TextStyle(color: Colors.red)),
            ],
            const SizedBox(height: 20),
            ElevatedButton(
              onPressed: _submit,
              child: Text(isLogin ? 'Einloggen' : 'Registrieren'),
            ),
            TextButton(
              onPressed: () => setState(() => isLogin = !isLogin),
              child: Text(isLogin
                  ? 'Noch kein Konto? Jetzt registrieren'
                  : 'Schon ein Konto? Jetzt einloggen'),
            ),
          ],
        ),
      ),
    );
  }
}

class HomeScreen extends StatelessWidget {
  const HomeScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Home'),
        actions: [
          IconButton(
            icon: const Icon(Icons.logout),
            onPressed: () => FirebaseAuth.instance.signOut(),
          )
        ],
      ),
      body: ListView(
        children: const [
          ListTile(
            leading: Icon(Icons.people),
            title: Text('Kundenliste'),
            subtitle: Text('Alle Kunden anzeigen'),
          ),
          ListTile(
            leading: Icon(Icons.work),
            title: Text('Aufträge'),
            subtitle: Text('Offen/erledigt filtern'),
          ),
        ],
      ),
    );
  }
}
```

## 4) Beispiel-Screens

### Kundenliste

```dart
import 'package:flutter/material.dart';
import 'package:cloud_firestore/cloud_firestore.dart';

class CustomerListScreen extends StatelessWidget {
  const CustomerListScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Kunden')),
      body: StreamBuilder<QuerySnapshot>(
        stream: FirebaseFirestore.instance
            .collection('customers')
            .orderBy('name')
            .snapshots(),
        builder: (context, snapshot) {
          if (snapshot.connectionState == ConnectionState.waiting) {
            return const Center(child: CircularProgressIndicator());
          }
          final docs = snapshot.data?.docs ?? [];
          if (docs.isEmpty) {
            return const Center(child: Text('Noch keine Kunden'));
          }
          return ListView.builder(
            itemCount: docs.length,
            itemBuilder: (context, index) {
              final data = docs[index].data() as Map<String, dynamic>;
              return ListTile(
                title: Text(data['name'] ?? ''),
                subtitle: Text(data['address'] ?? ''),
              );
            },
          );
        },
      ),
    );
  }
}
```

### Auftragsliste mit Filter (offen/erledigt)

```dart
import 'package:flutter/material.dart';
import 'package:cloud_firestore/cloud_firestore.dart';

class JobListScreen extends StatefulWidget {
  const JobListScreen({super.key});

  @override
  State<JobListScreen> createState() => _JobListScreenState();
}

class _JobListScreenState extends State<JobListScreen> {
  String statusFilter = 'alle';

  @override
  Widget build(BuildContext context) {
    Query<Map<String, dynamic>> query =
        FirebaseFirestore.instance.collection('jobs').orderBy('date');
    if (statusFilter == 'offen') {
      query = query.where('status', isEqualTo: 'offen');
    } else if (statusFilter == 'erledigt') {
      query = query.where('status', isEqualTo: 'erledigt');
    }

    return Scaffold(
      appBar: AppBar(
        title: const Text('Aufträge'),
        actions: [
          PopupMenuButton<String>(
            onSelected: (value) => setState(() => statusFilter = value),
            itemBuilder: (context) => const [
              PopupMenuItem(value: 'alle', child: Text('Alle')),
              PopupMenuItem(value: 'offen', child: Text('Offen')),
              PopupMenuItem(value: 'erledigt', child: Text('Erledigt')),
            ],
          ),
        ],
      ),
      body: StreamBuilder<QuerySnapshot<Map<String, dynamic>>>(
        stream: query.snapshots(),
        builder: (context, snapshot) {
          if (snapshot.connectionState == ConnectionState.waiting) {
            return const Center(child: CircularProgressIndicator());
          }
          final docs = snapshot.data?.docs ?? [];
          if (docs.isEmpty) {
            return const Center(child: Text('Keine Aufträge'));
          }
          return ListView.builder(
            itemCount: docs.length,
            itemBuilder: (context, index) {
              final data = docs[index].data();
              return ListTile(
                title: Text(data['title'] ?? ''),
                subtitle: Text('${data['customerName'] ?? ''} — ${data['address'] ?? ''}'),
                trailing: Text(data['status'] ?? ''),
              );
            },
          );
        },
      ),
    );
  }
}
```

**Warum diese Felder?**
- `status` als Text ("offen"/"erledigt") ist einfach zu filtern.
- `date` als Timestamp erlaubt Sortieren und Kalender-Ansicht.

## 5) Firestore-Schema (Sammlungen & Felder)

```json
{
  "customers": {
    "<customerId>": {
      "name": "Muster GmbH",
      "address": "Hauptstraße 1, 12345 Stadt",
      "contact": "max@muster.de",
      "phone": "+49 123 456"
    }
  },
  "jobs": {
    "<jobId>": {
      "customerId": "<customerId>",
      "customerName": "Muster GmbH", // kopiert für einfachere Anzeige
      "title": "Heizung warten",
      "description": "Filter wechseln, Anlage prüfen",
      "address": "Hauptstraße 1, 12345 Stadt",
      "status": "offen", // oder "erledigt"
      "date": "Timestamp", // z.B. serverTimestamp()
      "assignee": "<uid des Mitarbeiters>",
      "assigneeName": "Anna Beispiel"
    }
  },
  "users": {
    "<uid>": {
      "name": "Anna Beispiel",
      "role": "techniker" // ggf. für Rechte
    }
  }
}
```

**Warum Kopie von `customerName` im Auftrag?** So muss die UI nicht für jede Zeile einen extra Lookup machen und bleibt schneller.

## 6) Schritt-für-Schritt Anleitung

1. **Neues Flutter-Projekt anlegen**
   - Installiere Flutter SDK.
   - Terminal öffnen und ausführen:
     - `flutter create hausmeister_app`
   - Im neuen Ordner arbeiten: `cd hausmeister_app`

2. **Pakete eintragen**
   - Öffne `pubspec.yaml` und füge unter `dependencies` die Pakete aus Abschnitt 2 hinzu.
   - Speichere die Datei und hole die Pakete: `flutter pub get`.

3. **Firebase-Projekt anlegen**
   - Gehe auf https://console.firebase.google.com und erstelle ein neues Projekt.
   - Aktiviere **Authentication** (E-Mail/Passwort) und **Firestore** (Native-Modus).

4. **Firebase in Flutter einrichten**
   - Installiere das CLI-Tool `firebase-tools` (optional) oder nutze den Web-Assistenten in der Firebase-Konsole.
   - Lade die Plattform-Dateien herunter:
     - Android: `google-services.json` in `android/app/` legen.
     - iOS: `GoogleService-Info.plist` in `ios/Runner/` legen.
   - Füge die Gradle-Änderungen laut Firebase-Dokumentation hinzu (classpath in `android/build.gradle`, Plugin `com.google.gms.google-services` in `android/app/build.gradle`).
   - Für iOS einmal `cd ios && pod install && cd ..` ausführen.

5. **Code einfügen**
   - Ersetze den Inhalt von `lib/main.dart` durch den Code aus Abschnitt 3.
   - Lege zusätzliche Dateien wie `customer_list_screen.dart` und `job_list_screen.dart` an (siehe Abschnitt 4) und binde sie in dein Routing ein.

6. **App starten (Emulator oder Gerät)**
   - Stelle sicher, dass ein Emulator läuft oder ein Gerät per USB verbunden ist (`flutter devices`).
   - Starte die App: `flutter run`.
   - Nach dem Start kannst du dich registrieren, einloggen und die Beispiel-Screens öffnen.

Fertig! Du hast jetzt ein einfaches Grundgerüst, das du Schritt für Schritt erweitern kannst.
