from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        user_id = request.form['UserID']
        password = request.form['Password']  

        if user_id == 'security' and password == 'security':
            return redirect(url_for('security'))
        elif user_id == 'analytics' and password == 'analytics':
            return redirect(url_for('analytics'))
        else:
            return "Invalid UserID or Password"
    return render_template('home.html')

@app.route('/security', methods=['GET'])
def security():
    return render_template('security.html')

@app.route('/analytics', methods=['GET'])
def analytics():
    return render_template('analytics.html')

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
