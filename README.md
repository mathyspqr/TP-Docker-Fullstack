# Todo App Flask ReactJS Docker

## Prérequis

Avant de commencer, assurez-vous d'avoir installé les éléments suivants :

- [Docker](https://www.docker.com/get-started)
- [Docker Compose](https://docs.docker.com/compose/install/)

## Installation

1. Clonez le dépôt :

  ```bash
  git clone https://github.com/mathyspqr/todo-app-flask-reactjs.git
  cd todo-app-flask-reactjs
  ```

2. Construisez et démarrez les conteneurs Docker :

  ```bash
  docker-compose up --build
  ```

3. Accédez à l'application dans votre navigateur à l'adresse suivante :

  ```
  http://localhost:3000
  ```

## Structure du projet

- `frontend/` - Contient le code ReactJS pour l'interface utilisateur avec son propre Dockerfile.
- `backend/` - Contient le code Flask pour l'API avec son propre Dockerfile.
- `docker-compose.yml` - Fichier de configuration pour Docker Compose.

## Utilisation

- Pour arrêter les conteneurs, utilisez :

  ```bash
  docker-compose down
  ```

- Pour reconstruire les conteneurs après avoir apporté des modifications au code, utilisez :

  ```bash
  docker-compose up --build
  ```

## Reverse Proxy et Base de Données

Ce projet utilise un reverse proxy pour diriger le trafic vers les conteneurs appropriés. Le reverse proxy est configuré à l'aide de Nginx et est défini dans le fichier `docker-compose.yml`. Cela permet de simplifier l'accès à l'application et de gérer les requêtes de manière efficace.

### Base de Données MySQL

L'application utilise une base de données MySQL pour stocker les données. Le conteneur MySQL est également défini dans le fichier `docker-compose.yml`. Voici comment la base de données est mise en place :

1. Le service MySQL est défini dans `docker-compose.yml` avec les configurations nécessaires telles que le nom de la base de données, l'utilisateur et le mot de passe.
2. Un conteneur phpMyAdmin est également configuré pour gérer la base de données via une interface web.

### Configuration dans `config.py` de Flask

La configuration de la base de données MySQL dans Flask est définie dans le fichier `config.py`. Voici un exemple de configuration :

```python
import os

class Config:
  SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'mysql+pymysql://user:password@db/todoapp')
  SQLALCHEMY_TRACK_MODIFICATIONS = False
```

Cette configuration utilise les variables d'environnement pour définir l'URI de la base de données, J'ai utilisé la dépendance SQLAlchemy pour interagir avec la base de données MySQL.

### Configuration dans `docker-compose.yml`

```yaml
version: '3.8'

services:
  reverse-proxy:
    image: nginx:latest
    ports:
      - "80:80"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
    depends_on:
      - frontend
      - backend
```

### Accès à phpMyAdmin

Pour accéder à phpMyAdmin et gérer la base de données MySQL, ouvrez votre navigateur et allez à l'adresse suivante :

```
http://localhost:8080
```

Utilisez les informations d'identification configurées dans le fichier `docker-compose.yml` pour vous connecter.

## Healthchecks

Des healthchecks sont mis en place pour s'assurer que les conteneurs fonctionnent correctement. Ces vérifications permettent de redémarrer automatiquement les conteneurs en cas de défaillance. Les healthchecks sont définis dans le fichier `docker-compose.yml` pour les services critiques tels que le backend et la base de données.

### Exemple de Healthcheck pour le Backend

```yaml
services:
  backend:
    build: ./backend
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:5000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
```

## Dockerfile

Chaque service de l'application a son propre Dockerfile qui définit l'environnement et les étapes nécessaires pour construire l'image Docker. Voici un aperçu des Dockerfiles pour le frontend et le backend.

### Dockerfile pour le Frontend

```dockerfile
# Utilise une image de base Node.js
FROM node:14

# Définit le répertoire de travail
WORKDIR /app

# Copie les fichiers package.json et package-lock.json
COPY package*.json ./

# Installe les dépendances
RUN npm install

# Copie le reste des fichiers de l'application
COPY . .

# Construit l'application pour la production
RUN npm run build

# Expose le port 3000
EXPOSE 3000

# Démarre l'application
CMD ["npm", "start"]
```

### Dockerfile pour le Backend

```dockerfile
# Utilise une image de base Python
FROM python:3.8-slim

# Définit le répertoire de travail
WORKDIR /app

# Copie le fichier requirements.txt
COPY requirements.txt ./

# Installe les dépendances
RUN pip install --no-cache-dir -r requirements.txt

# Copie le reste des fichiers de l'application
COPY . .

# Expose le port 5000
EXPOSE 5000

# Démarre l'application
CMD ["python", "app.py"]
```

## Docker Compose

Le fichier `docker-compose.yml` est utilisé pour définir et gérer les services Docker de l'application. Il permet de configurer les conteneurs, les réseaux, les volumes et les dépendances entre les services.

### Exemple de Configuration dans `docker-compose.yml`

```yaml
version: '3.8'

services:
  backend:
    build: ./backend
    ports:
      - "5000:5000"
    environment:
      MYSQL_HOST: mysql
      MYSQL_USER: user
      MYSQL_PASSWORD: password
      MYSQL_DATABASE: mydb
    networks:
      - app_network
    depends_on:
      - mysql
      - migrate
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:5000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    networks:
      - app_network
    depends_on:
      - backend
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:3000"]
      interval: 30s
      timeout: 10s
      retries: 3

  mysql:
    image: mysql:8.0
    environment:
      MYSQL_ROOT_PASSWORD: rootpassword
      MYSQL_DATABASE: mydb
      MYSQL_USER: user
      MYSQL_PASSWORD: password
    volumes:
      - mysql_data:/var/lib/mysql
    networks:
      - app_network
    healthcheck:
      test: ["CMD", "mysqladmin", "ping", "-h", "localhost"]
      interval: 30s
      timeout: 10s
      retries: 3

  phpmyadmin:
    image: phpmyadmin/phpmyadmin
    environment:
      PMA_HOST: mysql
      MYSQL_ROOT_PASSWORD: rootpassword
    ports:
      - "8081:80"
    networks:
      - app_network

  migrate:
    build: ./backend
    command: flask db upgrade
    environment:
      MYSQL_HOST: mysql
      MYSQL_USER: user
      MYSQL_PASSWORD: password
      MYSQL_DATABASE: mydb
    networks:
      - app_network
    depends_on:
      - mysql

  nginx:
    image: nginx:latest
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
    ports:
      - "80:80"
    networks:
      - app_network
    depends_on:
      - frontend
      - backend
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost"]
      interval: 30s
      timeout: 10s
      retries: 3

networks:
  app_network:
    driver: bridge

volumes:
  mysql_data:
```

### Explication de la Configuration

- `version: '3.8'`: Spécifie la version de Docker Compose à utiliser.
- `services`: Définit les différents services de l'application.

  - `backend`: Service pour l'application Flask.
    - `build`: Chemin vers le Dockerfile du backend.
    - `ports`: Mappe le port 5000 du conteneur au port 5000 de l'hôte.
    - `environment`: Définit les variables d'environnement pour MySQL.
    - `depends_on`: Indique que le service backend dépend des services mysql et migrate.
    - `healthcheck`: Vérifie la santé du service backend.

  - `frontend`: Service pour l'application ReactJS.
    - `build`: Chemin vers le Dockerfile du frontend.
    - `ports`: Mappe le port 3000 du conteneur au port 3000 de l'hôte.
    - `depends_on`: Indique que le service frontend dépend du service backend.
    - `healthcheck`: Vérifie la santé du service frontend.

  - `mysql`: Service pour la base de données MySQL.
    - `image`: Utilise l'image MySQL version 8.0.
    - `environment`: Définit les variables d'environnement pour MySQL.
    - `volumes`: Monte le volume `mysql_data` pour persister les données.
    - `healthcheck`: Vérifie la santé du service MySQL.

  - `phpmyadmin`: Service pour phpMyAdmin.
    - `image`: Utilise l'image phpMyAdmin.
    - `environment`: Définit les variables d'environnement pour phpMyAdmin.
    - `ports`: Mappe le port 8081 du conteneur au port 80 de l'hôte.

  - `migrate`: Service pour exécuter les migrations de la base de données.
    - `build`: Chemin vers le Dockerfile du backend.
    - `command`: Commande pour exécuter les migrations.
    - `environment`: Définit les variables d'environnement pour MySQL.
    - `depends_on`: Indique que le service migrate dépend du service mysql.

  - `nginx`: Service pour le reverse proxy Nginx.
    - `image`: Utilise l'image Nginx.
    - `volumes`: Monte le fichier de configuration Nginx.
    - `ports`: Mappe le port 80 du conteneur au port 80 de l'hôte.
    - `depends_on`: Indique que le service nginx dépend des services frontend et backend.
    - `healthcheck`: Vérifie la santé du service Nginx.

- `networks`: Définit le réseau `app_network` utilisé par les services.
- `volumes`: Définit le volume `mysql_data` pour persister les données MySQL.
