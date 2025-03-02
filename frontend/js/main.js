document.addEventListener('DOMContentLoaded', () => {
    const canvas = document.getElementById('renderCanvas');
    const renderer = new Renderer(canvas);
    const imagePreview = document.getElementById('imagePreview');
    const processButton = document.getElementById('processButton');
    const loadingOverlay = document.querySelector('.loading-overlay');
    
    // Update with your actual backend URL
    const BACKEND_URL = 'https://signage-3d-backend.onrender.com';
    
    // Handle file input change for preview
    document.getElementById('imageUpload').addEventListener('change', (event) => {
        const file = event.target.files[0];
        if (file) {
            const reader = new FileReader();
            reader.onload = (e) => {
                imagePreview.src = e.target.result;
                imagePreview.style.display = 'block';
            };
            reader.readAsDataURL(file);
        }
    });
    
    document.getElementById('processButton').addEventListener('click', async () => {
        const fileInput = document.getElementById('imageUpload');
        const materialType = document.getElementById('materialType').value;
        const file = fileInput.files[0];
        
        if (!file) {
            alert('Please select an image first');
            return;
        }
        
        // Show loading state
        processButton.disabled = true;
        processButton.textContent = 'Processing...';
        loadingOverlay.style.display = 'flex';
        
        const formData = new FormData();
        formData.append('file', file);
        
        try {
            console.log('Sending request to server...');
            const response = await fetch(`${BACKEND_URL}/process-image`, {
                method: 'POST',
                body: formData
            });
            
            console.log('Response status:', response.status);
            
            if (!response.ok) {
                const errorText = await response.text();
                console.error('Server response:', errorText);
                throw new Error(`Server error: ${errorText}`);
            }
            
            console.log('Getting blob from response...');
            const blob = await response.blob();
            console.log('Blob size:', blob.size);
            
            const url = URL.createObjectURL(blob);
            console.log('Created URL:', url);
            
            await renderer.loadModel(url, materialType);
            console.log('Model loaded successfully');
            
        } catch (error) {
            console.error('Detailed error:', error);
            if (error.message.includes('Failed to fetch')) {
                alert('Cannot connect to server. Please make sure the backend server is running at ' + BACKEND_URL);
            } else {
                alert('Error processing image: ' + error.message);
            }
        } finally {
            // Reset states
            processButton.disabled = false;
            processButton.textContent = 'Generate 3D Mockup';
            loadingOverlay.style.display = 'none';
        }
    });
}); 