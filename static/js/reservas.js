document.addEventListener("DOMContentLoaded", function () {

    const calendarDiv = document.getElementById("calendario_reservas");

    console.log("reservas.js carregou!");
    console.log("RAW JSON:", calendarDiv.dataset.datasOcupadas);

    let datasOcupadas = {};

    try {
        datasOcupadas = JSON.parse(calendarDiv.dataset.datasOcupadas || "{}");
        console.log("Parsed:", datasOcupadas);
    } catch (e) {
        console.error("Erro ao ler JSON:", e);
        return;
    }

    flatpickr(calendarDiv, {
        inline: true,
        locale: "pt",
        disableMobile: true,

        onDayCreate: function (_, __, ___, dayElem) {
            const d = dayElem.dateObj;

            const yyyy = d.getFullYear();
            const mm = String(d.getMonth() + 1).padStart(2, "0");
            const dd = String(d.getDate()).padStart(2, "0");

            const key = `${yyyy}-${mm}-${dd}`;

            if (datasOcupadas[key]) {
                const tipos = datasOcupadas[key];

                if (tipos.length === 2) {
                    dayElem.classList.add("dia-duplo");
                } else if (tipos[0] === "festa") {
                    dayElem.classList.add("dia-festa");
                } else if (tipos[0] === "churrasqueira") {
                    dayElem.classList.add("dia-churras");
                }
            }
        }
    });
});
