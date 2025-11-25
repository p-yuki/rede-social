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
    bloco = db.Column(db.String(16), nullable=False)
    is_adm = db.Column(db.Boolean, default=False, nullable=False)
    is_sindico = db.Column(db.Boolean, default=False, nullable=False)

    trabalhos = db.relationship('Trabalho', backref='usuario', lazy=True)
    achados = db.relationship('Achado', backref='usuario', lazy=True)
    reservas = db.relationship('Reserva', backref='usuario', lazy=True)


class Trabalho(db.Model):
    __tablename__ = 'trabalhos'
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    foto_id = db.Column(db.Integer, db.ForeignKey('fotos.id'))
    
    descricao = db.Column(db.Text, nullable=False)
    categoria = db.Column(db.String(255), nullable=False)
    data_trabalho = db.Column(db.DateTime, default=db.func.current_timestamp())
    nome_trabalho = db.Column(db.String(255), nullable=False)
    bloco = db.Column(db.String(16))
    apartamento = db.Column(db.String(16))
    contato = db.Column(db.String(255), nullable=False)


class Foto(db.Model):
    __tablename__ = 'fotos'
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    filename = db.Column(db.String(255))
    foto_path = db.Column(db.String(500), nullable=False)
    data_upload = db.Column(db.DateTime, default=db.func.current_timestamp())

    trabalhos = db.relationship('Trabalho', backref='foto', lazy=True)
    achados = db.relationship('Achado', backref='foto', lazy=True)


class Aviso(db.Model):
    __tablename__ = 'avisos'
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    foto_id = db.Column(db.Integer, db.ForeignKey('fotos.id'), nullable=True)
    descricao = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(16), nullable=False)
    horario_aviso = db.Column(db.Time(16))
    data_aviso = db.Column(db.Date())
    data_criacao = db.Column(db.DateTime, default=db.func.current_timestamp())
    nome_aviso = db.Column(db.String(255), nullable=False)

class Achado(db.Model):
    __tablename__ = 'achados'
    id = db.Column(db.Integer, primary_key=True)

    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    foto_id = db.Column(db.Integer, db.ForeignKey('fotos.id'))

    descricao = db.Column(db.String(255), nullable=False)
    local = db.Column(db.String(255), nullable=False)
    status = db.Column(db.String(16), nullable=False)
    contato = db.Column(db.String(20), nullable=False)

    data_achado = db.Column(db.DateTime, default=db.func.current_timestamp())
    data_encontro = db.Column(db.Date())


class Reserva(db.Model):
    __tablename__ = 'reservas'
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    data_reserva = db.Column(db.DateTime, nullable=False)
    data_criacao = db.Column(db.DateTime, default=db.func.current_timestamp())
    local = db.Column(db.String(255), nullable=False)