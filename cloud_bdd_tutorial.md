# Créer et se connecter à une base de données Cloud

## Connexion à une base de données Azure

Commencez par rassembler les informations de connexion nécessaires pour votre base Azure : nom du serveur, nom de la base, nom d’utilisateur et mot de passe.

## Connexion avec DBeaver

1. Ouvrez DBeaver et cliquez sur le bouton « New Database Connection ».
2. Sélectionnez le type de base (par ex. PostgreSQL, MySQL, etc.) correspondant à votre serveur Azure. Dans cet exemple, nous utilisons MySQL.
3. Renseignez les champs de connexion :
   - **Host** : le nom de votre serveur Azure (ex. `votre-serveur.mysql.database.azure.com`)
   - **Port** : 3306 (par défaut pour MySQL)
   - **Database** : le nom de la base (vous pouvez laisser vide pour lister/sélectionner ensuite)
   - **Username** : votre utilisateur (ex. `votreutilisateur@votre-serveur`). Défini lors de la création du serveur.
   - **Password** : votre mot de passe. Défini lors de la création du serveur.
4. Cliquez sur « Test Connection » pour vérifier l’accès.
5. Si c’est ok, cliquez sur « Finish » pour enregistrer la connexion.

Si vous voyez une erreur SSL du type :

>> Connections using insecure transport are prohibited while --require_secure_transport=ON.

Vous avez deux possibilités :

### Option 1 : dans DBeaver

Dans l’onglet « Driver Properties », ajustez les propriétés :
- **useSSL** : true

Même si la valeur est déjà à `true`, passez-la à `false`, appliquez, puis repassez à `true` et ré-appliquez. (Cela force parfois le driver à réévaluer la configuration SSL ; il est de notoriété publique que la config JSON n’est pas toujours parsée correctement du premier coup dans DBeaver.)

### Option 2 : dans le portail Azure

1. Allez dans le Portail Azure, ouvrez votre serveur MySQL et ses paramètres.
2. Recherchez le paramètre `require_secure_transport` et mettez-le à OFF. Ce n’est pas recommandé en production, mais cela reste acceptable pour de l’apprentissage/test.


## Création d’une base et d’une table

Notre application aura des utilisateurs avec un identifiant et un mot de passe. Nous allons créer une table « users » pour stocker ces informations.

1. Dans DBeaver, clic droit sur votre connexion > « SQL Editor » > « New SQL Script ».
2. Saisissez les commandes suivantes pour créer la table `users` :
```sql
-- Créer la base si elle n’existe pas
CREATE DATABASE IF NOT EXISTS my_app;

-- Se positionner sur la base de travail
USE my_app;

-- Créer la table users si elle n’existe pas
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY, -- Identifiant unique de l’utilisateur
    username VARCHAR(50) NOT NULL UNIQUE, -- Le nom d’utilisateur doit être unique
    password_hash VARCHAR(255) NOT NULL, -- Stocker le mot de passe haché
    email VARCHAR(100), -- Champ email optionnel
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP(), -- Date de création
    last_login TIMESTAMP NULL, -- Dernière connexion
    is_active BOOLEAN DEFAULT TRUE -- Utilisateur actif ou non
);

-- Visualiser la table
SELECT * FROM my_app.users;
```

### Exercice

Écrivez un script Python qui se connecte à la base et permet :
- d’insérer un nouvel utilisateur avec un mot de passe hashé ;
- de se connecter en vérifiant l’identifiant et le mot de passe.

Recommandations :
- Utilisez de préférence la bibliothèque `SQLAlchemy` pour la connexion.
- Utilisez la bibliothèque `hashlib` pour hacher les mots de passe avant insertion.
- Créez un module `mysql_app_func.py` qui contiendra les fonctions d’accès à la base.
- Vous pouvez avoir un notebook à côté pour tester les fonctions. Dans ce cas, placez ces magics au début du notebook pour recharger le module à chaque exécution :
```python
%load_ext autoreload
%autoreload 2
```
Fonctions à créer :
- Stocker les paramètres de connexion dans `params.yaml`.
- Stocker les informations sensibles (ex. mot de passe) dans `secrets.yaml` (ne pas versionner sur git !).
- `load_yaml(file_path: str) -> Dict[str, Any]` pour lire un fichier YAML.
- `create_db_engine(params: Dict[str, Any], secrets: Dict[str, Any]) -> Any` pour créer l’engine.
- `hash_password(password: str) -> str` pour hacher les mots de passe.
- `insert_user(username: str, password: str, email: str) -> bool` pour insérer un utilisateur (mot de passe haché obligatoire).
- `login(username: str, password: str) -> bool`.

## Stockage

Créez un stockage Blob Azure pour enregistrer les fichiers uploadés par les utilisateurs.

### Exercice

Écrivez un script Python qui se connecte à Azure Blob Storage et permet d’envoyer et de télécharger des fichiers. Créez d’abord un jeton avec les permissions appropriées pour accéder au stockage.

https://learn.microsoft.com/en-us/azure/storage/blobs/storage-blob-upload-python