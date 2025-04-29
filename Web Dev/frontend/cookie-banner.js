class CookieBanner {
    constructor() {
        this.banner = null;
        this.preferences = {
            essential: true,
            analytics: false,
            marketing: false
        };
        this.init();
    }

    init() {
        if (!this.getCookieConsent()) {
            this.createBanner();
        }
    }

    createBanner() {
        this.banner = document.createElement('div');
        this.banner.className = 'cookie-banner';
        this.banner.innerHTML = `
            <div class="cookie-content">
                <h3>We use cookies to enhance your experience</h3>
                <p>We use cookies to help us understand how you use our website and to improve your experience. You can customize your preferences below.</p>
                <div class="cookie-preferences">
                    <div class="preference-item">
                        <label>
                            <input type="checkbox" checked disabled>
                            Essential Cookies (Required)
                        </label>
                    </div>
                    <div class="preference-item">
                        <label>
                            <input type="checkbox" id="analyticsCookies">
                            Analytics Cookies
                        </label>
                    </div>
                    <div class="preference-item">
                        <label>
                            <input type="checkbox" id="marketingCookies">
                            Marketing Cookies
                        </label>
                    </div>
                </div>
                <div class="cookie-buttons">
                    <button class="accept-all">Accept All</button>
                    <button class="save-preferences">Save Preferences</button>
                    <button class="reject-all">Reject All</button>
                </div>
            </div>
        `;

        document.body.appendChild(this.banner);
        this.attachEventListeners();
    }

    attachEventListeners() {
        const acceptAll = this.banner.querySelector('.accept-all');
        const savePreferences = this.banner.querySelector('.save-preferences');
        const rejectAll = this.banner.querySelector('.reject-all');
        const analyticsCheckbox = this.banner.querySelector('#analyticsCookies');
        const marketingCheckbox = this.banner.querySelector('#marketingCookies');

        acceptAll.addEventListener('click', () => {
            this.preferences.analytics = true;
            this.preferences.marketing = true;
            this.saveCookieConsent();
            this.hideBanner();
        });

        savePreferences.addEventListener('click', () => {
            this.preferences.analytics = analyticsCheckbox.checked;
            this.preferences.marketing = marketingCheckbox.checked;
            this.saveCookieConsent();
            this.hideBanner();
        });

        rejectAll.addEventListener('click', () => {
            this.preferences.analytics = false;
            this.preferences.marketing = false;
            this.saveCookieConsent();
            this.hideBanner();
        });
    }

    saveCookieConsent() {
        const consent = {
            preferences: this.preferences,
            timestamp: new Date().toISOString()
        };
        localStorage.setItem('cookieConsent', JSON.stringify(consent));
        this.updateCookieSettings();
    }

    getCookieConsent() {
        const consent = localStorage.getItem('cookieConsent');
        if (consent) {
            this.preferences = JSON.parse(consent).preferences;
            this.updateCookieSettings();
            return true;
        }
        return false;
    }

    updateCookieSettings() {
        // Update Google Analytics based on preferences
        if (this.preferences.analytics) {
            this.enableGoogleAnalytics();
        } else {
            this.disableGoogleAnalytics();
        }

        // Update marketing cookies based on preferences
        if (this.preferences.marketing) {
            this.enableMarketingCookies();
        } else {
            this.disableMarketingCookies();
        }
    }

    enableGoogleAnalytics() {
        // Add Google Analytics tracking code
        const script = document.createElement('script');
        script.async = true;
        script.src = 'https://www.googletagmanager.com/gtag/js?id=YOUR-GA-ID';
        document.head.appendChild(script);

        window.dataLayer = window.dataLayer || [];
        function gtag(){dataLayer.push(arguments);}
        gtag('js', new Date());
        gtag('config', 'YOUR-GA-ID');
    }

    disableGoogleAnalytics() {
        // Remove Google Analytics tracking
        const scripts = document.querySelectorAll('script[src*="googletagmanager.com"]');
        scripts.forEach(script => script.remove());
    }

    enableMarketingCookies() {
        // Add marketing tracking scripts
        // Example: Facebook Pixel, etc.
    }

    disableMarketingCookies() {
        // Remove marketing tracking scripts
    }

    hideBanner() {
        this.banner.style.display = 'none';
    }
}

// Initialize cookie banner when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new CookieBanner();
}); 