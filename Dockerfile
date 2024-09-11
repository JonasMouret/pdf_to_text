# Utiliser une image Python 3.12.5
FROM python:3.12.5-slim

# Définir le répertoire de travail
WORKDIR /app

# Créer un utilisateur non-root
RUN useradd -ms /bin/bash appuser

# Changer d'utilisateur
USER appuser

# Copier les fichiers requirements.txt et installer les dépendances
COPY --chown=appuser:appuser requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copier tout le contenu de l'application dans le conteneur
COPY --chown=appuser:appuser . .

# Exposer le port 5000 pour Gunicorn
EXPOSE 8080

# Commande pour démarrer l'application Flask avec Gunicorn
CMD ["gunicorn","--config", "gunicorn_config.py", "app:app"]
