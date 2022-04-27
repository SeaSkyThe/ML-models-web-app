from flask import Flask, request, render_template
import pickle

app = Flask(__name__)

#model = pickle.load(open('model.pkl', 'rb'))

@app.route("/")
def home():
    return render_template('index.html')

@app.route('/predict',methods=['POST'])
def predict():
    """Pega o filme de entrada e gera as recomendações"""
    movie = str(request.form["movie"])
    #prediction = model.predict([[rooms, distance]])
    #output = round(prediction[0], 2) 

    return render_template('index.html', prediction_text=f'As recomendações para o filme {movie} são: {movie}')


if(__name__ == "__main__"):
    app.run(debug=True)