// Tab Management
function showTab(tabName) {
    // Hide all tab content
    document.querySelectorAll('.tab-content').forEach(tab => {
        tab.classList.remove('active');
    });
    
    // Remove active class from all tab buttons
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    
    // Show selected tab
    document.getElementById(tabName + '-tab').classList.add('active');
    
    // Add active class to clicked button
    event.target.classList.add('active');
    
    // Load content based on tab
    if (tabName === 'requirements') {
        loadAdminRequirements();
    } else if (tabName === 'students') {
        loadStudentsList();
    } else if (tabName === 'student-list') {
        loadAllStudentsList();
    } else if (tabName === 'clearances') {
        loadSubmittedClearances();
    }
}

// Requirements Management
async function addRequirement() {
    const reqName = document.getElementById('new-requirement').value.trim();
    if (!reqName) {
        alert('Please enter a requirement name');
        return;
    }
    
    try {
        const response = await fetch('/api/requirements', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ name: reqName })
        });
        
        const result = await response.json();
        if (result.success) {
            document.getElementById('new-requirement').value = '';
            loadAdminRequirements();
        } else {
            alert(result.message || 'Failed to add requirement');
        }
    } catch (error) {
        alert('Error adding requirement: ' + error.message);
    }
}

async function loadAdminRequirements() {
    try {
        const response = await fetch('/api/requirements');
        const requirements = await response.json();
        
        const container = document.getElementById('admin-requirements-list');
        container.innerHTML = '';
        
        if (requirements.length === 0) {
            container.innerHTML = '<p class="no-data">No requirements posted yet.</p>';
            return;
        }
        
        requirements.forEach(req => {
            const reqCard = document.createElement('div');
            reqCard.className = 'requirement-card';
            reqCard.innerHTML = `
                <div class="requirement-content">
                    <span class="requirement-name">${req.name}</span>
                    <button class="btn-danger btn-small" onclick="deleteRequirement(${req.id})">Delete</button>
                </div>
            `;
            container.appendChild(reqCard);
        });
    } catch (error) {
        console.error('Error loading requirements:', error);
    }
}

async function deleteRequirement(reqId) {
    if (!confirm('Are you sure you want to delete this requirement? This will remove it from all students.')) {
        return;
    }
    
    try {
        const response = await fetch(`/api/requirements/${reqId}`, {
            method: 'DELETE'
        });
        
        const result = await response.json();
        if (result.success) {
            loadAdminRequirements();
            loadStudentsList(); // Refresh students list too
        } else {
            alert(result.message || 'Failed to delete requirement');
        }
    } catch (error) {
        alert('Error deleting requirement: ' + error.message);
    }
}

async function loadSubmittedClearances() {
    try {
        const response = await fetch('/api/submitted-clearances');
        const clearances = await response.json();
        
        const container = document.getElementById('submitted-clearances-list');
        container.innerHTML = '';
        
        if (clearances.length === 0) {
            container.innerHTML = '<p class="no-data">No clearances submitted yet.</p>';
            return;
        }
        
        clearances.forEach(clearance => {
            const clearanceCard = document.createElement('div');
            clearanceCard.className = 'clearance-card';
            clearanceCard.innerHTML = `
                <div class="clearance-header">
                    <div class="clearance-info">
                        <h4>${clearance.student_name}</h4>
                        <p>Student Number: ${clearance.student_number}</p>
                        <p>Submitted: ${new Date(clearance.submitted_date).toLocaleDateString()}</p>
                    </div>
                    <div class="clearance-actions">
                        <button onclick="undoSubmission(${clearance.student_id})" class="btn btn-warning">Undo Submission</button>
                    </div>
                </div>
            `;
            container.appendChild(clearanceCard);
        });
    } catch (error) {
        console.error('Error loading submitted clearances:', error);
    }
}

// Signature Template Upload
async function uploadSignature() {
    const fileInput = document.getElementById('signature-upload');
    const file = fileInput.files[0];
    
    if (!file) {
        alert('Please select a file');
        return;
    }
    
    const formData = new FormData();
    formData.append('signature', file);
    
    try {
        const response = await fetch('/api/signature-template', {
            method: 'POST',
            body: formData
        });
        
        const result = await response.json();
        if (result.success) {
            document.getElementById('signature-preview').innerHTML = 
                `<img src="${result.file_path}" alt="Signature Template" style="max-width:100%;max-height:200px;">`;
            alert('Signature template uploaded successfully');
        } else {
            alert(result.message || 'Failed to upload signature template');
        }
    } catch (error) {
        alert('Error uploading signature: ' + error.message);
    }
}

// Student Management
async function loadStudentsList(filters = {}) {
    try {
        const queryParams = new URLSearchParams(filters);
        const response = await fetch(`/api/students?${queryParams}`);
        const data = await response.json();
        
        const container = document.getElementById('students-list');
        container.innerHTML = '';
        
        if (data.students.length === 0) {
            container.innerHTML = '<p class="no-students">No students found.</p>';
            return;
        }
        
        data.students.forEach(student => {
            const studentCard = createStudentCard(student, data.requirements);
            container.appendChild(studentCard);
        });
    } catch (error) {
        console.error('Error loading students:', error);
    }
}

