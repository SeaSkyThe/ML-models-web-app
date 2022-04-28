import pickle
import pandas as pd
import sklearn as sk
import numpy as np

N_NEIGHBORS = 11

class Model():
	def __init__(self, path_to_model, model_type=1):
		self.path_to_model = path_to_model
		self.model_type = model_type # model_types = {1: KNN_COLABORATIVE FILTERING; 2: KNN_CONTENT_BASED_GENRES; 3: KNN_CONTENT_BASED_TAGS}


	def load_model(self):
		with open(self.path_to_model, 'rb') as model_file:
			model = pickle.load(model_file)
		return model

	def generate_recommendations(self, movie_name, printable=True):
		if(self.model_type==1):
			lista_recomendacoes = []
			# Carregando o modelo
			model = self.load_model()
			# Carregando os dados
			with open("src/data/data_cf.pkl", 'rb') as d:
				data = pickle.load(d)

			with open("src/data/movie_user_matrix_cf.pkl", 'rb') as m:
				movie_user_matrix = pickle.load(m)

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


