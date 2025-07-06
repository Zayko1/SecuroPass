// ==================== static/js/passwords.js ====================
let passwords = [];
let currentEditId = null;

// Au chargement de la page
document.addEventListener('DOMContentLoaded', function() {
    loadPasswords();
    setupEventListeners();
});

// Configuration des écouteurs d'événements
function setupEventListeners() {
    // Recherche
    document.getElementById('searchInput').addEventListener('input', function(e) {
        filterPasswords(e.target.value);
    });

    // Formulaire d'ajout
    document.getElementById('addPasswordForm').addEventListener('submit', function(e) {
        e.preventDefault();
        addPassword();
    });

    // Formulaire de modification
    document.getElementById('editPasswordForm').addEventListener('submit', function(e) {
        e.preventDefault();
        updatePassword();
    });

    // Toggle password visibility
    document.getElementById('toggleAddPassword').addEventListener('click', function() {
        togglePasswordVisibility('addPassword', this);
    });

    document.getElementById('toggleEditPassword').addEventListener('click', function() {
        togglePasswordVisibility('editPassword', this);
    });

    // Générateur de mot de passe
    document.getElementById('generatePassword').addEventListener('click', function() {
        $('#generatorModal').modal('show');
        generateNewPassword();
    });

    // Slider de longueur
    document.getElementById('genLength').addEventListener('input', function(e) {
        document.getElementById('lengthValue').textContent = e.target.value;
        generateNewPassword();
    });

    // Checkboxes du générateur
    ['genLower', 'genUpper', 'genDigits', 'genSpecial'].forEach(id => {
        document.getElementById(id).addEventListener('change', generateNewPassword);
    });

    // Bouton régénérer
    document.getElementById('regeneratePassword').addEventListener('click', generateNewPassword);

    // Utiliser le mot de passe généré
    document.getElementById('useGeneratedPassword').addEventListener('click', function() {
        const password = document.getElementById('generatedPassword').value;
        document.getElementById('addPassword').value = password;
        checkPasswordStrength('addPassword', 'addPasswordStrength');
        $('#generatorModal').modal('hide');
    });

    // Vérification de la force du mot de passe
    document.getElementById('addPassword').addEventListener('input', function() {
        checkPasswordStrength('addPassword', 'addPasswordStrength');
    });

    document.getElementById('editPassword').addEventListener('input', function() {
        checkPasswordStrength('editPassword', 'editPasswordStrength');
    });
}

// Charger les mots de passe
function loadPasswords() {
    fetch('/api/passwords')
        .then(response => response.json())
        .then(data => {
            passwords = data;
            displayPasswords(passwords);
        })
        .catch(error => {
            console.error('Erreur :', error);
            showAlert('Erreur lors du chargement des mots de passe', 'danger');
        });
}

// Afficher les mots de passe
function displayPasswords(passwordList) {
    const tbody = document.getElementById('passwordsTableBody');
    const noPasswordsMsg = document.getElementById('noPasswordsMessage');
    const table = document.getElementById('passwordsTable');

    tbody.innerHTML = '';

    if (passwordList.length === 0) {
        table.style.display = 'none';
        noPasswordsMsg.style.display = 'block';
        return;
    }

    table.style.display = 'table';
    noPasswordsMsg.style.display = 'none';

    passwordList.forEach(password => {
        const tr = document.createElement('tr');
        
        const levelClass = password.niveau === 'Fort' || password.niveau === 'Très Fort' ? 
            'text-success' : password.niveau === 'Moyen' ? 'text-warning' : 'text-danger';
        
        tr.innerHTML = `
            <td>${escapeHtml(password.titre)}</td>
            <td>${escapeHtml(password.identifiant)}</td>
            <td>
                <div class="d-flex align-items-center">
                    <span class="password-field" data-password="${escapeHtml(password.password)}">
                        ${password.masked_password}
                    </span>
                    <button class="btn btn-sm btn-outline-secondary ms-2" onclick="togglePassword(this)">
                        <i class="fas fa-eye"></i>
                    </button>
                    <button class="btn btn-sm btn-outline-secondary ms-1" onclick="copyPassword('${password.password}')">
                        <i class="fas fa-copy"></i>
                    </button>
                </div>
            </td>
            <td>
                ${password.site_web ? `<a href="${escapeHtml(password.site_web)}" target="_blank" class="text-info">
                    <i class="fas fa-external-link-alt"></i> Visiter
                </a>` : '-'}
            </td>
            <td><span class="${levelClass}">${password.niveau}</span></td>
            <td>${password.date_ajout}</td>
            <td>
                <button class="btn btn-sm btn-primary" onclick="editPassword(${password.id})">
                    <i class="fas fa-edit"></i>
                </button>
                <button class="btn btn-sm btn-danger" onclick="deletePassword(${password.id})">
                    <i class="fas fa-trash"></i>
                </button>
            </td>
        `;
        
        tbody.appendChild(tr);
    });
}

