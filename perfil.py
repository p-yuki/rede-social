from flask import Blueprint, render_template, session
from models import Usuario
from utils import login_required

perfis_bp = Blueprint('perfis_bp', __name__)

@perfis_bp.route('/perfil')
@login_required
def perfil():
    user_id = session.get('user_id')

    usuario = Usuario.query.get(user_id)
    return render_template(
        'perfil.html',
        usuario=usuario
    )