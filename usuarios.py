from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, Usuario

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

        if not nome or not email or not senha:
            flash('Preencha todos os campos!', 'danger')
            return redirect(url_for('usuarios_form'))

        if Usuario.query.filter_by(email=email).first():
            flash('Este email já está cadastrado.', 'danger')
            return redirect(url_for('usuarios_form'))

        usuario = Usuario()
        usuario.nome = nome
        usuario.email = email
        usuario.senha = generate_password_hash(senha)
        usuario.bloco = bloco
        usuario.apartamento = apartamento
        usuario.is_adm = is_adm
        usuario.is_sindico = is_sindico
        db.session.add(usuario)
        db.session.commit()
        return redirect(url_for('home'))
    
    return render_template('usuarios_form.html', title='Cadastro')


@usuarios_bp.route('/usuarios/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        senha = request.form.get('senha', '')
        user = Usuario.query.filter_by(email=email).first()

        if user and check_password_hash(user.senha, senha):  # ou check_password_hash
            session['user_id'] = user.id
            session['user_name'] = user.nome
            session['user_bloco'] = user.bloco
            session['user_apartamento'] = user.apartamento
            session['is_adm'] = user.is_adm
            flash('Login realizado com sucesso!', 'success')
            return redirect(url_for('home'))
    flash('Email ou senha incorretos!', 'danger')
    return render_template('login.html', title='Login')


@usuarios_bp.route('/usuarios/logout')
def logout():
    session.clear()
    flash('Você saiu da conta.', 'info')
    return redirect(url_for('login'))