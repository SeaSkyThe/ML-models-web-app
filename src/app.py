from flask import Flask, request, render_template
import pickle

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
    movie = str(request.form["movie"])
    #prediction = model.predict([[rooms, distance]])
    #output = round(prediction[0], 2) 
    return render_template('recommender_results.html', prediction_text=f'As recomendações para o filme {movie} são: {movie}')
    


if(__name__ == "__main__"):
    app.run(debug=True)