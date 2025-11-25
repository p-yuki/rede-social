from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from werkzeug.utils import secure_filename
from models import db, Achado, Usuario, Foto
from utils import login_required, allowed_file
import os
from datetime import datetime
from flask import current_app as app

achados_bp = Blueprint('achados_bp', __name__)

@achados_bp.route('/achados/novo_achado', methods=['GET', 'POST'])
def novo_achados():
    if request.method == 'POST':
        descricao = request.form.get('descricao', '').strip()
        arquivo_foto = request.files.get('foto')
        contato = request.form.get('contato')
        local = request.form.get('local')
        status = request.form.get('status')
        data_encontro = request.form.get('data_encontro')
        
        if not descricao:
            flash('A descrição é obrigatória!', 'danger')
            return render_template('achados_perdidos_form.html')
        
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
        
        #cria a postagem
        achado = Achado()
        achado.usuario_id = session['user_id']
        achado.foto_id = foto_id
        achado.descricao = descricao
        achado.status = status
        achado.contato = contato
        achado.local = local
        achado.data_encontro = data_encontro
        db.session.add(achado)
        db.session.commit()
        
        flash('Achado criada com sucesso!', 'success')
        return redirect(url_for('achados_bp.achados'))
    
    return render_template('achados_perdidos_form.html')

@achados_bp.route('/achados/excluir/<int:achado_id>', methods=['POST'])
def excluir_achado(achado_id):
    achado = Achado.query.get_or_404(achado_id)

    # verifica se o usuário logado é o autor do post
    if achado.usuario_id != session['user_id']:
        flash('Você não tem permissão para excluir este post.', 'danger')
        return redirect(url_for('achados_bp.achados'))

    # se tiver foto, excluir foto física e do banco
    if achado.foto_id:
        foto = Foto.query.get(achado.foto_id)
        if foto:
            try:
                caminho_foto = os.path.join(app.config['UPLOAD_FOLDER'], foto.foto_path)
                if os.path.exists(caminho_foto):
                    os.remove(caminho_foto)
            except Exception as e:
                print(f"Erro ao excluir o arquivo da foto: {e}")

            db.session.delete(foto)

    # excluir o Achado sempre
    db.session.delete(achado)
    db.session.commit()

    flash('Post excluído com sucesso!', 'success')
    return redirect(url_for('achados_bp.achados'))

@achados_bp.route('/achados')
def achados():
    achados = (
        db.session.query(Achado, Usuario)
        .join(Usuario, Usuario.id == Achado.usuario_id)
        .order_by(Achado.data_achado.desc())
        .all()
    )
    return render_template('achados_perdidos.html', achados=achados)