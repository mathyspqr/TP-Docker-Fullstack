# Utiliser une image de base Node.js
FROM node:16-alpine

# Définir le répertoire de travail dans le conteneur
WORKDIR /app

# Copier le fichier package.json et package-lock.json
COPY package*.json ./

# Installer les dépendances
RUN npm install

# Copier le reste des fichiers de l'application
COPY . .

# Exposer le port utilisé par l'application React (par défaut 3000)
EXPOSE 3000

# Démarrer l'application en mode développement
CMD ["npm", "run", "dev"]