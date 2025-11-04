from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from utils import login_required

perfis_bp = Blueprint('perfis_bp', __name__)

@perfis_bp.route('/perfil')
@login_required
def perfil():
    usuario_data = {
        'nome': session.get('usuario.name'),
        'bloco': session.get('usuario.bloco'),
        'apartamento': session.get('usuario.apartamento'),
        'foto': session.get('usuario.foto')
    }
    return render_template('perfil.html', usuario=usuario_data)
