from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, Usuario, Foto # Importar Foto
from utils import allowed_file # Importar função de validação de arquivo
from werkzeug.utils import secure_filename
from datetime import datetime
from flask import current_app as app
import os # Importar módulo OS

usuarios_bp = Blueprint('usuarios_bp', __name__)

@usuarios_bp.route('/usuarios/novo', methods=['GET', 'POST'])
def novo():
    if request.method == 'POST':
        nome = request.form.get('nome', '').strip()
        email = request.form.get('email', '').strip().lower()
        senha = request.form.get('senha', '')
        bloco = request.form.get('bloco','')
        apartamento = request.form.get('apartamento','')
        is_adm = bool(int(request.form.get('is_adm', 0)))
        is_sindico = bool(int(request.form.get('is_sindico', 0)))
        
        # NOVIDADE: Recebe o arquivo
        arquivo_foto = request.files.get('foto') 

        if not nome or not email or not senha:
            flash('Preencha todos os campos obrigatórios (nome, email, senha)!', 'danger')
            return render_template('usuarios_form.html')

        if Usuario.query.filter_by(email=email).first():
            flash('Este email já está cadastrado.', 'danger')
            return render_template('usuarios_form.html')

        foto_id = None
        
        # 💡 Processamento do Upload da Foto (Similar ao AEP/Trabalhos)
        if arquivo_foto and arquivo_foto.filename != '' and allowed_file(arquivo_foto.filename):
            filename = arquivo_foto.filename
            nome_seguro = secure_filename(filename)
            unique_filename = f"user_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{nome_seguro}"
            
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
            arquivo_foto.save(filepath)
            
            # Cria registro da foto
            foto = Foto()
            foto.foto_path = unique_filename
            foto.usuario_id = session['user_id'] # Note: se o ADM está cadastrando, o ID da foto é do ADM
            foto.filename = nome_seguro
            
            db.session.add(foto)
            db.session.flush() 
            foto_id = foto.id 
            
        usuario = Usuario()
        usuario.nome = nome
        usuario.email = email
        usuario.senha = generate_password_hash(senha)
        usuario.bloco = bloco
        usuario.apartamento = apartamento
        usuario.is_adm = is_adm
        usuario.is_sindico = is_sindico
        usuario.foto_id = foto_id # NOVIDADE: Relaciona a foto ao usuário
        
        db.session.add(usuario)
        db.session.commit()
        
        flash('Morador cadastrado com sucesso!', 'success')
        # Redirecionado para a listagem de usuários após cadastro
        return redirect(url_for('usuarios'))
    
    return render_template('usuarios_form.html', title='Cadastro')


@usuarios_bp.route('/usuarios/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        senha = request.form.get('senha', '')
        user = Usuario.query.filter_by(email=email).first()

        if user and not user.is_active:
            flash('Este usuário está desativado. Fale com o administrador.', 'danger')
            return render_template('login.html')

        if user and check_password_hash(user.senha, senha):
            # NOVIDADE: Buscar foto e salvar na session
            foto_path = None
            if user.foto_id:
                foto = Foto.query.get(user.foto_id)
                if foto:
                    foto_path = foto.foto_path  # ou check_password_hash
            session['user_id'] = user.id
            session['user_name'] = user.nome
            session['user_bloco'] = user.bloco
            session['user_apartamento'] = user.apartamento
            session['is_adm'] = user.is_adm
            session['is_sindico'] = user.is_sindico # Garante que o síndico está salvo
            session['user_foto_path'] = foto_path # NOVIDADE: Caminho da foto
            
            flash('Login realizado com sucesso!', 'success')
            return redirect(url_for('home'))
            

    flash('Email ou senha incorretos!', 'danger')
    return render_template('login.html')


@usuarios_bp.route('/usuarios/desativar/<int:user_id>', methods=['POST'])
def desativar_usuario(user_id):
    usuario = Usuario.query.get_or_404(user_id)
    usuario.is_active = False
    db.session.commit()

    flash(f'O usuário {usuario.nome} foi desativado.', 'warning')
    return redirect(url_for('usuarios'))


@usuarios_bp.route('/usuarios/logout')
def logout():
    session.clear()
    flash('Você saiu da conta.', 'info')
    return redirect(url_for('login'))

@usuarios_bp.route('/usuarios')
def usuarios():
    usuarios = Usuario.query.order_by(Usuario.nome).all()
    return render_template('usuarios.html', usuarios=usuarios)

