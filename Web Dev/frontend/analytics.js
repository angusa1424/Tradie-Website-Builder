class Analytics {
    constructor() {
        this.events = [];
        this.errors = [];
        this.performance = {};
        this.userBehavior = {};
        this.init();
    }

    init() {
        this.setupErrorTracking();
        this.setupPerformanceMonitoring();
        this.setupUserBehaviorTracking();
        this.setupEventTracking();
    }

    setupErrorTracking() {
        window.onerror = (message, source, lineno, colno, error) => {
            this.trackError({
                type: 'runtime',
                message,
                source,
                lineno,
                colno,
                stack: error?.stack,
                timestamp: new Date().toISOString()
            });
        };

        window.addEventListener('unhandledrejection', (event) => {
            this.trackError({
                type: 'promise',
                message: event.reason?.message || 'Unhandled Promise Rejection',
                stack: event.reason?.stack,
                timestamp: new Date().toISOString()
            });
        });
    }

    setupPerformanceMonitoring() {
        if (window.performance && window.performance.timing) {
            window.addEventListener('load', () => {
                const timing = window.performance.timing;
                this.performance = {
                    pageLoad: timing.loadEventEnd - timing.navigationStart,
                    domContentLoaded: timing.domContentLoadedEventEnd - timing.navigationStart,
                    firstPaint: timing.responseEnd - timing.navigationStart,
                    dnsLookup: timing.domainLookupEnd - timing.domainLookupStart,
                    tcpConnection: timing.connectEnd - timing.connectStart,
                    serverResponse: timing.responseEnd - timing.requestStart,
                    domProcessing: timing.domComplete - timing.domLoading,
                    resourceLoading: timing.loadEventEnd - timing.domContentLoadedEventEnd
                };
                this.sendPerformanceData();
            });
        }
    }

    setupUserBehaviorTracking() {
        // Track page views
        this.trackPageView();

        // Track clicks
        document.addEventListener('click', (e) => {
            const target = e.target;
            this.trackUserAction('click', {
                element: target.tagName.toLowerCase(),
                id: target.id,
                class: target.className,
                text: target.textContent?.trim(),
                path: this.getElementPath(target)
            });
        });

        // Track form interactions
        document.addEventListener('submit', (e) => {
            const form = e.target;
            this.trackUserAction('form_submit', {
                formId: form.id,
                formAction: form.action,
                formMethod: form.method
            });
        });

        // Track scroll depth
        let maxScroll = 0;
        window.addEventListener('scroll', () => {
            const scrollPercent = (window.scrollY + window.innerHeight) / document.documentElement.scrollHeight * 100;
            if (scrollPercent > maxScroll) {
                maxScroll = scrollPercent;
                this.trackUserAction('scroll', { depth: Math.round(maxScroll) });
            }
        });

        // Track time on page
        let startTime = Date.now();
        window.addEventListener('beforeunload', () => {
            const timeSpent = Date.now() - startTime;
            this.trackUserAction('time_spent', { seconds: Math.round(timeSpent / 1000) });
        });
    }

    setupEventTracking() {
        // Track custom events
        window.trackEvent = (category, action, label, value) => {
            this.trackUserAction('custom_event', {
                category,
                action,
                label,
                value
            });
        };
    }

    trackError(error) {
        this.errors.push(error);
        this.sendErrorData(error);
    }

    trackUserAction(type, data) {
        const action = {
            type,
            data,
            timestamp: new Date().toISOString(),
            url: window.location.href,
            userAgent: navigator.userAgent
        };
        this.userBehavior[type] = this.userBehavior[type] || [];
        this.userBehavior[type].push(action);
        this.sendUserBehaviorData(action);
    }

    trackPageView() {
        this.trackUserAction('page_view', {
            path: window.location.pathname,
            referrer: document.referrer,
            title: document.title
        });
    }

    getElementPath(element) {
        const path = [];
        while (element && element.nodeType === Node.ELEMENT_NODE) {
            let selector = element.nodeName.toLowerCase();
            if (element.id) {
                selector += `#${element.id}`;
                path.unshift(selector);
                break;
            } else {
                let sibling = element;
                let nth = 1;
                while (sibling = sibling.previousElementSibling) {
                    if (sibling.nodeName.toLowerCase() === selector) nth++;
                }
                if (nth !== 1) selector += `:nth-of-type(${nth})`;
            }
            path.unshift(selector);
            element = element.parentNode;
        }
        return path.join(' > ');
    }

    async sendErrorData(error) {
        try {
            await fetch('/api/analytics/error', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(error)
            });
        } catch (e) {
            console.error('Failed to send error data:', e);
        }
    }

    async sendPerformanceData() {
        try {
            await fetch('/api/analytics/performance', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(this.performance)
            });
        } catch (e) {
            console.error('Failed to send performance data:', e);
        }
    }

    async sendUserBehaviorData(action) {
        try {
            await fetch('/api/analytics/behavior', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(action)
            });
        } catch (e) {
            console.error('Failed to send user behavior data:', e);
        }
    }
}

// Initialize analytics when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new Analytics();
}); 