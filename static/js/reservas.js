document.addEventListener("DOMContentLoaded", function () {
    const calendarDiv = document.getElementById("calendario_reservas");

    console.log("reservas.js carregou!");
    console.log("RAW JSON:", calendarDiv.dataset.datasOcupadas);

    let datasOcupadas = {};

    try {
        datasOcupadas = JSON.parse(calendarDiv.dataset.datasOcupadas || "{}");
        console.log("Datas ocupadas parseadas:", datasOcupadas);
    } catch (e) {
        console.error("Erro ao ler JSON:", e);
        return;
    }

    flatpickr(calendarDiv, {
        inline: true,
        locale: "pt",
        disableMobile: true,

        onDayCreate: function (dObj, dStr, fp, dayElem) {
            const d = dayElem.dateObj;

            const yyyy = d.getFullYear();
            const mm = String(d.getMonth() + 1).padStart(2, "0");
            const dd = String(d.getDate()).padStart(2, "0");

            const key = `${yyyy}-${mm}-${dd}`;

            if (datasOcupadas[key]) {
                const locais = datasOcupadas[key];
                
                console.log(`Data ${key} tem locais:`, locais);

                // Verificar quais locais estão reservados nesta data
                const temChurrasqueira = locais.includes("churrasqueira");
                const temSalao = locais.includes("salao_festa");

                if (temChurrasqueira && temSalao) {
                    dayElem.classList.add("dia-duplo");
                    console.log(`✅ Aplicado dia-duplo para ${key}`);
                } else if (temChurrasqueira) {
                    dayElem.classList.add("dia-churras");
                    console.log(`🔴 Aplicado dia-churras para ${key}`);
                } else if (temSalao) {
                    dayElem.classList.add("dia-festa");
                    console.log(`🔵 Aplicado dia-festa para ${key}`);
                }
            }
        }
    });
});