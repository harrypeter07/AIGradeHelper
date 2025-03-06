document.addEventListener('DOMContentLoaded', function() {
    // File upload UI enhancement
    const uploadBoxes = document.querySelectorAll('.upload-box');
    
    uploadBoxes.forEach(box => {
        const input = box.querySelector('input[type="file"]');
        
        // Drag and drop handling
        box.addEventListener('dragover', (e) => {
            e.preventDefault();
            box.classList.add('drag-over');
        });
        
        box.addEventListener('dragleave', () => {
            box.classList.remove('drag-over');
        });
        
        box.addEventListener('drop', (e) => {
            e.preventDefault();
            box.classList.remove('drag-over');
            
            const files = e.dataTransfer.files;
            if (files.length) {
                input.files = files;
                updateFileName(box, files[0].name);
            }
        });
        
        // File input change handling
        input.addEventListener('change', (e) => {
            if (e.target.files.length) {
                updateFileName(box, e.target.files[0].name);
            }
        });
    });
    
    function updateFileName(box, fileName) {
        const textElement = box.querySelector('.upload-text');
        textElement.textContent = fileName;
    }
    
    // Form submission handling
    const form = document.querySelector('form');
    if (form) {
        form.addEventListener('submit', (e) => {
            const submitButton = form.querySelector('button[type="submit"]');
            submitButton.disabled = true;
            submitButton.innerHTML = `
                <span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>
                Grading...
            `;
        });
    }
    
    // Score animation on results page
    const scoreCircle = document.querySelector('.score-circle');
    if (scoreCircle) {
        const score = parseInt(scoreCircle.dataset.score);
        const scoreNumber = scoreCircle.querySelector('.score-number');
        
        let currentScore = 0;
        const duration = 1000;
        const steps = 60;
        const increment = score / steps;
        
        const timer = setInterval(() => {
            currentScore += increment;
            if (currentScore >= score) {
                currentScore = score;
                clearInterval(timer);
            }
            scoreNumber.textContent = Math.round(currentScore);
        }, duration / steps);
    }
});
