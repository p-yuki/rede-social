# a criação de avisos NÃO pode ser acessada por usuários comuns

from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from werkzeug.utils import secure_filename
from models import db, Aviso, Usuario, Foto
from utils import login_required, allowed_file
import os
from datetime import datetime
from flask import current_app as app


avisos_bp = Blueprint('avisos_bp', __name__)

@avisos_bp.route('/avisos/novo', methods=['GET', 'POST'])
@login_required
def novo_aviso():
    if request.method == 'POST':
        nome_aviso = request.form.get('nome_aviso', '').strip()
        descricao = request.form.get('descricao', '').strip()
        data_aviso = request.form.get('data_aviso')
        horario_aviso = request.form.get('horario_aviso')
        status = request.form.get('status', 'pendente')
        arquivo_foto = request.files.get('foto')
        
        if not descricao:
            flash('A descrição é obrigatória!', 'danger')
            return render_template('avisos_form.html')
        
        foto_id = None
        
        #processar upload da foto se foi enviada
        if arquivo_foto and arquivo_foto.filename != '':
            filename = arquivo_foto.filename
            if filename and allowed_file(filename):
                #gera nome único para o arquivo
                nome_seguro = secure_filename(filename)
                unique_filename = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{filename}"
                
                #salva arquivo na pasta de uploads
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
                os.makedirs(os.path.dirname(filepath), exist_ok=True)
                arquivo_foto.save(filepath)
                
                #cria registro da foto no banco
                foto = Foto()
                foto.foto_path = unique_filename
                foto.usuario_id = session['user_id']
                
                db.session.add(foto)
                db.session.flush()  #gera o id sem commit final
                foto_id = foto.id  #pega o id da foto criada
        
        #cria o aviso
        aviso = Aviso()
        aviso.usuario_id = session['user_id']
        aviso.foto_id = foto_id
        aviso.status = status
        aviso.nome_aviso = nome_aviso
        aviso.descricao = descricao
        aviso.data_aviso = data_aviso
        aviso.horario_aviso = horario_aviso
        db.session.add(aviso)
        db.session.commit()
        
        flash('aviso criado com sucesso!', 'success')
        return redirect(url_for('avisos_bp.avisos'))
    
    return render_template('avisos_form.html')

@avisos_bp.route('/avisos/excluir/<int:aviso_id>', methods=['POST'])
@login_required
def excluir_aviso(aviso_id):
    aviso = Aviso.query.get_or_404(aviso_id)
        
    #verifica se o usuário logado é o autor do aviso
    if aviso.usuario_id != session['user_id']:
        flash('Você não tem permissão para excluir este aviso.', 'danger')
        return redirect(url_for('avisos_bp.avisos'))
        
    #verifica se o aviso tem uma foto associada para excluir
    if aviso.foto_id:
        foto = Foto.query.get(aviso.foto_id)
        if foto:
            #exclui o arquivo físico da foto
            try:
                caminho_foto = os.path.join(app.config['UPLOAD_FOLDER'], foto.caminho)
                if os.path.exists(caminho_foto):
                    os.remove(caminho_foto)
            except Exception as e:
                print(f"Erro ao excluir arquivo: {e}")
                
            #exclui o registro da foto do banco
            db.session.delete(foto)
        
        #exclui o aviso
        db.session.delete(aviso)
        db.session.commit()
        
    flash('Post excluído com sucesso!', 'success')
    
    return redirect(url_for('avisos_bp.avisos'))

@avisos_bp.route('/avisos')
def avisos():
    avisos = (
    Aviso.query
    .join(Usuario)
    .add_columns(
        Aviso.id, 
        Aviso.descricao, 
        Aviso.foto_id, 
        Aviso.data_aviso,
        Usuario.nome.label('usuario_nome')
    )
    .order_by(Aviso.data_aviso.desc())
    .all()
)

    
    return render_template('avisos.html', avisos=avisos)