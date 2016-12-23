# coding: utf8
from django.shortcuts import render
from django.views.generic import TemplateView, ListView, DetailView
from rest_framework.views import APIView
from rest_framework.response import Response
from SPARQLWrapper import SPARQLWrapper, JSON
from haversine import haversine
import json as j

# Vue de Tests, non utilisée pour le projet
class HomeView(TemplateView):
    template_name = "base.html"

    def get_context_data(self, **kwargs):
        context = super(HomeView,self).get_context_data(**kwargs)

        sparql = SPARQLWrapper("http://localhost:9091/sparql")
        sparql.setQuery("""
            SELECT DISTINCT ?lat ?long ?coeff WHERE {
              ?s <http://localhost:9091/projetsiw/c-users-angy-documents-djangodevenv-projetsiw-base-adresses#latitude> ?lat.
              ?s <http://localhost:9091/projetsiw/c-users-angy-documents-djangodevenv-projetsiw-base-adresses#longitude> ?long.
              ?s <http://localhost:9091/projetsiw/c-users-angy-documents-djangodevenv-projetsiw-base-adresses#coeff-total> ?coeff
            }
        """)
        sparql.setReturnFormat(JSON)
        results = sparql.query().convert()


        context['retour'] = j.dumps(results["results"]["bindings"])

        return context

