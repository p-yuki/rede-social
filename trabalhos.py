from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from werkzeug.utils import secure_filename
from models import db, Trabalho, Usuario, Foto
from utils import login_required, allowed_file
import os
from datetime import datetime
from flask import current_app as app

trabalhos_bp = Blueprint('trabalhos_bp', __name__)


@trabalhos_bp.route('/trabalhos/novo_trabalho', methods=['GET', 'POST'])
def novo_trabalho():
    if request.method == 'POST':
        descricao = request.form.get('descricao', '').strip()

        # Recebe o arquivo de foto
        arquivo_foto = request.files.get('foto')
        categoria = request.form.get('categoria')
        nome_trabalho = request.form.get('nome_trabalho')

        if not descricao:
            flash('A descrição é obrigatória!', 'danger')
            return render_template('trabalhos_form.html')

        foto_id = None

        # Processamento do upload da foto
        if arquivo_foto and arquivo_foto.filename != '':
            filename = arquivo_foto.filename
            if filename and allowed_file(filename):
                # Gera nome único para o arquivo
                nome_seguro = secure_filename(filename)
                unique_filename = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{nome_seguro}"

                # Salva arquivo na pasta de uploads
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
                os.makedirs(os.path.dirname(filepath), exist_ok=True)
                arquivo_foto.save(filepath)

                # Cria registro da foto no banco
                foto = Foto()
                foto.foto_path = unique_filename
                foto.usuario_id = session.get('user_id')
                foto.filename = nome_seguro

                db.session.add(foto)
                db.session.flush()  # Gera o id sem commit final
                foto_id = foto.id  # Pega o id da foto criada

        # Cria o trabalho (fora do bloco de upload)
        trabalho = Trabalho()
        trabalho.usuario_id = session.get('user_id')
        trabalho.foto_id = foto_id  # Salva o ID da foto
        trabalho.categoria = categoria
        trabalho.nome_trabalho = nome_trabalho
        trabalho.descricao = descricao
        db.session.add(trabalho)
        db.session.commit()

        flash('Trabalho criado com sucesso!', 'success')
        return redirect(url_for('trabalhos_bp.trabalhos'))

    return render_template('trabalhos_form.html')


@trabalhos_bp.route('/trabalhos/excluir/<int:trabalho_id>', methods=['POST'])
def excluir_trabalho(trabalho_id):
    trabalho = Trabalho.query.get_or_404(trabalho_id)

    # verifica se o usuário logado é o autor do post
    if trabalho.usuario_id != session.get('user_id'):
        flash('Você não tem permissão para excluir este post.', 'danger')
        return redirect(url_for('trabalhos_bp.trabalhos'))

    # se tiver foto, excluir foto física e do banco
    if trabalho.foto_id:
        foto = Foto.query.get(trabalho.foto_id)
        if foto:
            try:
                caminho_foto = os.path.join(app.config['UPLOAD_FOLDER'], foto.foto_path)
                if os.path.exists(caminho_foto):
                    os.remove(caminho_foto)
            except Exception as e:
                print(f"Erro ao excluir o arquivo da foto: {e}")

            db.session.delete(foto)

    # excluir o Trabalho sempre
    db.session.delete(trabalho)
    db.session.commit()

    flash('Post excluído com sucesso!', 'success')
    return redirect(url_for('trabalhos_bp.trabalhos'))


@trabalhos_bp.route('/trabalhos')
def trabalhos():
    # Adicionado 'Foto' à query e feito o outerjoin
    trabalhos = (
        db.session.query(Trabalho, Usuario, Foto)
        .join(Usuario, Usuario.id == Trabalho.usuario_id)
        .outerjoin(Foto, Foto.id == Trabalho.foto_id)
        .order_by(Trabalho.data_trabalho.desc())
        .all()
    )

    return render_template('trabalhos.html', trabalhos=trabalhos)