// Filtrer les mots de passe
function filterPasswords(query) {
    if (!query) {
        displayPasswords(passwords);
        return;
    }

    const filtered = passwords.filter(p => 
        p.titre.toLowerCase().includes(query.toLowerCase()) ||
        p.identifiant.toLowerCase().includes(query.toLowerCase()) ||
        (p.site_web && p.site_web.toLowerCase().includes(query.toLowerCase()))
    );
    
    displayPasswords(filtered);
}

// Ajouter un mot de passe
function addPassword() {
    const data = {
        title: document.getElementById('addTitle').value,
        identifier: document.getElementById('addIdentifier').value,
        password: document.getElementById('addPassword').value,
        site: document.getElementById('addSite').value,
        notes: document.getElementById('addNotes').value
    };

    fetch('/api/passwords', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(result => {
        if (result.success) {
            $('#addPasswordModal').modal('hide');
            document.getElementById('addPasswordForm').reset();
            loadPasswords();
            showAlert('Mot de passe ajouté avec succès', 'success');
        } else {
            showAlert(result.error || 'Erreur lors de l\'ajout', 'danger');
        }
    })
    .catch(error => {
        console.error('Erreur:', error);
        showAlert('Erreur lors de l\'ajout du mot de passe', 'danger');
    });
}

// Modifier un mot de passe
function editPassword(id) {
    const password = passwords.find(p => p.id === id);
    if (!password) return;

    currentEditId = id;
    document.getElementById('editId').value = id;
    document.getElementById('editTitle').value = password.titre;
    document.getElementById('editIdentifier').value = password.identifiant;
    document.getElementById('editPassword').value = password.password;
    document.getElementById('editSite').value = password.site_web || '';
    document.getElementById('editNotes').value = password.notes || '';

    checkPasswordStrength('editPassword', 'editPasswordStrength');
    $('#editPasswordModal').modal('show');
}

// Mettre à jour un mot de passe
function updatePassword() {
    const data = {
        title: document.getElementById('editTitle').value,
        identifier: document.getElementById('editIdentifier').value,
        password: document.getElementById('editPassword').value,
        site: document.getElementById('editSite').value,
        notes: document.getElementById('editNotes').value
    };

    fetch(`/api/passwords/${currentEditId}`, {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(result => {
        if (result.success) {
            $('#editPasswordModal').modal('hide');
            loadPasswords();
            showAlert('Mot de passe modifié avec succès', 'success');
        } else {
            showAlert(result.error || 'Erreur lors de la modification', 'danger');
        }
    })
    .catch(error => {
        console.error('Erreur:', error);
        showAlert('Erreur lors de la modification du mot de passe', 'danger');
    });
}

// Supprimer un mot de passe
function deletePassword(id) {
    if (!confirm('Êtes-vous sûr de vouloir supprimer ce mot de passe ?')) {
        return;
    }

    fetch(`/api/passwords/${id}`, {
        method: 'DELETE'
    })
    .then(response => response.json())
    .then(result => {
        if (result.success) {
            loadPasswords();
            showAlert('Mot de passe supprimé avec succès', 'success');
        } else {
            showAlert(result.error || 'Erreur lors de la suppression', 'danger');
        }
    })
    .catch(error => {
        console.error('Erreur:', error);
        showAlert('Erreur lors de la suppression du mot de passe', 'danger');
    });
}

// Basculer la visibilité du mot de passe
function togglePassword(button) {
    const span = button.parentElement.querySelector('.password-field');
    const icon = button.querySelector('i');
    
    if (span.textContent === span.dataset.password) {
        span.textContent = '********';
        icon.classList.remove('fa-eye-slash');
        icon.classList.add('fa-eye');
    } else {
        span.textContent = span.dataset.password;
        icon.classList.remove('fa-eye');
        icon.classList.add('fa-eye-slash');
    }
}

// Basculer la visibilité des champs de mot de passe
function togglePasswordVisibility(inputId, button) {
    const input = document.getElementById(inputId);
    const icon = button.querySelector('i');
    
    if (input.type === 'password') {
        input.type = 'text';
        icon.classList.remove('fa-eye');
        icon.classList.add('fa-eye-slash');
    } else {
        input.type = 'password';
        icon.classList.remove('fa-eye-slash');
        icon.classList.add('fa-eye');
    }
}

// Copier le mot de passe
function copyPassword(password) {
    navigator.clipboard.writeText(password).then(() => {
        showAlert('Mot de passe copié dans le presse-papiers', 'success');
    }).catch(err => {
        console.error('Erreur lors de la copie:', err);
        showAlert('Erreur lors de la copie du mot de passe', 'danger');
    });
}

// Générer un nouveau mot de passe
function generateNewPassword() {
    const length = parseInt(document.getElementById('genLength').value);
    const options = {
        length: length,
        include_lower: document.getElementById('genLower').checked,
        include_upper: document.getElementById('genUpper').checked,
        include_digits: document.getElementById('genDigits').checked,
        include_special: document.getElementById('genSpecial').checked
    };

    fetch('/api/generate-password', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(options)
    })
    .then(response => response.json())
    .then(result => {
        document.getElementById('generatedPassword').value = result.password;
        updateStrengthIndicator('genPasswordStrength', result.level);
    })
    .catch(error => {
        console.error('Erreur:', error);
        showAlert('Erreur lors de la génération du mot de passe', 'danger');
    });
}

// Vérifier la force du mot de passe
function checkPasswordStrength(inputId, strengthId) {
    const password = document.getElementById(inputId).value;
    
    if (!password) {
        document.getElementById(strengthId).className = 'password-strength';
        return;
    }

    fetch('/api/password-strength', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ password: password })
    })
    .then(response => response.json())
    .then(result => {
        updateStrengthIndicator(strengthId, result.level);
    })
    .catch(error => {
        console.error('Erreur:', error);
    });
}

// Mettre à jour l'indicateur de force
function updateStrengthIndicator(indicatorId, level) {
    const indicator = document.getElementById(indicatorId);
    
    if (level === 'Faible') {
        indicator.className = 'password-strength strength-weak';
    } else if (level === 'Moyen') {
        indicator.className = 'password-strength strength-medium';
    } else {
        indicator.className = 'password-strength strength-strong';
    }
}

// Afficher une alerte
function showAlert(message, type) {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    const container = document.querySelector('.container');
    container.insertBefore(alertDiv, container.firstChild);
    
    // Auto-fermeture après 5 secondes
    setTimeout(() => {
        alertDiv.remove();
    }, 5000);
}

// Échapper le HTML
function escapeHtml(text) {
    const map = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#039;'
    };
    return text.replace(/[&<>"']/g, m => map[m]);
}
