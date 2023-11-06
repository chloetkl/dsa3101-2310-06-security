from flask import Flask, request, send_file, render_template


app = Flask(__name__)

@app.route("/")
def nusecure():
    return "<p>Welcome to NUSecure!</p>"

@app.route("/prediction")
def send_p():
    return send_file("back/data/test.png")

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
