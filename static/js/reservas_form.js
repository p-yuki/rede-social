document.addEventListener("DOMContentLoaded", function () {
    const selectLocal = document.getElementById("local");

    // ler o JSON do data-attribute
    const reservasPorLocal = JSON.parse(selectLocal.dataset.reservas);

    let calendario = null;

    function iniciarCalendario(localSelecionado) {
        let datasBloqueadas = reservasPorLocal[localSelecionado] || [];

        // resetar calendário anterior
        if (calendario) {
            calendario.destroy();
        }

        calendario = flatpickr("#data_reserva", {
            enableTime: false,
            dateFormat: "Y-m-d",
            minDate: "today",
            disable: datasBloqueadas
        });
    }

    // inicializa ao entrar na página
    iniciarCalendario(selectLocal.value);

    // muda conforme troca o local
    selectLocal.addEventListener("change", function () {
        iniciarCalendario(this.value);
    });
});
