from flask import Flask, render_template
from models import db
import os

app = Flask(__name__)
app.secret_key = 'sua_chave_secreta_123'
app.config['UPLOAD_FOLDER'] = os.path.join('static', 'uploads')
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024
#cria pasta de uploads se não existir
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

from trabalhos import trabalhos_bp
app.register_blueprint(trabalhos_bp)

from avisos import avisos_bp
app.register_blueprint(avisos_bp)

from usuarios import usuarios_bp
app.register_blueprint(usuarios_bp)

from aeps import aeps_bp
app.register_blueprint(aeps_bp)


app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:Senai%40118@localhost/redesocialdb'
db.init_app(app)

@app.route('/')
def painel():
    return render_template('painel.html')

@app.route('/achados_perdidos')
def achados_perdidos():
    return render_template('achados_perdidos.html')

@app.route('/trabalhos')
def trabalhos():
    return render_template('trabalhos.html')

@app.route('/perfil')
def perfil():
    return render_template('perfil.html')

@app.route('/chat')
def chat():
    return render_template('chat.html')

if __name__ == '__main__':
    app.run(debug=True)
    
    from flask import Flask

app = Flask(__name__)

