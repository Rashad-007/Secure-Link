// SecureLink client-side interactivity
document.addEventListener('DOMContentLoaded', () => {
    // Auto-dismiss alerts after 6 seconds
    const alerts = document.querySelectorAll('.alert-dismissible');
    alerts.forEach(alert => {
        setTimeout(() => {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 6000);
    });

    // File input preview
    const fileInput = document.getElementById('file-upload-input');
    const fileLabel = document.getElementById('file-selected-name');
    if (fileInput && fileLabel) {
        fileInput.addEventListener('change', (e) => {
            if (e.target.files.length > 0) {
                const f = e.target.files[0];
                const sizeKb = (f.size / 1024).toFixed(1);
                fileLabel.innerHTML = `<span class="text-cyan">Selected:</span> <strong>${f.name}</strong> (${sizeKb} KB)`;
            }
        });
    }
});

// Copy to clipboard helper
function copyToClipboard(elementId, btnElement) {
    const textElement = document.getElementById(elementId);
    if (!textElement) return;
    
    const textToCopy = textElement.innerText || textElement.value;
    navigator.clipboard.writeText(textToCopy).then(() => {
        const originalHtml = btnElement.innerHTML;
        btnElement.innerHTML = '<span class="text-success">Copied!</span>';
        setTimeout(() => {
            btnElement.innerHTML = originalHtml;
        }, 2000);
    }).catch(err => {
        console.error('Failed to copy: ', err);
    });
}

