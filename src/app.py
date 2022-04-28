from flask import Flask, request, render_template
import pickle
from models import *

app = Flask(__name__)

#model = pickle.load(open('model.pkl', 'rb'))

@app.route("/")
def home_page():
    return render_template('home.html')

@app.route('/recommender_form')
def recommender_form_page():
    return render_template('recommender_form.html')

@app.route('/recommender_results', methods=['POST'])
def recommender_results_page():
    """Pega o filme de entrada e gera as recomendações"""
    #print(request.form)
    movie_name = str(request.form["movie"])

    model = Model('src/models/knn_cf.sav')
    distances, suggestions, lista_recomendacoes = model.generate_recommendations(movie_name = movie_name, printable=False)

    #prediction = model.predict([[rooms, distance]])
    #output = round(prediction[0], 2) 
    return render_template('recommender_results.html', prediction_text=f'As recomendações para o filme {movie_name} são: {lista_recomendacoes}')
    


if(__name__ == "__main__"):
    app.run(debug=True)