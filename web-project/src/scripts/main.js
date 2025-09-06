// This file is intentionally left blank.
function hideAllSections() {
    document.getElementById('login-page').style.display = 'none';
    document.getElementById('register-page').style.display = 'none';
    document.getElementById('student-dashboard').style.display = 'none';
    document.getElementById('admin-dashboard').style.display = 'none';
}

// --- Navigation ---
function showRegisterPage() {
    hideAllSections();
    document.getElementById('register-page').style.display = 'block';
}
function showLoginPage() {
    hideAllSections();
    document.getElementById('login-page').style.display = 'block';
}
function logout() {
    hideAllSections();
    showLoginPage();
}

// --- Registration ---
function toggleMajorField() {
    const year = document.getElementById('reg-year').value;
    document.getElementById('major-field').style.display = (year === '3' || year === '4') ? 'block' : 'none';
}

function handleRegister(event) {
    event.preventDefault();
    const sn = document.getElementById('reg-student-number').value.trim();
    const name = document.getElementById('reg-name').value.trim();
    const course = document.getElementById('reg-course').value;
    const year = document.getElementById('reg-year').value;
    const major = document.getElementById('reg-major').value;
    const section = document.getElementById('reg-section').value;
    if (!sn.match(/^022\d-\d{4}$/)) {
        document.getElementById('register-error').textContent = "Student number format is invalid.";
        return false;
    }
    let students = JSON.parse(localStorage.getItem('students') || '[]');
    if (students.find(s => s.sn === sn)) {
        document.getElementById('register-error').textContent = "Student number already registered.";
        return false;
    }
    students.push({ sn, name, course, year, major, section, requirements: {}, clearance: false });
    localStorage.setItem('students', JSON.stringify(students));
    document.getElementById('register-error').textContent = "Registration successful! You can now login.";
    setTimeout(showLoginPage, 1200);
    return false;
}

// --- Login ---
function handleLogin(event) {
    event.preventDefault();
    const username = document.getElementById('login-username').value.trim();
    const password = document.getElementById('login-password').value;
    document.getElementById('login-error').textContent = "";
    if (username === 'adminadmin' && password === 'adminadmin') {
        hideAllSections();
        document.getElementById('admin-dashboard').style.display = 'block';
        loadAdminRequirements();
        loadStudentsList();
        return false;
    }
    let students = JSON.parse(localStorage.getItem('students') || '[]');
    let student = students.find(s => s.sn === username);
    if (student && password === student.sn) {
        hideAllSections();
        document.getElementById('student-dashboard').style.display = 'block';
        document.getElementById('student-number').value = student.sn;
        loadStudentRequirements();
        return false;
    }
    document.getElementById('login-error').textContent = "Invalid credentials.";
    return false;
}

// --- Requirements (Admin) ---
function showRequirementsPanel() {
    document.getElementById('requirements-panel').style.display = 'block';
    document.getElementById('signature-upload-panel').style.display = 'none';
}
function showSignatureUploadPanel() {
    document.getElementById('requirements-panel').style.display = 'none';
    document.getElementById('signature-upload-panel').style.display = 'block';
}

function addRequirement() {
    const req = document.getElementById('new-requirement').value.trim();
    if (!req) return;
    let requirements = JSON.parse(localStorage.getItem('requirements') || '[]');
    if (!requirements.includes(req)) requirements.push(req);
    localStorage.setItem('requirements', JSON.stringify(requirements));
    document.getElementById('new-requirement').value = '';
    loadAdminRequirements();
}

function loadAdminRequirements() {
    let requirements = JSON.parse(localStorage.getItem('requirements') || '[]');
    const ul = document.getElementById('admin-requirements-list');
    ul.innerHTML = '';
    requirements.forEach(r => {
        const li = document.createElement('li');
        li.textContent = r;
        ul.appendChild(li);
    });
}

// --- Signature Template Upload (Admin) ---
function uploadSignature() {
    const input = document.getElementById('signature-upload');
    const file = input.files[0];
    if (!file) return;
    const reader = new FileReader();
    reader.onload = function(e) {
        localStorage.setItem('signatureTemplate', e.target.result);
        document.getElementById('signature-preview').innerHTML = `<img src="${e.target.result}" style="max-width:100%;max-height:100px;">`;
    };
    reader.readAsDataURL(file);
}

