// Interactive Career Timeline
class CareerTimeline {
    constructor() {
        this.timelineData = [];
        this.autoPlayInterval = null;
        this.currentIndex = 0;
        this.isAutoPlaying = false;
        this.init();
    }

    init() {
        this.loadTimelineData();
        this.createTimeline();
        this.initializeControls();
        this.bindEvents();
    }

    async loadTimelineData() {
        try {
            const response = await fetch('/api/timeline');
            if (response.ok) {
                const data = await response.json();
                this.timelineData = data.timeline || [];
            }
        } catch (error) {
            console.log('Using sample timeline data');
            this.timelineData = this.getSampleData();
        }

        // Sort by date
        this.timelineData.sort((a, b) => new Date(a.date) - new Date(b.date));
    }

    getSampleData() {
        return [
            {
                id: 1,
                title: 'Primeiro Projeto Web',
                description: 'Desenvolvimento do primeiro website responsivo usando HTML, CSS e JavaScript',
                date: '2023-01-15',
                type: 'project',
                technologies: ['HTML', 'CSS', 'JavaScript'],
                image: null
            },
            {
                id: 2,
                title: 'Certificação Python',
                description: 'Concluído curso avançado de Python para desenvolvimento web',
                date: '2023-06-20',
                type: 'achievement',
                technologies: ['Python', 'Flask', 'Django'],
                image: null
            },
            {
                id: 3,
                title: 'Sistema de E-commerce',
                description: 'Desenvolvimento completo de plataforma de vendas online com painel administrativo',
                date: '2023-12-10',
                type: 'project',
                technologies: ['Python', 'Flask', 'SQLAlchemy', 'Bootstrap'],
                image: null
            }
        ];
    }

    createTimeline() {
        const timelineContainer = document.getElementById('career-timeline');
        if (!timelineContainer) return;

        timelineContainer.innerHTML = `
            <div class="timeline-header text-center mb-5">
                <h2 class="fw-bold mb-3">
                    <i class="fas fa-route me-2 text-primary"></i>
                    <span data-i18n="timeline_title">Linha do Tempo da Carreira</span>
                </h2>
                <p class="lead text-muted" data-i18n="timeline_subtitle">
                    Acompanhe a evolução dos meus projetos e conquistas
                </p>
                <div class="timeline-controls mt-4">
                    <button class="btn btn-outline-primary me-2" onclick="careerTimeline.toggleAutoPlay()">
                        <i class="fas fa-play me-1" id="autoplay-icon"></i>
                        <span id="autoplay-text" data-i18n="timeline_autoplay">Auto-Play</span>
                    </button>
                    <button class="btn btn-outline-secondary" onclick="careerTimeline.resetTimeline()">
                        <i class="fas fa-undo me-1"></i>
                        <span data-i18n="timeline_reset">Reiniciar</span>
                    </button>
                </div>
            </div>
            
            <div class="timeline-container">
                <div class="timeline-progress">
                    <div class="timeline-progress-bar" id="timeline-progress"></div>
                </div>
                <div class="timeline-items">
                    ${this.timelineData.map((item, index) => this.createTimelineItem(item, index)).join('')}
                </div>
            </div>
            
            <div class="timeline-detail-modal" id="timeline-modal" style="display: none;">
                <div class="timeline-modal-content">
                    <div class="timeline-modal-header">
                        <h4 id="modal-title"></h4>
                        <button class="btn-close" onclick="careerTimeline.closeModal()"></button>
                    </div>
                    <div class="timeline-modal-body">
                        <div id="modal-content"></div>
                    </div>
                </div>
            </div>
        `;
    }

    createTimelineItem(item, index) {
        const isLeft = index % 2 === 0;
        const typeIcon = item.type === 'project' ? 'fas fa-code' : 'fas fa-trophy';
        const typeColor = item.type === 'project' ? 'primary' : 'success';

        return `
            <div class="timeline-item ${isLeft ? 'timeline-left' : 'timeline-right'}" 
                 data-index="${index}" 
                 onclick="careerTimeline.showDetail(${index})">
                <div class="timeline-marker">
                    <div class="timeline-icon bg-${typeColor}">
                        <i class="${typeIcon}"></i>
                    </div>
                    <div class="timeline-date">${this.formatDate(item.date)}</div>
                </div>
                <div class="timeline-content">
                    <div class="timeline-card">
                        ${item.image ? `
                            <div class="timeline-image">
                                <img src="${item.image}" alt="${item.title}">
                            </div>
                        ` : ''}
                        <div class="timeline-card-body">
                            <h5 class="timeline-title">${item.title}</h5>
                            <p class="timeline-description">${this.truncateText(item.description, 100)}</p>
                            ${item.technologies ? `
                                <div class="timeline-technologies">
                                    ${item.technologies.slice(0, 3).map(tech => 
                                        `<span class="badge bg-light text-dark me-1">${tech}</span>`
                                    ).join('')}
                                </div>
                            ` : ''}
                        </div>
                    </div>
                </div>
            </div>
        `;
    }

