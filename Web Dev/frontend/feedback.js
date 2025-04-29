class FeedbackSystem {
    constructor() {
        this.feedbackButton = null;
        this.feedbackForm = null;
        this.init();
    }

    init() {
        this.createFeedbackButton();
        this.createFeedbackForm();
    }

    createFeedbackButton() {
        this.feedbackButton = document.createElement('button');
        this.feedbackButton.className = 'feedback-button';
        this.feedbackButton.innerHTML = `
            <i class="fas fa-comment"></i>
            <span>Feedback</span>
        `;
        this.feedbackButton.addEventListener('click', () => this.toggleFeedbackForm());
        document.body.appendChild(this.feedbackButton);
    }

    createFeedbackForm() {
        this.feedbackForm = document.createElement('div');
        this.feedbackForm.className = 'feedback-form hidden';
        this.feedbackForm.innerHTML = `
            <div class="feedback-content">
                <div class="feedback-header">
                    <h3>Share Your Feedback</h3>
                    <button class="close-button">&times;</button>
                </div>
                <form id="feedbackForm">
                    <div class="form-group">
                        <label for="feedbackType">What type of feedback do you have?</label>
                        <select id="feedbackType" required>
                            <option value="">Select type</option>
                            <option value="bug">Bug Report</option>
                            <option value="feature">Feature Request</option>
                            <option value="improvement">Improvement Suggestion</option>
                            <option value="other">Other</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label for="feedbackMessage">Your Feedback</label>
                        <textarea id="feedbackMessage" rows="4" required placeholder="Please describe your feedback in detail..."></textarea>
                    </div>
                    <div class="form-group">
                        <label for="feedbackEmail">Your Email (optional)</label>
                        <input type="email" id="feedbackEmail" placeholder="Enter your email if you'd like us to follow up">
                    </div>
                    <div class="form-group">
                        <label>How would you rate your experience?</label>
                        <div class="rating">
                            <input type="radio" id="star5" name="rating" value="5">
                            <label for="star5">★</label>
                            <input type="radio" id="star4" name="rating" value="4">
                            <label for="star4">★</label>
                            <input type="radio" id="star3" name="rating" value="3">
                            <label for="star3">★</label>
                            <input type="radio" id="star2" name="rating" value="2">
                            <label for="star2">★</label>
                            <input type="radio" id="star1" name="rating" value="1">
                            <label for="star1">★</label>
                        </div>
                    </div>
                    <button type="submit" class="submit-button">Submit Feedback</button>
                </form>
            </div>
        `;

        document.body.appendChild(this.feedbackForm);
        this.attachFormEventListeners();
    }

    attachFormEventListeners() {
        const form = this.feedbackForm.querySelector('#feedbackForm');
        const closeButton = this.feedbackForm.querySelector('.close-button');

        form.addEventListener('submit', (e) => {
            e.preventDefault();
            this.submitFeedback(form);
        });

        closeButton.addEventListener('click', () => {
            this.toggleFeedbackForm();
        });

        // Close form when clicking outside
        document.addEventListener('click', (e) => {
            if (e.target === this.feedbackForm) {
                this.toggleFeedbackForm();
            }
        });
    }

    toggleFeedbackForm() {
        this.feedbackForm.classList.toggle('hidden');
        this.feedbackButton.classList.toggle('hidden');
    }

    async submitFeedback(form) {
        const formData = {
            type: form.querySelector('#feedbackType').value,
            message: form.querySelector('#feedbackMessage').value,
            email: form.querySelector('#feedbackEmail').value,
            rating: form.querySelector('input[name="rating"]:checked')?.value || 0,
            timestamp: new Date().toISOString(),
            userAgent: navigator.userAgent,
            url: window.location.href
        };

        try {
            const response = await fetch('/api/feedback', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(formData)
            });

            if (response.ok) {
                this.showThankYouMessage();
                form.reset();
            } else {
                throw new Error('Failed to submit feedback');
            }
        } catch (error) {
            console.error('Error submitting feedback:', error);
            this.showErrorMessage();
        }
    }

    showThankYouMessage() {
        const message = document.createElement('div');
        message.className = 'feedback-message success';
        message.textContent = 'Thank you for your feedback!';
        this.feedbackForm.querySelector('.feedback-content').appendChild(message);
        setTimeout(() => {
            message.remove();
            this.toggleFeedbackForm();
        }, 3000);
    }

    showErrorMessage() {
        const message = document.createElement('div');
        message.className = 'feedback-message error';
        message.textContent = 'Sorry, there was an error submitting your feedback. Please try again.';
        this.feedbackForm.querySelector('.feedback-content').appendChild(message);
        setTimeout(() => message.remove(), 3000);
    }
}

// Initialize feedback system when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new FeedbackSystem();
}); 