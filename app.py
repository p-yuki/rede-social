from flask import Flask, render_template, session
from models import db
from utils import login_required
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

@app.context_processor
def inject_usuario():
    class Usuario:
        def __init__(self, nome, bloco, apartamento, is_adm):
            self.nome = nome
            self.bloco = bloco
            self.apartamento = apartamento
            self.is_adm = is_adm

    usuario = Usuario(
        session.get('user_name'),
        session.get('user_bloco'),
        session.get('user_apartamento'),
        session.get('is_adm')
    )

    return dict(usuario=usuario)


@app.route('/')
def login():
    return render_template('login.html')

@app.route('/painel')
@login_required
def painel():
    return render_template('painel.html')

@app.route('/achados_perdidos')
@login_required
def achados_perdidos():
    return render_template('achados_perdidos.html')

@app.route('/trabalhos')
@login_required
def trabalhos():
    return render_template('trabalhos.html')

@app.route('/perfil')
@login_required
def perfil():
    return render_template('perfil.html')


@app.route('/usuarios')
@login_required
def novo_user():
    return render_template('usuarios.html')

@app.route('/chat')
@login_required
def chat():
    return render_template('chat.html')

if __name__ == '__main__':
    app.run(debug=True)