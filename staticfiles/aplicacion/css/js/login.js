document.addEventListener('DOMContentLoaded', function() {
    var loginForm = document.getElementById('login-form');
  
    loginForm.addEventListener('submit', function(event) {
        var username = document.getElementById('id_username').value;
        var password = document.getElementById('id_password').value;
        var errorMessage = document.getElementById('error-message');
  
        if (!username || !password) {
            errorMessage.textContent = 'Por favor, completa todos los campos.';
            event.preventDefault();
  
            // Resaltar campos que faltan
            if (!username) {
                document.getElementById('id_username').classList.add('is-invalid');
            }
            if (!password) {
                document.getElementById('id_password').classList.add('is-invalid');
            }
        } else {
            // Restablecer estilos y opacidad después de la animación
            document.getElementById('id_username').classList.remove('is-invalid');
            document.getElementById('id_password').classList.remove('is-invalid');
            loginForm.style.opacity = '0.5';
            setTimeout(function() {
                loginForm.style.opacity = '1';
            }, 1000);
        }
    });
  });