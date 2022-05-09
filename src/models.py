import pickle
import pandas as pd
import numpy as np
import sklearn 
from imdb import Cinemagoer #biblioteca utilizada para gerar o link baseado no nome do filme

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

import time
def timeit(method):
    def timed(*args, **kw):
        ts = time.time()
        result = method(*args, **kw)
        te = time.time()
        if 'log_time' in kw:
            name = kw.get('log_name', method.__name__.upper())
            kw['log_time'][name] = int((te - ts) * 1000)
        else:
            print ('%r  %2.2f ms' % \
                  (method.__name__, (te - ts) * 1000))
        return result
    return timed

#CLASSE RESPONSAVEL POR CARREGAR OS MODELOS E OS DADOS E GERAR AS RECOMENDAÇÕES
class Model(metaclass=Singleton):
	def __init__(self, model_type=1):
		self.model_type = model_type # model_types = {1: KNN_COLABORATIVE FILTERING; 2: KNN_CONTENT_BASED_GENRES; 3: KNN_CONTENT_BASED_TAGS}
		self.data_and_model = None

		self.db = Database()

		self.already_processed_recommendations = {}

	#@timeit
	def load_data_and_model(self):
		#se for diferente de None e não for uma Exception (erro)
		if(self.db != None and not isinstance(self.db, Exception)):
			self.data_and_model = self.db.get_data_and_models_from_db() #pegando dicionario com os objetos que representam os dados e o modelo
			return self.data_and_model
		else: #caso for uma Exception, retorna a exception
			return self.db

	#@timeit
	def generate_recommendations(self, movie_name, printable=True):
		if(self.model_type==1):
			if(movie_name in self.already_processed_recommendations.keys()):
				return self.already_processed_recommendations[movie_name][0], self.already_processed_recommendations[movie_name][1], self.already_processed_recommendations[movie_name][2]
			else:
				lista_recomendacoes = []
				# Carregando o modelo e os dados
				if(self.data_and_model == None):
					self.data_and_model = self.load_data_and_model()

				#Se os dados e o modelo foram carregados da maneira correta fazemos o processamento
				if(self.data_and_model != None and not isinstance(self.data_and_model, Exception)):
					#TALVEZ DA PRA SUBSTITUIR O USO DE CHAVE ESPECIFICA POR VARIAVEIS GLOBAIS NAS 3 LINHAS ABAIXO: TODO
					model = self.data_and_model['knn_cf'] 
					movie_user_matrix = self.data_and_model['movie_user_matrix']
					data = self.data_and_model['movies_cf']


					# Pegando o Id do filme que tenha o nome passado
					movieId = data.loc[data["title"] == movie_name]["movieId"].values[0]
				    
					distances, suggestions = model.kneighbors(movie_user_matrix.getrow(movieId).todense().tolist(), n_neighbors=N_NEIGHBORS)
				    
				
					#Criando objeto imdb
					ia = Cinemagoer()
					for i in range(0, len(distances.flatten())):
						if(i == 0):
							if(printable):
								print('Recomendações para {0} (ID: {1}): \n '.format(movie_name, movieId))
						else:
							#caso sejam geradas menos que N_NEIGHBORS recomendações, exibem-se apenas as geradas
							if(np.size(data.loc[data["movieId"] == suggestions.flatten()[i]]["title"].values) > 0 and np.size(data.loc[data["movieId"] == suggestions.flatten()[i]]["movieId"].values[0]) > 0):
								movie_title = data.loc[data["movieId"] == suggestions.flatten()[i]]["title"].values[0]
								movie_ID = data.loc[data["movieId"] == suggestions.flatten()[i]]["movieId"].values[0]
								movie_distance = distances.flatten()[i]
								movie_object_by_imdb = ia.search_movie(movie_title)
								if(printable):
									print('{0}: {1} (ID: {2}), com distância de {3} '.format(i, movie_title, movie_ID, movie_distance))


								if(len(movie_object_by_imdb) >= 1): #se encontrou um filme com tal titulo na pesquisa, usa o objeto
									lista_recomendacoes.append((movie_title, 
																movie_ID, 
																movie_distance,
																ia.get_imdbURL(movie_object_by_imdb[0])))
								else:
									lista_recomendacoes.append((movie_title, 
																movie_ID, 
																movie_distance,
																'Not Found'))

								#Lista_recomendaçoes é uma lista no formato [(Nome do filme, ID, distancia, Link para o IMDB), (Nome do filme, ID, distancia,  Link para o IMDB)]
					self.already_processed_recommendations[movie_title] = (distances, suggestions, lista_recomendacoes)

					return distances, suggestions, lista_recomendacoes
				else:
					raise Exception("Desculpe, foi impossivel gerar recomendações")
					

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


