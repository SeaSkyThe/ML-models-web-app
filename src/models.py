import pickle
import pandas as pd
import sklearn as sk
import numpy as np

from compressor import *
from db import *

from flask_pymongo import pymongo
from pymongo.server_api import ServerApi


N_NEIGHBORS = 11

class Singleton(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]

class Model(metaclass=Singleton):
	def __init__(self, model_type=1):
		self.model_type = model_type # model_types = {1: KNN_COLABORATIVE FILTERING; 2: KNN_CONTENT_BASED_GENRES; 3: KNN_CONTENT_BASED_TAGS}
		self.data_and_model = None

		self.db = Database()


	def load_data_and_model(self):
		self.data_and_model = self.db.get_data_and_models_from_db() #pegando dicionario com os objetos que representam os dados e o modelo
		
		return self.data_and_model

	def generate_recommendations(self, movie_name, printable=True):
		if(self.model_type==1):
			lista_recomendacoes = []
			# Carregando o modelo e os dados
			if(self.data_and_model == None):
				self.data_and_model = self.load_data_and_model()
			#TALVEZ DA PRA SUBSTITUIR O USO DE CHAVE ESPECIFICA POR VARIAVEIS GLOBAIS NAS 3 LINHAS ABAIXO: TODO
			model = self.data_and_model['knn_cf'] 
			movie_user_matrix = self.data_and_model['movie_user_matrix']
			data = self.data_and_model['movies_cf']


			# Pegando o Id do filme que tenha o nome passado
			movieId = data.loc[data["title"] == movie_name]["movieId"].values[0]
		    
			distances, suggestions = model.kneighbors(movie_user_matrix.getrow(movieId).todense().tolist(), n_neighbors=N_NEIGHBORS)
		    
			
			for i in range(0, len(distances.flatten())):
				if(i == 0):
					if(printable):
						print('Recomendações para {0} (ID: {1}): \n '.format(movie_name, movieId))
				else:
					#caso sejam geradas menos que N_NEIGHBORS recomendações, exibem-se apenas as geradas
					if(np.size(data.loc[data["movieId"] == suggestions.flatten()[i]]["title"].values) > 0 and np.size(data.loc[data["movieId"] == suggestions.flatten()[i]]["movieId"].values[0]) > 0):
						if(printable):
							print('{0}: {1} (ID: {2}), com distância de {3} '.format(i, data.loc[data["movieId"] == suggestions.flatten()[i]]["title"].values[0], data.loc[data["movieId"] == suggestions.flatten()[i]]["movieId"].values[0], distances.flatten()[i]))
						lista_recomendacoes.append('{0}: {1} (ID: {2}), com distância de {3} \n '.format(i, data.loc[data["movieId"] == suggestions.flatten()[i]]["title"].values[0], data.loc[data["movieId"] == suggestions.flatten()[i]]["movieId"].values[0], distances.flatten()[i])) 
			
			return distances, suggestions, lista_recomendacoes

# class Model():
# 	def __init__(self, path_to_model, model_type=1):
# 		self.path_to_model = path_to_model
# 		self.model_type = model_type # model_types = {1: KNN_COLABORATIVE FILTERING; 2: KNN_CONTENT_BASED_GENRES; 3: KNN_CONTENT_BASED_TAGS}
# 		self.model = None

# 	def load_model(self):
# 		with open(self.path_to_model, 'rb') as model_file:
# 			self.model = pickle.load(model_file)

# 		return self.model

# 	def generate_recommendations(self, movie_name, printable=True):
# 		if(self.model_type==1):
# 			lista_recomendacoes = []
# 			# Carregando o modelo
# 			model = self.load_model()
# 			# Carregando os dados
# 			with open("src/data/movies_cf.pkl", 'rb') as d:
# 				data = pickle.load(d)

# 			with open("src/data/movie_user_matrix_cf.pkl", 'rb') as m:
# 				movie_user_matrix = pickle.load(m)

# 			# Pegando o Id do filme que tenha o nome passado
# 			movieId = data.loc[data["title"] == movie_name]["movieId"].values[0]
		    
# 			distances, suggestions = model.kneighbors(movie_user_matrix.getrow(movieId).todense().tolist(), n_neighbors=N_NEIGHBORS)
		    
			
# 			for i in range(0, len(distances.flatten())):
# 				if(i == 0):
# 					if(printable):
# 						print('Recomendações para {0} (ID: {1}): \n '.format(movie_name, movieId))
# 				else:
# 					#caso sejam geradas menos que N_NEIGHBORS recomendações, exibem-se apenas as geradas
# 					if(np.size(data.loc[data["movieId"] == suggestions.flatten()[i]]["title"].values) > 0 and np.size(data.loc[data["movieId"] == suggestions.flatten()[i]]["movieId"].values[0]) > 0):
# 						if(printable):
# 							print('{0}: {1} (ID: {2}), com distância de {3} '.format(i, data.loc[data["movieId"] == suggestions.flatten()[i]]["title"].values[0], data.loc[data["movieId"] == suggestions.flatten()[i]]["movieId"].values[0], distances.flatten()[i]))
# 						lista_recomendacoes.append('{0}: {1} (ID: {2}), com distância de {3} \n '.format(i, data.loc[data["movieId"] == suggestions.flatten()[i]]["title"].values[0], data.loc[data["movieId"] == suggestions.flatten()[i]]["movieId"].values[0], distances.flatten()[i])) 
			
# 			return distances, suggestions, lista_recomendacoes

	# def generate_recommendations(self, movie_name, printable=True):
	# 	if(self.model_type==1):
	# 		lista_recomendacoes = []
	# 		# Carregando o modelo
	# 		model = self.load_model()
	# 		# Carregando os dados
	# 		with open("src/data/movies_cf.pkl", 'rb') as d:
	# 			data = pickle.load(d)

	# 		with open("src/data/movie_user_matrix_cf.pkl", 'rb') as m:
	# 			movie_user_matrix = pickle.load(m)

	# 		# Pegando o Id do filme que tenha o nome passado
	# 		movieId = data.loc[data["title"] == movie_name]["movieId"].values[0]
		    
	# 		distances, suggestions = model.kneighbors(movie_user_matrix.getrow(movieId).todense().tolist(), n_neighbors=N_NEIGHBORS)
		    
			
	# 		for i in range(0, len(distances.flatten())):
	# 			if(i == 0):
	# 				if(printable):
	# 					print('Recomendações para {0} (ID: {1}): \n '.format(movie_name, movieId))
	# 			else:
	# 				#caso sejam geradas menos que N_NEIGHBORS recomendações, exibem-se apenas as geradas
	# 				if(np.size(data.loc[data["movieId"] == suggestions.flatten()[i]]["title"].values) > 0 and np.size(data.loc[data["movieId"] == suggestions.flatten()[i]]["movieId"].values[0]) > 0):
	# 					if(printable):
	# 						print('{0}: {1} (ID: {2}), com distância de {3} '.format(i, data.loc[data["movieId"] == suggestions.flatten()[i]]["title"].values[0], data.loc[data["movieId"] == suggestions.flatten()[i]]["movieId"].values[0], distances.flatten()[i]))
	# 					lista_recomendacoes.append('{0}: {1} (ID: {2}), com distância de {3} \n '.format(i, data.loc[data["movieId"] == suggestions.flatten()[i]]["title"].values[0], data.loc[data["movieId"] == suggestions.flatten()[i]]["movieId"].values[0], distances.flatten()[i])) 
			
	# 		return distances, suggestions, lista_recomendacoes


