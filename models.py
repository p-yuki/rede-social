from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

#cria tabela usuarios
class Usuario(db.Model):
    __tablename__ = 'usuarios'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), nullable=False)
    senha = db.Column(db.String(255), nullable=False)
    apartamento = db.Column(db.String(16), nullable=False)
    is_adm = db.Column(db.Boolean, default=False, nullable=False)
    is_sindico = db.Column(db.Boolean, default=False, nullable=False)
    posts = db.relationship('Postagem', backref='usuario', lazy=True, cascade='all, delete-orphan') #cascade = deleta os posts se o usuário for excluído

class Trabalho(db.Model):
    __tablename__ = 'trabalhos'
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    foto_id = db.Column(db.Integer, db.ForeignKey('fotos.id'), nullable=True)
    descricao = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(16), nullable=False)
    data_trabalho = db.Column(db.DateTime, default=db.func.current_timestamp())

class Foto(db.Model):
    __tablename__ = 'fotos'
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    filename = db.Column(db.String(255), nullable=False)
    foto_path = db.Column(db.String(500), nullable=False)
    data_upload = db.Column(db.DateTime, default=db.func.current_timestamp())

class Aviso(db.Model):
    __tablename__ = 'avisos'
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    foto_id = db.Column(db.Integer, db.ForeignKey('fotos.id'), nullable=True)
    descricao = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(16), nullable=False)
    data_aviso = db.Column(db.DateTime, default=db.func.current_timestamp())

class Aep(db.Model):
    __tablename__ = 'aeps'
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    foto_id = db.Column(db.Integer, db.ForeignKey('fotos.id'), nullable=True)
    descricao = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(16), nullable=False)
    data_aep = db.Column(db.DateTime, default=db.func.current_timestamp())