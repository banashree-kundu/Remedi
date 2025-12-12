document.addEventListener('DOMContentLoaded', () => {
    
    // --- Elements ---
    const viewMode = document.getElementById('view-mode');
    const editMode = document.getElementById('edit-mode');
    const uploadSection = document.getElementById('upload-section');
    
    const btnEnableEdit = document.getElementById('btn-enable-edit');
    const btnCancel = document.getElementById('btn-cancel');
    
    // Image Upload Elements
    const btnTriggerUpload = document.getElementById('btn-trigger-upload');
    const realFileInput = document.getElementById('real-file-input');
    const profileCircle = document.getElementById('profile-circle');

    // --- 1. TOGGLE LOGIC ---

    // Click "Edit Profile" -> Hide View, Show Form
    btnEnableEdit.addEventListener('click', () => {
        viewMode.style.display = 'none';      // Hide text details
        editMode.style.display = 'block';     // Show inputs
        uploadSection.style.display = 'flex'; // Show upload button
    });

    // Click "Cancel" -> Revert changes (or just hide form)
    btnCancel.addEventListener('click', () => {
        viewMode.style.display = 'block';     // Show text details
        editMode.style.display = 'none';      // Hide inputs
        uploadSection.style.display = 'none'; // Hide upload button
    });


    // --- 2. IMAGE PREVIEW LOGIC ---

    // Click Blue Upload Button -> Click Hidden Input
    btnTriggerUpload.addEventListener('click', () => {
        realFileInput.click();
    });

    // File Selected -> Update Circle Background
    realFileInput.addEventListener('change', (e) => {
        const file = e.target.files[0];
        if (file) {
            const tempUrl = URL.createObjectURL(file);
            profileCircle.style.backgroundImage = `url('${tempUrl}')`;
            
        }
    });

    
});