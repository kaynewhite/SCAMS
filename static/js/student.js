// Student Dashboard JavaScript

async function loadStudentRequirements() {
    try {
        const response = await fetch('/api/student-requirements');
        const data = await response.json();
        
        const container = document.getElementById('student-requirements');
        container.innerHTML = '';
        
        if (!data.requirements || data.requirements.length === 0) {
            container.innerHTML = '<p>No requirements posted yet.</p>';
            updateClearanceStatus(false, 0, 0);
            return;
        }
        
        data.requirements.forEach(req => {
            const item = document.createElement('div');
            item.className = `requirement-item ${req.completed ? 'completed' : ''}`;
            
            item.innerHTML = `
                <input type="checkbox" disabled ${req.completed ? 'checked' : ''}>
                <label>${req.name}</label>
            `;
            
            container.appendChild(item);
        });
        
        const completedCount = data.requirements.filter(r => r.completed).length;
        const totalCount = data.requirements.length;
        const allCompleted = completedCount === totalCount && totalCount > 0;
        
        updateClearanceStatus(data.clearance_submitted, completedCount, totalCount);
        
        // Show download button if clearance is submitted
        const downloadBtn = document.getElementById('download-clearance-btn');
        downloadBtn.style.display = data.clearance_submitted ? 'block' : 'none';
        
    } catch (error) {
        console.error('Error loading requirements:', error);
        document.getElementById('student-requirements').innerHTML = 
            '<p style="color: red;">Error loading requirements. Please try again.</p>';
    }
}

function updateClearanceStatus(submitted, completed, total) {
    const statusDiv = document.getElementById('clearance-status');
    
    if (submitted) {
        statusDiv.className = 'clearance-status completed';
        statusDiv.innerHTML = `
            <span>🎉 Congratulations! You have completed all requirements!</span><br>
            <span>Your clearance has been submitted and approved.</span><br>
            <span>You can now print your clearance certificate below.</span>
        `;
    } else if (completed === total && total > 0) {
        statusDiv.className = 'clearance-status completed';
        statusDiv.innerHTML = `
            <span>✅ You have completed all requirements!</span><br>
            <span>Please wait for admin approval to get your clearance.</span>
        `;
    } else {
        statusDiv.className = 'clearance-status pending';
        statusDiv.innerHTML = `
            <span>📋 Clearance Progress: ${completed}/${total} requirements completed</span><br>
            <span style="color: #dc3545; font-weight: bold;">⚠️ Please visit the SBO office to complete all requirements before downloading your clearance.</span>
        `;
    }
}

async function downloadClearance() {
    try {
        // Get the student's submitted clearance info to find the clearance ID
        const response = await fetch('/api/student-requirements');
        const data = await response.json();
        
        if (!data.clearance_submitted) {
            alert('Clearance not yet submitted. Please contact administration.');
            return;
        }
        
        // For now, we'll show a message since we need the clearance ID
        // In a full implementation, you'd get this from the API
        alert('Your clearance has been submitted successfully! Please contact the administrator to download your clearance certificate.');
        
    } catch (error) {
        console.error('Error downloading clearance:', error);
        alert('Error downloading clearance. Please try again.');
    }
}

// Initialize when page loads
document.addEventListener('DOMContentLoaded', function() {
    loadStudentRequirements();
});