from flask_pymongo import pymongo
from pymongo.server_api import ServerApi
from urllib.parse import quote_plus
import gridfs

import os
import time
try:
	from compressor import *
except:
	from src.compressor import *
# Criando objeto para comprimir os arquivos pickle de dados e dos modelos
compressor = Compressor()


#GRIDFS é uma biblioteca que auxilia no manuseio de arquivos maiores que 16mb dentro de bancos de dados MongoDB

class Database():
	_instance = None

	def __init__(self):
		self.client = self.create_conection()


	@classmethod
	def instance(cls):
		if(cls._instance is None):
			cls._instance = cls()
		return cls._instance

	
	def create_conection(self):
		#utilizando Enviroment Variables
		username = quote_plus(os.environ.get('MONGODB_USER'))
		password = quote_plus(os.environ.get('MONGODB_PASSWORD'))
		cluster = 'ML-WebApp-Flask'
		uri = "mongodb+srv://" + username + ":" + password + "@ml-webapp-flask.lrl8g.mongodb.net/" + cluster + "?retryWrites=true&w=majority"
		#Criando conexao
		try:
			self.client = pymongo.MongoClient(uri, server_api=ServerApi('1'), serverSelectionTimeoutMS=5000) #conectando ao database
			return self.client
		except Exception as e:
			print(f'Erro inesperado ao se conectar com o MongoDB Atlas {e=}, {type(e)=}')
			return e


	#Funcao que só executa seu papel 1 vez - Envia os dados comprimidos para o MongoDB Altas
	def upload_data_and_models_to_db(self, client: pymongo.MongoClient):
		if(not "Data" in client.list_database_names()): #se nao existir o database DATA a gente cria um e insere (para que façamos apenas 1 vez)
			#Inserindo dados necessários no banco de dados
			fs = gridfs.GridFS(client.Data) #criando um objeto GRIDFS que permite dar upload em arquivos grandes - para o Database de Dados

			# Subindo as informações sobre os filmes
			compressed_movies_cf = compressor.compress_pickle(path_to_pickle='src/data/movies_cf.pkl')
			movies_cf = fs.put(compressed_movies_cf, filename='movies_cf', content_type="DataFrame")

			compressed_movie_user_matrix = compressor.compress_pickle(path_to_pickle='src/data/movie_user_matrix_cf.pkl')
			movie_user_matrix_cf = fs.put(compressed_movie_user_matrix, filename='movie_user_matrix_cf', content_type="Matrix")

		if(not "Models" in client.list_database_names()):
		#criando objeto gridfs para dar upload para o database de modelos
			fs = gridfs.GridFS(client.Models)

			# Chamando a funcao de compressao do arquivo pickle
			compressed_model = compressor.compress_pickle(path_to_pickle='src/models/knn_cf.sav')
			# Mandando para o MongoDB Atlas
			knn_cf = fs.put(compressed_model, filename='knn_cf', content_type="ML-Model")
	
	def get_data_and_models_from_db(self):
		objects = {} #dicionario de objetos para dar como retorno da funcao

		
		if(self.client != None and isinstance(self.client, pymongo.MongoClient)):
			client = self.client
		
		#Connectando com o banco Data utilizando o GRIDFS
		try:
			fs = gridfs.GridFS(client.Data)
			#pegando a versao comprimida direto do banco
			compressed_movies_cf = fs.get_version('movies_cf').read()
			#descomprimindo em pickle, e transformando o pickle em objeto novamente
			movies_cf = compressor.decompress_and_depickle_pickle(compressed_movies_cf)
			objects['movies_cf'] = movies_cf

			#pegando a versao comprimida direto do banco
			compressed_movie_user_matrix = fs.get_version('movie_user_matrix_cf').read()
			#descomprimindo em pickle, e transformando o pickle em objeto novamente
			movie_user_matrix_cf = compressor.decompress_and_depickle_pickle(compressed_movie_user_matrix)
			objects['movie_user_matrix'] = movie_user_matrix_cf

			#Conectando com o banco 'Models' utilizando o GRIDFS
			fs = gridfs.GridFS(client.Models)
			compressed_knn_cf = fs.get_version('knn_cf').read()
			knn_cf = compressor.decompress_and_depickle_pickle(compressed_knn_cf)
			objects['knn_cf'] = knn_cf

		
			return objects

		except Exception as e:
			print(f'Erro inesperado ao tentar resgatar os dados/modelo do MongoDB Atlas {e=}, {type(e)=}')
			return [[], [], []]

if __name__=='__main__':
	database = Database()
	client = database.create_conection()
	database.upload_data_and_models_to_db(client)

	

# try:
# 	print("\n\nSERVER INFO: \n")
# 	print(client.server_info())
# 	print("\n\n")
# except Exception:
# 	print("Incapaz de se conectar ao servidor")