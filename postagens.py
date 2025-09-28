from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from werkzeug.utils import secure_filename
from models import db, Postagem, Usuario, Foto
from utils import login_required, allowed_file
import os
from datetime import datetime
from app import app

postagens_bp = Blueprint('postagens_bp', __name__)
@postagens_bp.route('postagens/novo')
def novo():
    return render_template('novo_post.html')


@postagens_bp.route('postagens/criar_post', methods=['GET', 'POST'])
@login_required
def criar_postagem():
    if request.method == 'POST':
        descricao = request.form.get('descricao', '').strip()
        arquivo_foto = request.files.get('foto')
        
        if not descricao:
            flash('A descrição é obrigatória!', 'danger')
            return render_template('criar_post.html')
        
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
        postagem = Postagem()
        postagem.usuario_id = session['user_id']
        postagem.foto_id = foto_id
        postagem.status = 'pendente'
        db.session.add(postagem)
        db.session.commit()
        
        flash('Postagem criada com sucesso!', 'success')
        return redirect(url_for('posts_bp.feed'))
    
    return render_template('criar_post.html')

@postagens_bp.route('/postagens/excluir/<int:post_id>', methods=['POST'])
@login_required
def excluir_post(post_id):
    post = Postagem.query.get_or_404(post_id)
        
    #verifica se o usuário logado é o autor do post
    if post.usuario_id != session['user_id']:
        flash('Você não tem permissão para excluir este post.', 'danger')
        return redirect(url_for('postagens_bp.listar_posts'))
        
    #verifica se o post tem uma foto associada para excluir
    if post.foto_id:
        foto = Foto.query.get(post.foto_id)
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
        
        #exclui o post
        db.session.delete(post)
        db.session.commit()
        
    flash('Post excluído com sucesso!', 'success')
    
    return redirect(url_for('postagens_bp.listar_posts'))

@postagens_bp.route('postagens/postagem_feed')
def listar_posts():
    posts = Postagem.query.join(Usuario).add_columns(
        Postagem.id, 
        Postagem.descricao, 
        Postagem.foto_id, 
        Postagem.data_postagem,
        Usuario.nome.label('autor_nome')
    ).order_by(Postagem.data_postagem.desc()).all()
    
    return render_template('feed.html', posts=posts)


