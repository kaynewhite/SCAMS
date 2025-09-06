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
        
        // Show print button if clearance is submitted
        const printBtn = document.getElementById('print-clearance-btn');
        printBtn.style.display = data.clearance_submitted ? 'block' : 'none';
        
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
            <span>Please complete all requirements to receive your clearance.</span>
        `;
    }
}

async function printClearance() {
    try {
        const response = await fetch('/api/student-clearance');
        const data = await response.json();
        
        if (!data.clearance_submitted) {
            alert('Clearance not yet submitted. Please contact administration.');
            return;
        }
        
        // Populate the clearance template
        const template = document.getElementById('clearance-template');
        const reqList = document.getElementById('completed-req-list');
        const signatureDisplay = document.getElementById('signature-template-display');
        
        // Clear and populate requirements list
        reqList.innerHTML = '';
        data.completed_requirements.forEach(req => {
            const li = document.createElement('li');
            li.textContent = req.name;
            reqList.appendChild(li);
        });
        
        // Set signature template or placeholder
        if (data.signature_template) {
            signatureDisplay.innerHTML = `<img src="${data.signature_template}" alt="Official Signatures">`;
        } else {
            signatureDisplay.innerHTML = '<p style="text-align: center; padding: 2rem;">Signature template will be added here</p>';
        }
        
        // Show template and print
        template.style.display = 'block';
        
        setTimeout(() => {
            window.print();
            template.style.display = 'none';
        }, 500);
        
    } catch (error) {
        console.error('Error printing clearance:', error);
        alert('Error preparing clearance for printing. Please try again.');
    }
}

// Initialize when page loads
document.addEventListener('DOMContentLoaded', function() {
    loadStudentRequirements();
});