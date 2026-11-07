# SmartGrades — Python, Tkinter et SQLite

SmartGrades est un prototype d'application de bureau permettant de gérer les comptes des étudiants universitaires, les modules, les groupes et les notes. Il utilise **exactement trois tables dans la base de données** : `users`, `modules` et `grades`.

## Fonctionnalités incluses

- Connexion avec des interfaces distinctes pour les étudiants et les enseignants.
- Hachage des mots de passe avec PBKDF2-HMAC-SHA256.
- **Dashboard étudiant** : groupe, liste des modules, notes de contrôle continu et d'examen, moyennes des modules et moyenne semestrielle pondérée.
- **Dashboard enseignant** : consultation des modules attribués, saisie et modification des notes, consultation de la liste des étudiants et attribution des groupes.
- Clés étrangères SQLite, validation des notes et requêtes SQL paramétrées.
- Un enseignant peut être responsable de plusieurs modules.
- Aucun package tiers n'est nécessaire.

## Prérequis

- Python 3.10+ recommandé.
- Tkinter disponible dans votre installation Python.
- SQLite est utilisé via le module intégré `sqlite3` de Python.

## Lancer l'application

Exécutez les commandes suivantes depuis le dossier du projet :

```bash
python main.py
```

Cette commande initialise `database/students.db` si nécessaire, puis ouvre l'écran de connexion.

## Créer les données de démonstration

Exécutez cette commande depuis le dossier du projet pour créer ou actualiser les données locales de démonstration :

```bash
python -m demo.create_demo_users
```

Les données initiales comprennent :

- 60 étudiants fictifs répartis dans les groupes G1-G4.
- Cinq enseignants.
- Six modules.
- Des notes de contrôle continu et d'examen pour chaque étudiant.

Tous les comptes enseignants utilisent le mot de passe `TeacherDemo123!` et tous les comptes étudiants utilisent `StudentDemo123!`.

La liste complète des comptes est disponible dans [demo/DEMO_CREDENTIALS.txt](./demo/DEMO_CREDENTIALS.txt).

Une nouvelle exécution réinitialise les mots de passe de ces comptes de démonstration et complète les données manquantes.

Ces identifiants sont publics et destinés uniquement aux tests locaux. N'utilisez pas ce fichier ou ces comptes pour gérer de véritables informations étudiantes. Ne publiez jamais de données ou de mots de passe réels sur GitHub.

## Structure de la base de données

- `users` : comptes de connexion, rôles, informations d'identité et groupes des étudiants.
- `modules` : nom du module, coefficient et enseignant responsable (`teacher_id`).
- `grades` : notes de contrôle continu et d'examen pour chaque étudiant et module.

La base de données est créée par `database/database.py` à partir du fichier `database/schema.sql`.

Le fichier `students.db` contient les données utilisées à l'exécution et est volontairement ignoré par Git.

## Calcul des notes

- **Coefficient du contrôle continu** : 40 %
- **Coefficient de l'examen** : 60 %
- **Moyenne du module** :

  `moyenne = contrôle_continu × 0.40 + examen × 0.60`

- **Moyenne semestrielle** :

  `moyenne_semestre = somme(moyenne_module × coefficient) / somme(coefficients des modules dont les deux notes sont saisies)`

Les coefficients peuvent être modifiés dans `services/grade_service.py` afin de respecter les règles définies par votre professeur.

## Structure du projet

```text
SmartGrades/
├── main.py
├── database/
│   ├── database.py
│   └── schema.sql
├── demo/
│   ├── create_demo_users.py
│   └── DEMO_CREDENTIALS.txt
├── models/
│   ├── user.py
│   ├── module.py
│   └── grade.py
├── repositories/
│   ├── user_repository.py
│   ├── module_repository.py
│   └── grade_repository.py
├── services/
│   ├── auth_service.py
│   ├── module_service.py
│   └── grade_service.py
└── ui/
    └── main_window.py
```

## Publier le projet sur GitHub

```bash
git init
git add .
git commit -m "Initial SmartGrades application"
git branch -M master
git remote add origin <https://github.com/hard2007/projet.git>
git push -u origin master
```

## Limitations et périmètre du projet

Il s'agit d'un prototype réalisé dans le cadre d'un projet étudiant, et non d'un système d'authentification destiné à la production.

L'application permet actuellement aux enseignants de saisir les notes des modules qui leur sont attribués et d'affecter les étudiants à des groupes.

La création des modules est disponible via la couche `service` et le système de démonstration. Cependant, les fonctionnalités suivantes ne sont pas encore incluses :

- Formulaire complet de création de modules.
- Interface de gestion des comptes.
- Système de réinitialisation des mots de passe.
- Journalisation des actions conforme aux exigences d'un environnement de production.

La limitation à trois tables implique que les groupes sont stockés sous forme de texte dans les comptes des étudiants, plutôt que dans une table distincte `groups`.