#Vue utilisée dans le projet
#Represente notre API Rest
#Recupere les données de pieces, prestations et garages depuis les differents graphs rdf puis calcule les prix.
class APIHomeView(APIView):
    #Simple recuperation de logitude/latitudes/coeff des garages pour tests. Non utilisés dans le code final.
    def get(self, request, format=None):
        current_lat = 48.859029
        current_long = 2.408941

        sparql = SPARQLWrapper("http://localhost:9091/sparql")
        sparql.setQuery("""
            SELECT DISTINCT ?lat ?long ?coeff WHERE {
              ?s <http://localhost:9091/projetsiw/c-users-angy-documents-djangodevenv-projetsiw-base-adresses#latitude> ?lat.
              ?s <http://localhost:9091/projetsiw/c-users-angy-documents-djangodevenv-projetsiw-base-adresses#longitude> ?long.
              ?s <http://localhost:9091/projetsiw/c-users-angy-documents-djangodevenv-projetsiw-base-adresses#coeff-total> ?coeff
            }
        """)
        sparql.setReturnFormat(JSON)
        results = sparql.query().convert()

        subset = []
        second_subset = []
        cur_distance = 0
        max_coeff = 0

        for obj in results["results"]["bindings"]:
            cur_distance = haversine((48.859029,2.408941),(eval(obj["lat"]["value"]),eval(obj["long"]["value"])))
            if cur_distance < 5:
                subset.append(obj)

        for obj in subset:
            if len(second_subset)<10:
                second_subset.append(obj)
                if eval(obj["coeff"]["value"]) > max_coeff:
                    max_coeff = eval(obj["coeff"]["value"])
            else:
                if obj["coeff"]["value"] < max_coeff:
                    for idx,pointer in enumerate(second_subset):
                        if pointer["coeff"]["value"] == max_coeff:
                            second_subset[idx]=obj
                            break




        print(len(second_subset))

        return Response(second_subset)

    #Recupere les donnees envoyée par le client.
    #Recupere les informations depuis les graphs RDF
    #Retourne les prix calcules a partir des parametres entres (10 garages les moins chers dans un rayon de 10km.)
    def post(self, request, format=None):
        data = j.loads(request.data)
        print(request.data)
        print(data)

        current_lat = data["lat"]
        current_long = data["long"]

        #Recuperation des infos des garages.
        sparql = SPARQLWrapper("http://localhost:9091/sparql")
        sparql.setQuery("""
            SELECT DISTINCT ?lat ?long ?coeff ?nom ?adresse ?localite ?codepostal WHERE {
              ?s <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://localhost:9091/projetsiw/c-users-angy-documents-djangodevenv-projetsiw-base-adresses#c-users-angy-documents-djangodevenv-projetsiw-base-adresses>.
              ?s <http://localhost:9091/projetsiw/c-users-angy-documents-djangodevenv-projetsiw-base-adresses#latitude> ?lat.
              ?s <http://localhost:9091/projetsiw/c-users-angy-documents-djangodevenv-projetsiw-base-adresses#longitude> ?long.
              ?s <http://localhost:9091/projetsiw/c-users-angy-documents-djangodevenv-projetsiw-base-adresses#coeff-total> ?coeff.
              ?s <http://localhost:9091/projetsiw/c-users-angy-documents-djangodevenv-projetsiw-base-adresses#libelle-du-site> ?nom.
              ?s <http://localhost:9091/projetsiw/c-users-angy-documents-djangodevenv-projetsiw-base-adresses#adresse> ?adresse.
              ?s <http://localhost:9091/projetsiw/c-users-angy-documents-djangodevenv-projetsiw-base-adresses#localite> ?localite.
              ?s <http://localhost:9091/projetsiw/c-users-angy-documents-djangodevenv-projetsiw-base-adresses#code-postal> ?codepostal
            }
        """)
        sparql.setReturnFormat(JSON)
        results = sparql.query().convert()

        #Recuperation des informations des pieces
        sparql.setQuery("""
            SELECT DISTINCT ?piece ?coeff WHERE {
              ?s <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://localhost:9091/projetsiw/prix-pieces-csv#prix-pieces-csv>.
              ?s <http://localhost:9091/projetsiw/prix-pieces-csv#piece> ?piece.
              ?s <http://localhost:9091/projetsiw/prix-pieces-csv#coeff> ?coeff
            }
        """)
        results_pieces = sparql.query().convert()

        #Recuperation des informations des prestations
        sparql.setQuery("""
            SELECT DISTINCT ?presta ?prix WHERE {
              ?s <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://localhost:9091/projetsiw/prix-prestations-csv#prix-prestations-csv>.
              ?s <http://localhost:9091/projetsiw/prix-prestations-csv#prestation> ?presta.
              ?s <http://localhost:9091/projetsiw/prix-prestations-csv#prix> ?prix
            }
        """)
        results_presta = sparql.query().convert()

        subset = []
        second_subset = []
        cur_distance = 0
        max_coeff = 0

        #Initialisation de la structure de donnees des pieces
        piece = {}
        for obj in results_pieces["results"]["bindings"]:
            piece[obj["piece"]["value"]] = float(obj["coeff"]["value"])

        ##Initialisation de la structure de donnees des prestations
        prix={}
        for obj in results_presta["results"]["bindings"]:
            prix[obj["presta"]["value"]] = int(obj["prix"]["value"])

        #Initialisation de la structure de donnees des pieces
        #Reduction des resultats aux garages situes dans un rayon de 5Km
        for obj in results["results"]["bindings"]:
            cur_distance = haversine((48.859029,2.408941),(eval(obj["lat"]["value"]),eval(obj["long"]["value"])))
            if cur_distance < 5:
                subset.append(obj)

        #Stockage des 10 garages les moins cheres
        for obj in subset:
            if len(second_subset)<10:
                second_subset.append(obj)
                if eval(obj["coeff"]["value"]) > max_coeff:
                    max_coeff = eval(obj["coeff"]["value"])
            else:
                if obj["coeff"]["value"] < max_coeff:
                    for idx,pointer in enumerate(second_subset):
                        if pointer["coeff"]["value"] == max_coeff:
                            second_subset[idx]=obj
                            break

        #Calcul des prix pour les garages selectionnes
        for obj in second_subset:
            obj["prix"]=0
            for presta in data["reparations"]:
                obj["prix"]+=prix[presta["prestation"]]*piece[presta["piece"]]*float(obj["coeff"]["value"].replace(",","."))

        print(len(second_subset))

        return Response(second_subset)
