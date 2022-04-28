import blosc # biblioteca de compressao para comprimir o modelo antes de realizar o upload
import pickle

class Compressor():
	def __init__(self):
		pass
	def compress_pickle(self, path_to_pickle):
		with open(path_to_pickle, "rb") as f:
			normal_pickle_object = f.read() #carregando o arquivo pickle normal
			compressed_pickle_object = blosc.compress(normal_pickle_object) #comprimindo o arquivo pickle

		return compressed_pickle_object

	def decompress_and_depickle_pickle(self, compressed_pickle_object):
		normal_pickle_object = blosc.decompress(compressed_pickle_object)

		depickled_object = pickle.loads(normal_pickle_object)

		return depickled_object
