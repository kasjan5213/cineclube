document.addEventListener("DOMContentLoaded", () => {
    document.querySelectorAll("form[data-confirmar]").forEach((form) => {
        form.addEventListener("submit", (evento) => {
            const mensagem = form.getAttribute("data-confirmar");
            if (!window.confirm(mensagem)) {
                evento.preventDefault();
            }
        });
    });

    const alertas = document.querySelectorAll(".alerta");
    if (alertas.length) {
        setTimeout(() => {
            alertas.forEach((alerta) => {
                alerta.style.opacity = "0";
                alerta.style.transition = "opacity 400ms";
            });
        }, 4000);
    }
});
