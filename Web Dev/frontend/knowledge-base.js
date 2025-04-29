class KnowledgeBase {
    constructor() {
        this.articles = [
            {
                id: 1,
                title: "Getting Started with 3-Click Website Builder",
                category: "Getting Started",
                content: `
                    <h2>Welcome to 3-Click Website Builder!</h2>
                    <p>Creating your website is as easy as 1-2-3:</p>
                    <ol>
                        <li>Enter your business name</li>
                        <li>Select your service type</li>
                        <li>Choose your location</li>
                    </ol>
                    <p>That's it! Your website will be generated instantly.</p>
                `,
                tags: ["beginner", "setup", "tutorial"]
            },
            {
                id: 2,
                title: "Customizing Your Website",
                category: "Customization",
                content: `
                    <h2>Customizing Your Website</h2>
                    <p>After creating your website, you can customize it in several ways:</p>
                    <ul>
                        <li>Change the color scheme</li>
                        <li>Add your logo</li>
                        <li>Customize the layout</li>
                        <li>Add additional pages</li>
                    </ul>
                `,
                tags: ["customization", "design", "layout"]
            },
            {
                id: 3,
                title: "Publishing Your Website",
                category: "Publishing",
                content: `
                    <h2>Publishing Your Website</h2>
                    <p>To publish your website:</p>
                    <ol>
                        <li>Click the "Publish" button</li>
                        <li>Choose your domain name</li>
                        <li>Select your hosting plan</li>
                        <li>Complete the payment process</li>
                    </ol>
                `,
                tags: ["publishing", "domain", "hosting"]
            }
        ];
        
        this.init();
    }

    init() {
        this.createKnowledgeBase();
        this.attachEventListeners();
    }

    createKnowledgeBase() {
        const container = document.createElement('div');
        container.className = 'knowledge-base';
        container.innerHTML = `
            <div class="knowledge-base-header">
                <h2>Knowledge Base</h2>
                <div class="search-container">
                    <input type="text" placeholder="Search articles..." class="search-input">
                    <button class="search-button">
                        <i class="fas fa-search"></i>
                    </button>
                </div>
            </div>
            <div class="knowledge-base-content">
                <div class="categories">
                    <h3>Categories</h3>
                    <ul class="category-list">
                        <li data-category="all" class="active">All Articles</li>
                        <li data-category="Getting Started">Getting Started</li>
                        <li data-category="Customization">Customization</li>
                        <li data-category="Publishing">Publishing</li>
                    </ul>
                </div>
                <div class="articles-container">
                    <div class="articles-list"></div>
                    <div class="article-content"></div>
                </div>
            </div>
        `;

        document.body.appendChild(container);
        this.renderArticles('all');
    }

    attachEventListeners() {
        const searchInput = document.querySelector('.search-input');
        const searchButton = document.querySelector('.search-button');
        const categoryList = document.querySelector('.category-list');

        searchInput.addEventListener('input', (e) => {
            this.searchArticles(e.target.value);
        });

        searchButton.addEventListener('click', () => {
            this.searchArticles(searchInput.value);
        });

        categoryList.addEventListener('click', (e) => {
            if (e.target.tagName === 'LI') {
                const category = e.target.dataset.category;
                this.filterByCategory(category);
                
                // Update active state
                categoryList.querySelectorAll('li').forEach(li => {
                    li.classList.remove('active');
                });
                e.target.classList.add('active');
            }
        });
    }

    renderArticles(category) {
        const articlesList = document.querySelector('.articles-list');
        const filteredArticles = category === 'all' 
            ? this.articles 
            : this.articles.filter(article => article.category === category);

        articlesList.innerHTML = filteredArticles.map(article => `
            <div class="article-item" data-id="${article.id}">
                <h4>${article.title}</h4>
                <div class="article-meta">
                    <span class="category">${article.category}</span>
                    <div class="tags">
                        ${article.tags.map(tag => `<span class="tag">${tag}</span>`).join('')}
                    </div>
                </div>
            </div>
        `).join('');

        // Add click event to articles
        articlesList.querySelectorAll('.article-item').forEach(item => {
            item.addEventListener('click', () => {
                const articleId = parseInt(item.dataset.id);
                this.showArticle(articleId);
            });
        });
    }

    showArticle(articleId) {
        const article = this.articles.find(a => a.id === articleId);
        const articleContent = document.querySelector('.article-content');
        
        if (article) {
            articleContent.innerHTML = `
                <div class="article-header">
                    <h2>${article.title}</h2>
                    <div class="article-meta">
                        <span class="category">${article.category}</span>
                        <div class="tags">
                            ${article.tags.map(tag => `<span class="tag">${tag}</span>`).join('')}
                        </div>
                    </div>
                </div>
                <div class="article-body">
                    ${article.content}
                </div>
            `;
        }
    }

    searchArticles(query) {
        if (!query) {
            this.renderArticles('all');
            return;
        }

        const searchResults = this.articles.filter(article => {
            const searchText = `${article.title} ${article.category} ${article.tags.join(' ')} ${article.content}`.toLowerCase();
            return searchText.includes(query.toLowerCase());
        });

        const articlesList = document.querySelector('.articles-list');
        articlesList.innerHTML = searchResults.map(article => `
            <div class="article-item" data-id="${article.id}">
                <h4>${article.title}</h4>
                <div class="article-meta">
                    <span class="category">${article.category}</span>
                    <div class="tags">
                        ${article.tags.map(tag => `<span class="tag">${tag}</span>`).join('')}
                    </div>
                </div>
            </div>
        `).join('');

        // Add click event to articles
        articlesList.querySelectorAll('.article-item').forEach(item => {
            item.addEventListener('click', () => {
                const articleId = parseInt(item.dataset.id);
                this.showArticle(articleId);
            });
        });
    }

    filterByCategory(category) {
        this.renderArticles(category);
    }
}

// Initialize knowledge base when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new KnowledgeBase();
}); 