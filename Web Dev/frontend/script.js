document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('websiteForm');
    const preview = document.getElementById('preview');
    const previewContent = document.getElementById('previewContent');
    const downloadPdf = document.getElementById('downloadPdf');
    const publishWebsite = document.getElementById('publishWebsite');

    const API_BASE_URL = 'https://3clickbuilder.com';

    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const formData = {
            businessName: document.getElementById('businessName').value,
            serviceType: document.getElementById('serviceType').value,
            location: document.getElementById('location').value
        };

        try {
            const response = await fetch(`${API_BASE_URL}/api/create-website`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(formData)
            });

            if (!response.ok) {
                throw new Error('Failed to create website');
            }

            const data = await response.json();
            previewContent.innerHTML = data.html;
            preview.style.display = 'block';
        } catch (error) {
            console.error('Error:', error);
            alert('Failed to create website. Please try again.');
        }
    });

    downloadPdf.addEventListener('click', async () => {
        const formData = {
            businessName: document.getElementById('businessName').value,
            serviceType: document.getElementById('serviceType').value,
            location: document.getElementById('location').value
        };

        try {
            const response = await fetch(`${API_BASE_URL}/download-pdf`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(formData)
            });

            if (!response.ok) {
                throw new Error('Failed to generate PDF');
            }

            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `${formData.businessName}-summary.pdf`;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);
        } catch (error) {
            console.error('Error:', error);
            alert('Failed to generate PDF. Please try again.');
        }
    });

    publishWebsite.addEventListener('click', async () => {
        const formData = {
            businessName: document.getElementById('businessName').value,
            serviceType: document.getElementById('serviceType').value,
            location: document.getElementById('location').value
        };

        try {
            const response = await fetch(`${API_BASE_URL}/publish`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(formData)
            });

            if (!response.ok) {
                throw new Error('Failed to publish website');
            }

            const data = await response.json();
            alert(`Website published successfully! Visit: ${data.url}`);
        } catch (error) {
            console.error('Error:', error);
            alert('Failed to publish website. Please try again.');
        }
    });
}); 