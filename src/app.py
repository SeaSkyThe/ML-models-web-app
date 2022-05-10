from flask import Flask, request, render_template, abort
import pickle
try:
    from models import *
except:
    from src.models import *

from urllib.parse import quote_plus
import urllib

from imdb import Cinemagoer #biblioteca utilizada para gerar o link baseado no nome do filme

TEST = False

app = Flask(__name__)

#model = pickle.load(open('model.pkl', 'rb'))

@app.route("/")
def home_page():
    return render_template('home.html')

@app.route('/recommender_form')
def recommender_form_page():
    return render_template('recommender_form.html')

@app.route('/references')
def references_page():
    return render_template('references.html')

@app.route('/abstract')
def abstract_page():
    return render_template('abstract.html')

@app.route('/intro')
def introduction_page():
    return render_template('introduction.html')


@app.route('/recommender_results', methods=['POST'])
def recommender_results_page():
    """Pega o filme de entrada e gera as recomendações"""
    #print(request.form)
    movie_name = str(request.form["movie"])

    model = Model()

    #lembrando - lista_recomendações é no formato: [(Nome do filme, ID, distancia, Link para o IMDB), (Nome do filme, ID, distancia,  Link para o IMDB)]

    try:
        distances, suggestions, lista_recomendacoes = model.generate_recommendations(movie_name = movie_name, printable=False)
        # else:
        #     lista_recomendacoes = [("Spider-Man 2", 8636, 0.2825555145647274, "https://www.imdb.com/title/tt0316654/"), ("X-Men", 3793, 0.3413763517073479, "https://www.imdb.com/title/tt0120903/"), ("Pirates of the Caribbean: The Curse of the Black Pearl", 6539, 0.3588441941956504, "https://www.imdb.com/title/tt0325980/"), ("Shrek", 4306, 0.368959263617995, "https://www.imdb.com/title/tt0126029/"), ("Lord of the Rings: The Fellowship of the Ring, The", 4993, 0.36952007138761145, "https://www.imdb.com/title/tt0120737/"), ("X2: X-Men United", 6333, 0.372830643301859, "https://www.imdb.com/title/tt0290334/"), ("Lord of the Rings: The Two Towers, The", 5952, 0.37605243697252433, "https://www.imdb.com/title/tt0167261/"), ("Minority Report", 5445, 0.38308412943069914, "https://www.imdb.com/title/tt0181689/"), ("Ocean's Eleven", 4963, 0.39309795039554385, "https://www.imdb.com/title/tt0240772/"), ("Lord of the Rings: The Return of the King, The", 7153, 0.40089356159107903, "https://www.imdb.com/title/tt0167260/")]
        #     distances = np.array([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
        #     suggestions = np.array([5349,8636,3793,6539,4306,4993,6333,5952,5445,4963,7153])
        #print(distances, suggestions, lista_recomendacoes)

        #pegando a url das capas dos filme
        cover_urls = {}
        ia = Cinemagoer()
        for recommendation in lista_recomendacoes:

            movie = ia.search_movie(recommendation[0])

            if(len(movie) >= 1):
                movie = movie[0]
                cover_urls[recommendation] = movie['full-size cover url']
            else:
                cover_urls[recommendation] = ''
        

        #print(lista_recomendacoes)
        #prediction = model.predict([[rooms, distance]])
        #output = round(prediction[0], 2) 
        return render_template('recommender_results.html', movie_name=movie_name, lista_recomendacoes=lista_recomendacoes, cover_urls=cover_urls)
    
    except Exception as error:
        print(f'Erro ao gerar recomendações: {error}\n')
        return internal_error(500)
        

@app.errorhandler(500)
def internal_error(error):
    return render_template('recommender_error.html'), 500

@app.route('/recommender_error')
def error500():
    abort(500)

if(__name__ == "__main__"):
    app.run(debug=True)