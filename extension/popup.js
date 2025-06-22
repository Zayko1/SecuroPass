const API_URL = "http://217.154.24.244:5000";

document.getElementById("login-form").addEventListener("submit", async (e) => {
    e.preventDefault();
    const username = document.getElementById("username").value;
    const password = document.getElementById("password").value;
    const response = await fetch(`${API_URL}/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, password })
    });
    if (response.ok) {
        // Gère la suite ici (exemple : afficher les mots de passe)
    } else {
        document.getElementById("login-error").innerText = "Échec de la connexion";
    }
});


async function loadPasswords() {
    document.getElementById("login-section").style.display = "none";
    document.getElementById("passwords-section").style.display = "block";
    const token = sessionStorage.getItem("token");
    const response = await fetch(`${API_URL}/passwords`, {
        headers: { "Authorization": `Bearer ${token}` }
    });
    if (response.ok) {
        const data = await response.json();
        const list = document.getElementById("passwords-list");
        list.innerHTML = "";
        data.passwords.forEach(pwd => {
            const li = document.createElement("li");
            li.textContent = `${pwd.service} : ${pwd.username} / ${pwd.password}`;
            list.appendChild(li);
        });
    } else {
        document.getElementById("passwords-list").innerHTML = "Erreur lors du chargement";
    }
}

document.getElementById("logout-btn").addEventListener("click", () => {
    sessionStorage.removeItem("token");
    document.getElementById("login-section").style.display = "block";
    document.getElementById("passwords-section").style.display = "none";
});
