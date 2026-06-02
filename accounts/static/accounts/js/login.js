const togglePassword = document.querySelector("#togglePassword");
const password = document.querySelector("#password");

if (togglePassword && password) {
    togglePassword.addEventListener("click", function () {
        const isHidden = password.getAttribute("type") === "password";
        password.setAttribute("type", isHidden ? "text" : "password");
        this.setAttribute("aria-pressed", String(isHidden));
        this.setAttribute("aria-label", isHidden ? "Ocultar contraseña" : "Mostrar contraseña");

        const icon = this.querySelector("i");
        icon.classList.toggle("fa-eye", !isHidden);
        icon.classList.toggle("fa-eye-slash", isHidden);
    });
}
