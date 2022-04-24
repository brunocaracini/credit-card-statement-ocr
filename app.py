from flask import Flask, render_template

#app creation
app = Flask(__name__)
app.secret_key = 'SecretKeyForSigningCookies'

#Test UI
@app.route('/index', methods=['GET'])
def main():
    return render_template('index.html')

@app.route('/forms', methods=['GET'])
def forms():
    return render_template('forms.html')

@app.route('/cards', methods=['GET'])
def cards():
    return render_template('cards.html')

@app.route('/charts', methods=['GET'])
def charts():
    return render_template('charts.html')

@app.route('/buttons', methods=['GET'])
def buttons():
    return render_template('buttons.html')

@app.route('/modals', methods=['GET'])
def modals():
    return render_template('modals.html')

@app.route('/tables', methods=['GET'])
def tables():
    return render_template('tables.html')

@app.route('/pages/login', methods=['GET'])
def login():
    return render_template('pages/login.html')

@app.route('/pages/404', methods=['GET'])
def error_404():
    return render_template('pages/404.html')

@app.route('/pages/create-account', methods=['GET'])
def create_account():
    return render_template('pages/create-account.html')

@app.route('/pages/forgot-password', methods=['GET'])
def forgot_password():
    return render_template('pages/forgot-password.html')

@app.route('/pages/blank', methods=['GET'])
def blank():
    return render_template('pages/blank.html')

if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=5000)