    formatDate(dateString) {
        const date = new Date(dateString);
        return date.toLocaleDateString('pt-BR', { 
            month: 'short', 
            year: 'numeric' 
        });
    }

    truncateText(text, maxLength) {
        return text.length > maxLength ? text.substring(0, maxLength) + '...' : text;
    }

    initializeControls() {
        this.updateProgressBar(0);
    }

    bindEvents() {
        // Observer for scroll animations
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('timeline-animate');
                }
            });
        }, { threshold: 0.2 });

        document.querySelectorAll('.timeline-item').forEach(item => {
            observer.observe(item);
        });
    }

    showDetail(index) {
        const item = this.timelineData[index];
        if (!item) return;

        const modal = document.getElementById('timeline-modal');
        const title = document.getElementById('modal-title');
        const content = document.getElementById('modal-content');

        title.textContent = item.title;
        content.innerHTML = `
            <div class="row">
                <div class="col-md-6">
                    <p class="text-muted mb-2">
                        <i class="fas fa-calendar me-2"></i>${this.formatFullDate(item.date)}
                    </p>
                    <p class="text-muted mb-3">
                        <i class="fas fa-tag me-2"></i>${item.type === 'project' ? 'Projeto' : 'Conquista'}
                    </p>
                    <p>${item.description}</p>
                    
                    ${item.technologies ? `
                        <div class="mt-3">
                            <h6>Tecnologias Utilizadas:</h6>
                            <div class="d-flex flex-wrap gap-2">
                                ${item.technologies.map(tech => 
                                    `<span class="badge bg-primary">${tech}</span>`
                                ).join('')}
                            </div>
                        </div>
                    ` : ''}
                </div>
                ${item.image ? `
                    <div class="col-md-6">
                        <img src="${item.image}" alt="${item.title}" class="img-fluid rounded">
                    </div>
                ` : ''}
            </div>
        `;

        modal.style.display = 'flex';
        this.currentIndex = index;
    }

    closeModal() {
        const modal = document.getElementById('timeline-modal');
        modal.style.display = 'none';
    }

    toggleAutoPlay() {
        if (this.isAutoPlaying) {
            this.stopAutoPlay();
        } else {
            this.startAutoPlay();
        }
    }

    startAutoPlay() {
        this.isAutoPlaying = true;
        const icon = document.getElementById('autoplay-icon');
        const text = document.getElementById('autoplay-text');
        
        icon.className = 'fas fa-pause me-1';
        text.textContent = 'Pausar';

        this.autoPlayInterval = setInterval(() => {
            this.currentIndex = (this.currentIndex + 1) % this.timelineData.length;
            this.highlightTimelineItem(this.currentIndex);
            this.updateProgressBar(this.currentIndex);
        }, 3000);
    }

    stopAutoPlay() {
        this.isAutoPlaying = false;
        const icon = document.getElementById('autoplay-icon');
        const text = document.getElementById('autoplay-text');
        
        icon.className = 'fas fa-play me-1';
        text.textContent = 'Auto-Play';

        if (this.autoPlayInterval) {
            clearInterval(this.autoPlayInterval);
            this.autoPlayInterval = null;
        }

        this.clearHighlights();
    }

    resetTimeline() {
        this.stopAutoPlay();
        this.currentIndex = 0;
        this.updateProgressBar(0);
        this.clearHighlights();
        
        // Scroll to top of timeline
        const timeline = document.getElementById('career-timeline');
        if (timeline) {
            timeline.scrollIntoView({ behavior: 'smooth' });
        }
    }

    highlightTimelineItem(index) {
        this.clearHighlights();
        const item = document.querySelector(`[data-index="${index}"]`);
        if (item) {
            item.classList.add('timeline-highlight');
            item.scrollIntoView({ behavior: 'smooth', block: 'center' });
        }
    }

    clearHighlights() {
        document.querySelectorAll('.timeline-highlight').forEach(item => {
            item.classList.remove('timeline-highlight');
        });
    }

    updateProgressBar(index) {
        const progress = document.getElementById('timeline-progress');
        if (progress && this.timelineData.length > 0) {
            const percentage = (index / (this.timelineData.length - 1)) * 100;
            progress.style.height = percentage + '%';
        }
    }

    formatFullDate(dateString) {
        const date = new Date(dateString);
        return date.toLocaleDateString('pt-BR', { 
            day: 'numeric',
            month: 'long', 
            year: 'numeric' 
        });
    }
}

// Initialize career timeline
document.addEventListener('DOMContentLoaded', function() {
    if (document.getElementById('career-timeline')) {
        window.careerTimeline = new CareerTimeline();
    }
});