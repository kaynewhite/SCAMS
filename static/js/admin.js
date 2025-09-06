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
        
        const ul = document.getElementById('admin-requirements-list');
        ul.innerHTML = '';
        
        requirements.forEach(req => {
            const li = document.createElement('li');
            li.textContent = req.name;
            ul.appendChild(li);
        });
    } catch (error) {
        console.error('Error loading requirements:', error);
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

// Initialize when page loads
document.addEventListener('DOMContentLoaded', function() {
    loadAdminRequirements();
    loadStudentsList();
});