function createStudentCard(student, requirements) {
    const card = document.createElement('div');
    card.className = 'student-card';
    
    const completedReqs = student.requirements.filter(r => r.completed);
    const allCompleted = completedReqs.length === requirements.length && requirements.length > 0;
    const clearanceStatus = student.clearance_submitted ? 'completed' : 'pending';
    
    card.innerHTML = `
        <div class="student-header">
            <div class="student-info">
                <h4>${student.name}</h4>
                <div class="student-details">
                    ${student.username} | ${student.course} Year ${student.year} 
                    ${student.major ? student.major : ''} Section ${student.section}
                </div>
            </div>
            <div class="clearance-status ${clearanceStatus}">
                ${student.clearance_submitted ? 'Clearance Submitted' : 'Pending'}
            </div>
        </div>
        <div class="progress-info">
            <strong>Completed: ${completedReqs.length}/${requirements.length}</strong>
        </div>
        <div class="requirements-grid">
            ${requirements.map(req => {
                const completed = student.requirements.find(r => r.requirement_id === req.id)?.completed || false;
                return `
                    <div class="requirement-item">
                        <input type="checkbox" 
                               ${completed ? 'checked' : ''} 
                               onchange="toggleStudentRequirement(${student.id}, ${req.id}, this.checked)">
                        <label>${req.name}</label>
                    </div>
                `;
            }).join('')}
        </div>
        <div class="card-actions">
            <button class="btn-success" 
                    ${allCompleted && !student.clearance_submitted ? '' : 'disabled'} 
                    onclick="submitClearance(${student.id})">
                Submit Clearance
            </button>
        </div>
    `;
    
    return card;
}

async function toggleStudentRequirement(studentId, requirementId, completed) {
    try {
        const response = await fetch('/api/student-requirement', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                student_id: studentId,
                requirement_id: requirementId,
                completed: completed
            })
        });
        
        const result = await response.json();
        if (result.success) {
            loadStudentsList(getCurrentFilters());
        } else {
            alert(result.message || 'Failed to update requirement');
        }
    } catch (error) {
        alert('Error updating requirement: ' + error.message);
    }
}

async function submitClearance(studentId) {
    try {
        const response = await fetch('/api/submit-clearance', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ student_id: studentId })
        });
        
        const result = await response.json();
        if (result.success) {
            loadStudentsList(getCurrentFilters());
            alert('Clearance submitted successfully!');
        } else {
            alert(result.message || 'Failed to submit clearance');
        }
    } catch (error) {
        alert('Error submitting clearance: ' + error.message);
    }
}

function searchStudents() {
    const filters = getCurrentFilters();
    loadStudentsList(filters);
}

function getCurrentFilters() {
    return {
        student_number: document.getElementById('search-student-number').value,
        course: document.getElementById('filter-course').value,
        year: document.getElementById('filter-year').value,
        major: document.getElementById('filter-major').value,
        section: document.getElementById('filter-section').value
    };
}

async function loadAllStudentsList() {
    try {
        const response = await fetch('/api/all-students');
        const students = await response.json();
        
        const container = document.getElementById('all-students-list');
        container.innerHTML = '';
        
        if (students.length === 0) {
            container.innerHTML = '<p class="no-data">No students registered yet.</p>';
            return;
        }
        
        // Create table
        const table = document.createElement('table');
        table.className = 'students-table';
        
        // Create header
        const thead = document.createElement('thead');
        thead.innerHTML = `
            <tr>
                <th>Name</th>
                <th>Student Number</th>
                <th>Course</th>
                <th>Year Level</th>
                <th>Major</th>
                <th>Section</th>
            </tr>
        `;
        table.appendChild(thead);
        
        // Create body
        const tbody = document.createElement('tbody');
        students.forEach(student => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td><strong>${student.name}</strong></td>
                <td>${student.username}</td>
                <td>${student.course}</td>
                <td>${student.year}</td>
                <td>${student.major || 'N/A'}</td>
                <td>${student.section}</td>
            `;
            tbody.appendChild(row);
        });
        
        table.appendChild(tbody);
        container.appendChild(table);
        
    } catch (error) {
        console.error('Error loading all students:', error);
    }
}

async function clearAllRequirements() {
    if (!confirm('Are you sure you want to clear ALL requirements? This will also revert all submitted clearances to pending status.')) {
        return;
    }
    
    try {
        const response = await fetch('/api/clear-all-requirements', {
            method: 'POST'
        });
        
        const result = await response.json();
        if (result.success) {
            alert('All requirements cleared and submitted clearances reverted to pending.');
            loadAdminRequirements();
            loadStudentsList();
            loadSubmittedClearances();
        } else {
            alert('Error: ' + result.message);
        }
    } catch (error) {
        console.error('Error clearing requirements:', error);
        alert('Error clearing requirements');
    }
}

async function undoSubmission(studentId) {
    if (!confirm('Are you sure you want to undo this student\'s clearance submission?')) {
        return;
    }
    
    try {
        const response = await fetch('/api/undo-submission', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ student_id: studentId })
        });
        
        const result = await response.json();
        if (result.success) {
            alert('Submission undone successfully.');
            loadSubmittedClearances();
            loadStudentsList();
        } else {
            alert('Error: ' + result.message);
        }
    } catch (error) {
        console.error('Error undoing submission:', error);
        alert('Error undoing submission');
    }
}

async function downloadAllClearances() {
    try {
        const response = await fetch('/download-all-clearances');
        if (response.ok) {
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'all_completed_clearances.csv';
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);
        } else {
            alert('Error downloading clearances');
        }
    } catch (error) {
        console.error('Error downloading clearances:', error);
        alert('Error downloading clearances');
    }
}

// Initialize when page loads
document.addEventListener('DOMContentLoaded', function() {
    loadAdminRequirements();
    loadStudentsList();
});