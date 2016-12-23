# Projet SIW

## Libraries utilisées
- SPARQLWrapper
- haversine
- django-rest-framework
- django-cors-headers
- cordova-plugin-whitelist
- Googlemaps JavaScript API

## Localisation du code
- Dossier carproject -> Code du serveur django
- Dossier UI -> Code du client cordova (application mobile)
- Fichier carproject/finder/views.py -> Vue de l'application, Contient les requêtes SPARQL et le calcule des prix du devis
- Fichier UI/www/index.html -> Point d'entrée client, contient :
    - la logique de navigation entre les differentes pages du projet (JavaScript)
    - les requête Ajax sur le serveur
    - les requetes sur la Googlemaps JavaScript API

## Tests (Developpeurs)
- Utiliser l'adresse http://10.0.2.2:8000/ pour tester l'appli dans l'emulateur.
- Utiliser l'adresse http://localhost:8000/ pour tester l'appli dans le navigateur.
