from flask import Flask, request, send_file, render_template
from back.models.sarima.fit_sarima_model import fit_sarima_model


app = Flask(__name__)

@app.route("/")
def nusecure():
    return "<p>Welcome to NUSecure!</p>"

@app.route("/fit_sarima")
def fit_sarima():
    fit_sarima_model()
    return "sarima pkl added in container"

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
