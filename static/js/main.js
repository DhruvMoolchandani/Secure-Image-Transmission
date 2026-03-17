document.addEventListener('DOMContentLoaded', () => {
    // --- UI Elements ---
    const hostDrop = document.getElementById('host-drop');
    const wmDrop = document.getElementById('wm-drop');
    const hostInput = document.getElementById('host_image');
    const wmInput = document.getElementById('watermark_image');
    const hostPreview = document.getElementById('host-preview');
    const wmPreview = document.getElementById('wm-preview');
    
    const alphaInput = document.getElementById('alpha');
    const alphaVal = document.getElementById('alpha-val');
    
    const form = document.getElementById('pipeline-form');
    const submitBtn = document.getElementById('submit-btn');
    const btnText = submitBtn.querySelector('.btn-text');
    const loader = submitBtn.querySelector('.loader');
    
    const resultsSection = document.getElementById('results-section');
    
    // --- File Input & Drag and Drop Handling ---
    function setupFileInput(dropZone, inputElement, previewElement) {
        // Click to open file dialog
        dropZone.addEventListener('click', () => inputElement.click());
        
        // Drag over effects
        dropZone.addEventListener('dragover', (e) => {
            e.preventDefault();
            dropZone.classList.add('drag-over');
        });
        
        dropZone.addEventListener('dragleave', () => {
            dropZone.classList.remove('drag-over');
        });
        
        dropZone.addEventListener('drop', (e) => {
            e.preventDefault();
            dropZone.classList.remove('drag-over');
            
            if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
                inputElement.files = e.dataTransfer.files;
                updatePreview(inputElement, previewElement);
            }
        });
        
        // Input change
        inputElement.addEventListener('change', () => {
            if (inputElement.files && inputElement.files.length > 0) {
                updatePreview(inputElement, previewElement);
            }
        });
    }
    
    function updatePreview(inputElement, previewElement) {
        const file = inputElement.files[0];
        if (file) {
            const reader = new FileReader();
            reader.onload = (e) => {
                previewElement.src = e.target.result;
                previewElement.classList.remove('hidden');
            };
            reader.readAsDataURL(file);
        }
    }
    
    setupFileInput(hostDrop, hostInput, hostPreview);
    setupFileInput(wmDrop, wmInput, wmPreview);
    
    // --- Slider Update ---
    alphaInput.addEventListener('input', (e) => {
        alphaVal.textContent = parseFloat(e.target.value).toFixed(1);
    });
    
    // --- Form Submission ---
    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        if (!hostInput.files.length || !wmInput.files.length) {
            alert('Please upload both host and watermark images.');
            return;
        }
        
        // UI Loading State
        btnText.classList.add('hidden');
        loader.classList.remove('hidden');
        submitBtn.disabled = true;
        
        const formData = new FormData();
        formData.append('host_image', hostInput.files[0]);
        formData.append('watermark_image', wmInput.files[0]);
        formData.append('alpha', alphaInput.value);
        
        try {
            const response = await fetch('/api/process', {
                method: 'POST',
                body: formData
            });
            
            const data = await response.json();
            
            if (response.ok && data.success) {
                // Update images (adding ?t= timestamp isn't necessary because API returns fresh paths)
                document.getElementById('res-watermarked').src = data.watermarked_url;
                document.getElementById('res-decrypted').src = data.decrypted_url;
                document.getElementById('res-extracted').src = data.extracted_url;
                
                // Show results
                resultsSection.classList.remove('hidden');
                
                // Scroll to results seamlessly
                setTimeout(() => {
                    resultsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
                }, 100);
            } else {
                alert(`Error: ${data.error || 'Failed to process pipeline.'}`);
            }
        } catch (error) {
            console.error('Submission error:', error);
            alert('A network error occurred while reaching the backend.');
        } finally {
            // Restore UI
            btnText.classList.remove('hidden');
            loader.classList.add('hidden');
            submitBtn.disabled = false;
        }
    });
});
