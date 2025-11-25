from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from models import Usuario, Trabalho, Achado
from utils import login_required

perfis_bp = Blueprint('perfis_bp', __name__)

@perfis_bp.route('/perfil')
@login_required
def perfil():
    user_id = session.get('user_id')

    usuario = Usuario.query.get(user_id)

    # Buscar trabalhos do próprio usuário
    trabalhos_usuario = Trabalho.query.filter_by(usuario_id=user_id).order_by(Trabalho.data_trabalho.desc()).all()

    # Buscar achados do próprio usuário
    achados_usuario = Achado.query.filter_by(usuario_id=user_id).order_by(Achado.data_encontro.desc()).all()

    return render_template(
        'perfil.html',
        usuario=usuario,
        trabalhos=trabalhos_usuario,
        achados=achados_usuario
    )

