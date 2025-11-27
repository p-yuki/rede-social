from flask import Flask, render_template, session
from models import db, Usuario, Aviso, Achado, Trabalho, Reserva
from utils import login_required
import os
from werkzeug.security import generate_password_hash
from flask_mail import Mail, Message

# --- INICIALIZAÇÃO E CHAVE SECRETA ---
app = Flask(__name__)

# 🔑 CHAVE SECRETA (CRUCIAL): Deve ser a PRIMEIRA configuração após 'app = Flask()'.
app.secret_key = 'sua_chave_secreta_123' 

# 📁 CONFIGURAÇÕES DE UPLOAD (CORREÇÃO DO CAMINHO ABSOLUTO)
# 1. Define o caminho base do projeto de forma absoluta.
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

# 2. Define a pasta de uploads DENTRO de 'static' usando o caminho absoluto.
app.config['UPLOAD_FOLDER'] = os.path.join(BASE_DIR, 'static', 'uploads')
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# 💾 Configuração do banco de dados
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:1234@localhost/redesocialdb'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)


app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'boavizinhanca118@gmail.com'
app.config['MAIL_PASSWORD'] = 'Boa@Vizinhanca118!'   # não use senha normal!
app.config['MAIL_DEFAULT_SENDER'] = ('Boa Vizinhança', 'boavizinhanca118@gmail.com')

mail = Mail(app)


# 🔧 Importa e registra blueprints
from trabalhos import trabalhos_bp
app.register_blueprint(trabalhos_bp)

from avisos import avisos_bp
app.register_blueprint(avisos_bp)

from usuarios import usuarios_bp
app.register_blueprint(usuarios_bp)

from achados import achados_bp
app.register_blueprint(achados_bp)

from reservas import reservas_bp
app.register_blueprint(reservas_bp)

# 🧠 Cria tabelas e o admin padrão
with app.app_context():
    db.create_all()  # garante que as tabelas existem
    # Verifica se o admin já existe
    if not Usuario.query.filter_by(email='adm@gmail.com').first():
        admin = Usuario()
        admin.nome = 'Administrador'
        admin.email = 'adm@email.com'
        admin.senha = generate_password_hash('12345')
        admin.bloco = '0'
        admin.apartamento = '0'
        admin.is_adm = True
        admin.is_sindico = False
        # Novo admin pode precisar do foto_id = None se for novo registro
        # admin.foto_id = None 

        db.session.add(admin)
        db.session.commit()

    else:
        print("⚙️ Conta de administrador já existe.")


# 📡 Injeção de dados do usuário logado no template
@app.context_processor
def inject_usuario():
    class UsuarioFake:
        # NOVIDADE: Adicionado 'foto_path' ao construtor
        def __init__(self, nome, email, bloco, apartamento, is_adm, is_sindico, foto_path):
            self.nome = nome
            self.email = email
            self.bloco = bloco
            self.apartamento = apartamento
            self.is_adm = is_adm
            self.is_sindico = is_sindico
            self.foto_path = foto_path  # NOVIDADE: Campo para o caminho da foto

    usuario = UsuarioFake(
        session.get('user_name'),
        session.get('user_email'),  # <-- ADICIONE AQUI
        session.get('user_bloco'),
        session.get('user_apartamento'),
        session.get('is_adm'),
        session.get('is_sindico'),
        session.get('user_foto_path')
    )

    return dict(usuario=usuario)


# 🧩 Rotas principais

@app.route('/')
def login():
    return render_template('login.html')

@app.route('/home')
@login_required
def home():
    # Último aviso URGENTE (se existir)
    aviso_urgente = (
        Aviso.query
        .filter_by(status='urgente')
        .order_by(Aviso.data_aviso.desc())
        .first()
    )

    # Últimos 3 avisos, independente do status
    ultimos_avisos = (
        Aviso.query
        .order_by(Aviso.data_aviso.desc())
        .limit(3)
        .all()
    )

    # 🔹 Últimos 3 Achados e Perdidos
    ultimos_achados = (
        Achado.query
        .order_by(Achado.data_achado.desc())
        .limit(3)
        .all()
    )

    # 🔹 Últimos 3 Trabalhos
    ultimos_trabalhos = (
        Trabalho.query
        .order_by(Trabalho.data_trabalho.desc())
        .limit(3)
        .all()
    )
    
    categoria_trabalho = {
    "beleza": "Beleza",
    "prestacao_servico": "Prestação de Serviço",
    "alimentacao": "Alimentação"
    }

    return render_template(
        'home.html',
        aviso=aviso_urgente,
        avisos=ultimos_avisos,
        achados=ultimos_achados,
        trabalhos=ultimos_trabalhos,
        categoria_trabalho=categoria_trabalho
    )


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
def usuarios():
    usuarios_lista = Usuario.query.all()
    return render_template('usuarios.html', usuarios=usuarios_lista)

@app.route('/reservas')
@login_required
def reservas():
    reservas = Reserva.query.all()

    reservas_por_local = {}
    for r in reservas:
        if r.local not in reservas_por_local:
            reservas_por_local[r.local] = []
        reservas_por_local[r.local].append(r.data_reserva.strftime("%Y-%m-%d"))

    return render_template("reservas.html", reservas_por_local=reservas_por_local)


@app.route('/acesso')
def acesso():
    return render_template('acesso.html')
    
@app.route('/painel')
@login_required
def painel():
    return render_template('painel_controle.html')

@app.route('/avisos')
@login_required
def avisos():
    return render_template('avisos.html')

@app.route('/achados')
@login_required
def achados():
    return render_template('achados_perdidos.html')

if __name__ == '__main__':
    app.run(debug=True)