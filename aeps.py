from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from werkzeug.utils import secure_filename
from models import db, Aep, Usuario, Foto
from utils import login_required, allowed_file
import os
from datetime import datetime
from flask import current_app as app

aeps_bp = Blueprint('aeps_bp', __name__)

@aeps_bp.route('/aeps/novo_aep', methods=['GET', 'POST'])
def novo_aeps():
    if request.method == 'POST':
        descricao = request.form.get('descricao', '').strip()
        arquivo_foto = request.files.get('foto')
        titulo = request.form.get('titulo')
        local = request.form.get('local')
        status = request.form.get('status')
        data_encontro = request.form.get('data_encontro')

        if not descricao:
            flash('A descrição é obrigatória!', 'danger')
            return render_template('achados_perdidos_form.html')

        foto_id = None
        
        # Upload da foto
        if arquivo_foto and arquivo_foto.filename != '':
            filename = arquivo_foto.filename

            if filename and allowed_file(filename):
                nome_seguro = secure_filename(filename)

                unique_filename = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{nome_seguro}"

                filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
                os.makedirs(os.path.dirname(filepath), exist_ok=True)

                arquivo_foto.save(filepath)

                foto = Foto(
                    usuario_id=session['user_id'],
                    filename=nome_seguro,
                    foto_path=unique_filename
                )

                db.session.add(foto)
                db.session.flush()

                foto_id = foto.id

        aep = Aep(
            usuario_id=session['user_id'],
            foto_id=foto_id,
            descricao=descricao,
            status=status,
            titulo=titulo,
            local=local,
            data_encontro=data_encontro
        )

        db.session.add(aep)
        db.session.commit()

        flash('Aep criado com sucesso!', 'success')
        return redirect(url_for('aeps_bp.aeps'))

    return render_template('achados_perdidos_form.html')


@aeps_bp.route('/aeps/excluir/<int:aep_id>', methods=['POST'])
def excluir_aep(aep_id):
    aep = Aep.query.get_or_404(aep_id)

    if aep.usuario_id != session['user_id']:
        flash('Você não tem permissão para excluir este post.', 'danger')
        return redirect(url_for('aeps_bp.aeps'))

    if aep.foto_id:
        foto = Foto.query.get(aep.foto_id)

        if foto:
            try:
                caminho_foto = os.path.join(app.config['UPLOAD_FOLDER'], foto.foto_path)
                if os.path.exists(caminho_foto):
                    os.remove(caminho_foto)
            except Exception as e:
                print(f"Erro ao excluir imagem: {e}")

            db.session.delete(foto)

    db.session.delete(aep)
    db.session.commit()

    flash('Post excluído com sucesso!', 'success')
    return redirect(url_for('aeps_bp.aeps'))


@aeps_bp.route('/aeps')
def aeps():

    # Retornando Aep, Usuario e Foto
    aeps = (
        db.session.query(Aep, Usuario, Foto)
        .join(Usuario, Usuario.id == Aep.usuario_id)
        .outerjoin(Foto, Foto.id == Aep.foto_id)
        .order_by(Aep.data_aep.desc())
        .all()
    )

    return render_template('achados_perdidos.html', aeps=aeps)
