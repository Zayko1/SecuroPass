const API_URL = "https://217.154.24.244:5000";  // ton domaine en HTTPS

// Éléments du DOM
const loginSec = document.getElementById("login-section");
const pwdSec   = document.getElementById("passwords-section");
const loginErr = document.getElementById("login-error");
const pwdList  = document.getElementById("passwords-list");
const logoutBtn= document.getElementById("logout-btn");

// Gestion du formulaire de login (session-cookie)
document.getElementById("login-form").addEventListener("submit", async e => {
    e.preventDefault();
    loginErr.textContent = "";

    const username = document.getElementById("username").value.trim();
    const password = document.getElementById("password").value;
    const body     = new URLSearchParams({ username, password });

    try {
        const resp = await fetch(`${API_URL}/login`, {
            method: "POST",
            body,
            credentials: "include"
        });
        if (!resp.ok && !resp.redirected) {
            throw new Error("Identifiants incorrects");
        }
        // Connecté : on affiche la liste des mots de passe
        await showPasswords();
    } catch (err) {
        loginErr.textContent = err.message;
    }
});

// Affiche la section passwords et charge les données
async function showPasswords() {
    loginSec.style.display = "none";
    pwdSec.style.display   = "block";

    try {
        const resp = await fetch(`${API_URL}/api/passwords`, {
            credentials: "include"
        });
        if (!resp.ok) {
            throw new Error("Erreur lors du chargement des mots de passe");
        }

        // On récupère soit un array, soit { passwords: [...] }
        const data = await resp.json();
        const pwds = Array.isArray(data) ? data : (data.passwords || []);

        if (pwds.length === 0) {
            pwdList.innerHTML = `
                <li class="list-group-item bg-dark text-warning">
                    Aucun mot de passe trouvé.
                </li>`;
            return;
        }

        // On vide la liste
        pwdList.innerHTML = "";

        pwds.forEach(p => {
            // Création de l'item
            const li = document.createElement("li");
            li.className = "list-group-item bg-dark text-white d-flex justify-content-between align-items-center";

            // Texte : service + identifiant + mot masqué
            const txt = document.createElement("div");
            txt.innerHTML = `
                <strong>${p.service || p.titre}</strong><br>
                ${p.username || p.identifiant} /
                <span class="password-text">${p.masked_password}</span>
            `;

            // Bouton copier
            const copyBtn = document.createElement("button");
            copyBtn.className = "btn btn-outline-light btn-sm";
            copyBtn.innerHTML = `<i class="fas fa-clipboard"></i>`;
            copyBtn.addEventListener("click", async () => {
                try {
                    // copie le mot de passe clair
                    await navigator.clipboard.writeText(p.password);
                    copyBtn.innerHTML = `<i class="fas fa-check"></i>`;
                    setTimeout(() => {
                        copyBtn.innerHTML = `<i class="fas fa-clipboard"></i>`;
                    }, 1000);
                } catch {
                    alert("Échec de la copie");
                }
            });

            // Assemblage
            li.append(txt, copyBtn);
            pwdList.appendChild(li);
        });

    } catch (err) {
        pwdList.innerHTML = `
            <li class="list-group-item bg-dark text-danger">
                ${err.message}
            </li>`;
    }
}




// Déconnexion (session-cookie)
logoutBtn.addEventListener("click", async () => {
    await fetch(`${API_URL}/logout`, {
        credentials: "include"
    });
    // Retour à la vue login
    loginSec.style.display = "block";
    pwdSec.style.display   = "none";
    document.getElementById("login-form").reset();
});
