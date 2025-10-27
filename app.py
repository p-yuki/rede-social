from flask import Flask, request, render_template, redirect, url_for
from models import db
import os

app = Flask(__name__)
app.secret_key = 'sua_chave_secreta_123'
app.config['UPLOAD_FOLDER'] = os.path.join('static', 'uploads')
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024
#cria pasta de uploads se não existir
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:1234@localhost/redesocialdb'
db.init_app(app)

@app.route('/')
def index():
    return render_template('painel.html')

if __name__ == '__main__':
    app.run(debug=True)
    
    from flask import Flask

app = Flask(__name__)

