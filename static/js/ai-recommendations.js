// AI-powered Content Recommendation System
class AIRecommendationEngine {
    constructor() {
        this.recommendations = [];
        this.currentProject = null;
        this.init();
    }

    init() {
        this.loadCurrentProject();
        this.generateRecommendations();
        this.displayRecommendations();
    }

    loadCurrentProject() {
        // Get project data from the page
        const projectElement = document.querySelector('[data-project-id]');
        if (projectElement) {
            this.currentProject = {
                id: projectElement.dataset.projectId,
                title: document.querySelector('.project-title')?.textContent || '',
                description: document.querySelector('.project-description')?.textContent || '',
                tags: Array.from(document.querySelectorAll('.project-tag')).map(tag => tag.textContent.trim()),
                category: document.querySelector('.project-category')?.textContent || ''
            };
        }
    }

    async generateRecommendations() {
        if (!this.currentProject) return;

        try {
            const response = await fetch('/api/recommendations', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-Requested-With': 'XMLHttpRequest'
                },
                body: JSON.stringify({
                    projectId: this.currentProject.id,
                    tags: this.currentProject.tags,
                    category: this.currentProject.category,
                    description: this.currentProject.description
                })
            });

            if (response.ok) {
                const data = await response.json();
                this.recommendations = data.recommendations || [];
            } else {
                // Fallback to client-side recommendations
                this.generateFallbackRecommendations();
            }
        } catch (error) {
            console.log('Using fallback recommendations');
            this.generateFallbackRecommendations();
        }
    }

    generateFallbackRecommendations() {
        // Simple similarity-based recommendations
        const allProjects = window.portfolioData?.projects || [];
        const similarities = [];

        allProjects.forEach(project => {
            if (project.id === parseInt(this.currentProject.id)) return;

            let score = 0;
            
            // Tag similarity
            const commonTags = project.tags?.filter(tag => 
                this.currentProject.tags.includes(tag)
            ).length || 0;
            score += commonTags * 3;

            // Category similarity
            if (project.category === this.currentProject.category) {
                score += 5;
            }

            // Title/description similarity (basic keyword matching)
            const projectWords = (project.title + ' ' + project.description).toLowerCase().split(/\s+/);
            const currentWords = (this.currentProject.title + ' ' + this.currentProject.description).toLowerCase().split(/\s+/);
            
            const commonWords = projectWords.filter(word => 
                word.length > 3 && currentWords.includes(word)
            ).length;
            score += commonWords;

            if (score > 0) {
                similarities.push({ project, score });
            }
        });

        // Sort by similarity and take top 3
        similarities.sort((a, b) => b.score - a.score);
        this.recommendations = similarities.slice(0, 3).map(item => item.project);
    }

    displayRecommendations() {
        if (this.recommendations.length === 0) return;

        const container = this.createRecommendationsContainer();
        const projectDetail = document.querySelector('.project-detail, .container');
        
        if (projectDetail && container) {
            projectDetail.appendChild(container);
            this.animateRecommendations();
        }
    }

    createRecommendationsContainer() {
        const section = document.createElement('section');
        section.className = 'recommendations-section py-5 mt-5 border-top';
        section.innerHTML = `
            <div class="container">
                <div class="row">
                    <div class="col-12">
                        <h3 class="h4 fw-bold mb-4">
                            <i class="fas fa-robot me-2 text-primary"></i>
                            <span data-i18n="recommendations_title">Projetos Relacionados</span>
                        </h3>
                        <p class="text-muted mb-4" data-i18n="recommendations_subtitle">
                            Recomendados com base em IA, considerando tags, categoria e conteúdo similar
                        </p>
                    </div>
                </div>
                <div class="row g-4">
                    ${this.recommendations.map((project, index) => this.createRecommendationCard(project, index)).join('')}
                </div>
            </div>
        `;
        return section;
    }

    createRecommendationCard(project, index) {
        return `
            <div class="col-md-4 recommendation-card" style="animation-delay: ${index * 0.1}s">
                <div class="card h-100 border-0 shadow-sm recommendation-item">
                    ${project.image_filename ? `
                        <div class="position-relative overflow-hidden rounded-top">
                            <img src="/static/uploads/${project.image_filename}" 
                                 class="card-img-top" alt="${project.title}" 
                                 style="height: 200px; object-fit: cover;">
                            <div class="recommendation-overlay">
                                <span class="badge bg-primary">
                                    <i class="fas fa-magic me-1"></i>IA
                                </span>
                            </div>
                        </div>
                    ` : ''}
                    <div class="card-body d-flex flex-column">
                        <h5 class="card-title fw-semibold">${project.title}</h5>
                        <p class="card-text text-muted flex-grow-1">${this.truncateText(project.description, 100)}</p>
                        
                        ${project.tags && project.tags.length ? `
                            <div class="mb-3">
                                ${project.tags.slice(0, 3).map(tag => 
                                    `<span class="badge bg-light text-dark me-1">${tag}</span>`
                                ).join('')}
                            </div>
                        ` : ''}
                        
                        <div class="d-flex justify-content-between align-items-center mt-auto">
                            <a href="/project/${project.id}" class="btn btn-outline-primary btn-sm">
                                <i class="fas fa-eye me-1"></i>
                                <span data-i18n="btn_view_project">Ver Projeto</span>
                            </a>
                            <small class="text-muted">
                                <i class="fas fa-heart me-1"></i>${project.likes_count || 0}
                            </small>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }

    truncateText(text, maxLength) {
        if (!text) return '';
        return text.length > maxLength ? text.substring(0, maxLength) + '...' : text;
    }

    animateRecommendations() {
        const cards = document.querySelectorAll('.recommendation-card');
        cards.forEach((card, index) => {
            card.classList.add('fade-in-up');
        });
    }
}

// Initialize AI recommendations when on project detail page
document.addEventListener('DOMContentLoaded', function() {
    if (document.querySelector('.project-detail, [data-project-id]')) {
        setTimeout(() => {
            new AIRecommendationEngine();
        }, 1000);
    }
});