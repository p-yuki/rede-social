from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from werkzeug.utils import secure_filename
from models import db, Achado, Usuario, Foto
from utils import allowed_file
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
            # Adicione os valores do formulário para manter os dados digitados
            return render_template('achados_perdidos_form.html', 
                                    descricao=descricao,
                                    contato=contato,
                                    local=local,
                                    status=status,
                                    data_encontro=data_encontro)

        foto_id = None
        
        # processa o upload da foto se existir
        if arquivo_foto and arquivo_foto.filename != '':
            filename = arquivo_foto.filename

            if filename and allowed_file(filename):
                nome_seguro = secure_filename(filename)
                unique_filename = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{nome_seguro}"
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
                os.makedirs(os.path.dirname(filepath), exist_ok=True)

                arquivo_foto.save(filepath)

                foto = Foto()
                foto.foto_path = unique_filename
                foto.usuario_id = session.get('user_id')
                foto.filename = nome_seguro

                db.session.add(foto)
                db.session.flush()
                foto_id = foto.id
        
        # cria a postagem de achado
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

    # verifica se o usuário é o autor do post
    if achado.usuario_id != session['user_id']:
        flash('Você não tem permissão para excluir este post.', 'danger')
        return redirect(url_for('achados_bp.achados'))

    # exclui a foto associada se existir
    if achado.foto_id:
        foto = Foto.query.get(achado.foto_id)
        if foto:
            try:
                caminho_foto = os.path.join(app.config['UPLOAD_FOLDER'], foto.foto_path)
                if os.path.exists(caminho_foto):
                    os.remove(caminho_foto)
            except Exception as e:
                print(f"erro ao excluir imagem: {e}")

            db.session.delete(foto)

    db.session.delete(achado)
    db.session.commit()

    flash('Post excluído com sucesso!', 'success')
    return redirect(url_for('achados_bp.achados'))

@achados_bp.route('/achados')
def achados():
    # busca todos os achados com usuários ativos
    achados = (
        db.session.query(Achado, Usuario)
        .join(Usuario, Usuario.id == Achado.usuario_id)
        .filter(Usuario.is_active == True)
        .order_by(Achado.data_achado.desc())
        .all()
    )

    return render_template('achados_perdidos.html', achados=achados)