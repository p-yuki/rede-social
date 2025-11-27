from flask import Flask, render_template, session, request
from models import db, Usuario, Aviso, Achado, Trabalho, Reserva
from utils import login_required
import os
from werkzeug.security import generate_password_hash
from flask_socketio import SocketIO, emit, join_room, leave_room

app = Flask(__name__)

# CONFIGURAÇÃO INICIAL
app.secret_key = 'sua_chave_secreta_123' 
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

app.config['SECRET_KEY'] = '123'
socketio = SocketIO(app)
app.config['UPLOAD_FOLDER'] = os.path.join(BASE_DIR, 'static', 'uploads')
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# CONFIGURAÇÃO DO BANCO
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:2007@localhost/redesocialdb'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # <- corrigido
db.init_app(app)

# BLUEPRINTS
from trabalhos import trabalhos_bp
from avisos import avisos_bp
from usuarios import usuarios_bp
from achados import achados_bp
from reservas import reservas_bp

app.register_blueprint(trabalhos_bp)
app.register_blueprint(avisos_bp)
app.register_blueprint(usuarios_bp)
app.register_blueprint(achados_bp)
app.register_blueprint(reservas_bp)

# INICIALIZAÇÃO DO BANCO + ADMIN
with app.app_context():
    db.create_all()
    
    if not Usuario.query.filter_by(email='adm@gmail.com').first():
        admin = Usuario()
        admin.nome = 'Administrador'
        admin.email = 'adm@gmail.com'
        admin.senha = generate_password_hash('12345')
        admin.bloco = '0'
        admin.apartamento = '0'
        admin.is_adm = True
        admin.is_sindico = False

        db.session.add(admin)
        db.session.commit()

# INJEÇÃO DE USUÁRIO
@app.context_processor
def inject_usuario():
    class UsuarioFake:
        def __init__(self, nome, email, bloco, apartamento, is_adm, is_sindico, foto_path):
            self.nome = nome
            self.email = email
            self.bloco = bloco
            self.apartamento = apartamento
            self.is_adm = is_adm
            self.is_sindico = is_sindico
            self.foto_path = foto_path

    usuario = UsuarioFake(
        session.get('user_name'),
        session.get('user_email'),
        session.get('user_bloco'),
        session.get('user_apartamento'),
        session.get('is_adm'),
        session.get('is_sindico'),
        session.get('user_foto_path')
    )

    return dict(usuario=usuario)

# ROTAS PRINCIPAIS
@app.route('/')
def login():
    return render_template('login.html')  # <- deixei esta como raiz

@app.route('/home')
@login_required
def home():
    aviso_urgente = Aviso.query.filter_by(status='urgente').order_by(Aviso.data_aviso.desc()).first()
    ultimos_avisos = Aviso.query.order_by(Aviso.data_aviso.desc()).limit(3).all()
    ultimos_achados = Achado.query.order_by(Achado.data_achado.desc()).limit(3).all()
    ultimos_trabalhos = Trabalho.query.order_by(Trabalho.data_trabalho.desc()).limit(3).all()

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
        reservas_por_local.setdefault(r.local, []).append(r.data_reserva.strftime("%Y-%m-%d"))
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

@app.route('/chat')
@login_required
def chat():
    return render_template('chat.html')

# =======================
# CHAT TEMPO REAL (ORIGINAL SEM ALTERAR LÓGICA)
# =======================

users_online = {}
rooms_users = {}

@socketio.on("join")
def join_room_event(data):
    username = data.get("username")
    room = data.get("room")
    sid = str(request.sid)

    users_online[sid] = {"username": username, "room": room}

    if room not in rooms_users:
        rooms_users[room] = []

    if username not in rooms_users[room]:
        rooms_users[room].append(username)

    join_room(room)
    emit("system_message", {"msg": f"{username} entrou no chat."}, to=room)
    emit("users", rooms_users[room], to=room)

@socketio.on("message")
def handle_message(data):
    username = data.get("username")
    msg = data.get("msg")
    room = data.get("room")

    emit("message", {"username": username, "msg": msg}, to=room)

@socketio.on("disconnect")
def disconnect_user():
    sid = str(request.sid)

    if sid not in users_online:
        return

    username = users_online[sid]["username"]
    room = users_online[sid]["room"]

    if room in rooms_users and username in rooms_users[room]:
        rooms_users[room].remove(username)

    del users_online[sid]

    emit("system_message", {"msg": f"{username} saiu do chat."}, to=room)
    emit("users", rooms_users.get(room, []), to=room)

# EXECUÇÃO
if __name__ == '__main__':
    socketio.run(app, debug=True)