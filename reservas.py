from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from models import db, Reserva, Usuario

reservas_bp = Blueprint('reservas_bp', __name__)

@reservas_bp.route('/reservas/nova_reserva', methods=['GET', 'POST'])
def nova_reserva():
    if request.method == 'POST':
        data_reserva = request.form.get('data_reserva', '').strip()
        local = request.form.get('local')

        # Evita reservas duplicadas
        reserva_existente = Reserva.query.filter_by(local=local, data_reserva=data_reserva).first()

        if reserva_existente:
            flash('Esta data já está reservada para este local.', 'danger')
            return redirect(url_for('reservas_bp.nova_reserva'))

        reserva = Reserva()
        reserva.usuario_id = session['user_id']
        reserva.data_reserva = data_reserva
        reserva.local = local

        db.session.add(reserva)
        db.session.commit()

        flash('Reserva criada com sucesso!', 'success')
        return redirect(url_for('reservas_bp.reservas'))

    # Monta datas ocupadas por local (para o calendário)
    reservas_por_local = {}
    reservas = Reserva.query.all()

    for r in reservas:
        data = r.data_reserva.strftime("%Y-%m-%d")
        reservas_por_local.setdefault(r.local, []).append(data)

    return render_template("reservas_form.html", reservas_por_local=reservas_por_local)

@reservas_bp.route('/reservas/excluir/<int:reserva_id>', methods=['POST'])
def excluir_reserva(reserva_id):
    reserva = Reserva.query.get_or_404(reserva_id)

    if reserva.usuario_id != session['user_id']:
        flash('Você não tem permissão para excluir esta reserva.', 'danger')
        return redirect(url_for('reservas_bp.reservas'))

    db.session.delete(reserva)
    db.session.commit()

    flash('Reserva excluída com sucesso!', 'success')
    return redirect(url_for('reservas_bp.reservas'))


@reservas_bp.route('/reservas')
def reservas():
    reservas = (
        db.session.query(Reserva, Usuario)
        .join(Usuario, Usuario.id == Reserva.usuario_id)
        .order_by(Reserva.data_reserva.desc())
        .all()
    )
    
    datas_ocupadas = {}

    for reserva, usuario in reservas:
        data = reserva.data_reserva.strftime("%Y-%m-%d")
        local = reserva.local  # "churrasqueira" ou "salao_festa"

        if data not in datas_ocupadas:
            datas_ocupadas[data] = []

        # Adiciona o local apenas se não estiver já na lista (evita duplicatas)
        if local not in datas_ocupadas[data]:
            datas_ocupadas[data].append(local)

    print("Datas ocupadas enviadas para template:", datas_ocupadas)  # Para debug

    local_reservas ={
        "salao_festa": "Salão de Festas",
        "churrasqueira": "Churrasqueira"
    }
    
    return render_template(
        "reservas.html",
        reservas=reservas,
        datas_ocupadas=datas_ocupadas, local_reservas=local_reservas
    )