// --- Student List & Filter (Admin) ---
function loadStudentsList(filter = {}) {
    let students = JSON.parse(localStorage.getItem('students') || '[]');
    // Filtering
    students = students.filter(s => {
        if (filter.sn && !s.sn.includes(filter.sn)) return false;
        if (filter.course && s.course !== filter.course) return false;
        if (filter.year && s.year !== filter.year) return false;
        if (filter.major && s.major !== filter.major) return false;
        if (filter.section && s.section !== filter.section) return false;
        return true;
    });
    const div = document.getElementById('students-list');
    div.innerHTML = '';
    if (students.length === 0) {
        div.textContent = "No students found.";
        return;
    }
    students.forEach(s => {
        let requirements = JSON.parse(localStorage.getItem('requirements') || '[]');
        let completed = requirements.filter(r => s.requirements && s.requirements[r]);
        let allCompleted = completed.length === requirements.length && requirements.length > 0;
        const studentDiv = document.createElement('div');
        studentDiv.style.borderBottom = "1px solid #ffd600";
        studentDiv.style.marginBottom = "1rem";
        studentDiv.innerHTML = `
            <strong>${s.name}</strong> (${s.sn})<br>
            ${s.course} Year ${s.year} ${s.major ? s.major : ''} Section ${s.section}<br>
            Completed: ${completed.length}/${requirements.length}
            <ul>${requirements.map(r => `<li>
                <label>
                    <input type="checkbox" ${s.requirements && s.requirements[r] ? 'checked' : ''} onchange="toggleStudentRequirement('${s.sn}','${r}',this.checked)">
                    ${r}
                </label>
            </li>`).join('')}</ul>
            <button ${allCompleted && !s.clearance ? '' : 'disabled'} onclick="submitClearance('${s.sn}')">Submit Clearance</button>
            <span style="color:${s.clearance ? '#002147' : '#c62828'};font-weight:600;">
                ${s.clearance ? 'Clearance Submitted' : ''}
            </span>
        `;
        div.appendChild(studentDiv);
    });
}

function toggleStudentRequirement(sn, req, checked) {
    let students = JSON.parse(localStorage.getItem('students') || '[]');
    let student = students.find(s => s.sn === sn);
    if (!student) return;
    if (!student.requirements) student.requirements = {};
    student.requirements[req] = checked;
    localStorage.setItem('students', JSON.stringify(students));
    loadStudentsList();
}

function submitClearance(sn) {
    let students = JSON.parse(localStorage.getItem('students') || '[]');
    let student = students.find(s => s.sn === sn);
    if (!student) return;
    student.clearance = true;
    localStorage.setItem('students', JSON.stringify(students));
    loadStudentsList();
}

// --- Search/Filter (Admin) ---
function searchStudents() {
    const sn = document.getElementById('search-student-number').value.trim();
    const course = document.getElementById('filter-course').value;
    const year = document.getElementById('filter-year').value;
    const major = document.getElementById('filter-major').value;
    const section = document.getElementById('filter-section').value;
    loadStudentsList({ sn, course, year, major, section });
}

// --- Student Dashboard ---
function loadStudentRequirements() {
    const sn = document.getElementById('student-number').value.trim();
    let students = JSON.parse(localStorage.getItem('students') || '[]');
    let student = students.find(s => s.sn === sn);
    if (!student) {
        document.getElementById('student-requirements').textContent = "Student not found.";
        return;
    }
    let requirements = JSON.parse(localStorage.getItem('requirements') || '[]');
    const div = document.getElementById('student-requirements');
    div.innerHTML = '';
    let completed = requirements.filter(r => student.requirements && student.requirements[r]);
    requirements.forEach(r => {
        const item = document.createElement('div');
        item.innerHTML = `<label>
            <input type="checkbox" disabled ${student.requirements && student.requirements[r] ? 'checked' : ''}>
            ${r}
        </label>`;
        div.appendChild(item);
    });
    // Clearance status
    const statusDiv = document.getElementById('clearance-status');
    if (student.clearance) {
        statusDiv.innerHTML = `<span style="color:#002147;font-weight:600;">You have completed all requirements! <br>Click below to print your clearance.</span>`;
        document.getElementById('print-clearance-btn').style.display = 'block';
    } else {
        statusDiv.innerHTML = `<span style="color:#c62828;">Clearance not yet completed.</span>`;
        document.getElementById('print-clearance-btn').style.display = 'none';
    }
}

function printClearance() {
    const sn = document.getElementById('student-number').value.trim();
    let students = JSON.parse(localStorage.getItem('students') || '[]');
    let student = students.find(s => s.sn === sn);
    if (!student) return;
    let requirements = JSON.parse(localStorage.getItem('requirements') || '[]');
    let completed = requirements.filter(r => student.requirements && student.requirements[r]);
    document.getElementById('clearance-template').style.display = 'block';
    const ul = document.getElementById('completed-req-list');
    ul.innerHTML = completed.map(r => `<li>${r}</li>`).join('');
    // Signature template
    const sigDiv = document.getElementById('signature-template');
    let sigImg = localStorage.getItem('signatureTemplate');
    sigDiv.innerHTML = `<p>Signatures:</p>` + (sigImg ? `<img src="${sigImg}" style="max-width:100%;max-height:100px;">` : `<div style="height:100px;"></div>`);
    setTimeout(() => {
        window.print();
        document.getElementById('clearance-template').style.display = 'none';
    }, 500);
}

// --- Initial Page Load ---
document.addEventListener('DOMContentLoaded', function() {
    showLoginPage();
    // For major field toggle on registration
    document.getElementById('reg-year').addEventListener('change', toggleMajorField);
});