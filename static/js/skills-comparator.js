// Skills Comparator System
class SkillsComparator {
    constructor() {
        this.skills = [];
        this.selectedSkills = [];
        this.comparisonData = null;
        this.init();
    }

    init() {
        this.loadSkills();
        this.createComparatorInterface();
        this.bindEvents();
    }

    async loadSkills() {
        try {
            const response = await fetch('/api/skills');
            if (response.ok) {
                const data = await response.json();
                this.skills = data.skills || [];
            }
        } catch (error) {
            console.log('Using sample skills data');
            this.skills = this.getSampleSkills();
        }
    }

    getSampleSkills() {
        return [
            { id: 1, name: 'Python', level: 9, projects: 8, experience_years: 3 },
            { id: 2, name: 'JavaScript', level: 8, projects: 12, experience_years: 4 },
            { id: 3, name: 'Flask', level: 9, projects: 6, experience_years: 2 },
            { id: 4, name: 'React', level: 7, projects: 5, experience_years: 2 },
            { id: 5, name: 'SQL', level: 8, projects: 10, experience_years: 3 },
            { id: 6, name: 'HTML/CSS', level: 9, projects: 15, experience_years: 4 },
            { id: 7, name: 'Bootstrap', level: 8, projects: 12, experience_years: 3 },
            { id: 8, name: 'Git', level: 8, projects: 20, experience_years: 3 }
        ];
    }

    createComparatorInterface() {
        const container = document.getElementById('skills-comparator');
        if (!container) return;

        container.innerHTML = `
            <div class="skills-comparator-section">
                <div class="row">
                    <div class="col-12 text-center mb-5">
                        <h2 class="fw-bold mb-3">
                            <i class="fas fa-balance-scale me-2 text-primary"></i>
                            <span data-i18n="skills_comparator_title">Comparador de Habilidades</span>
                        </h2>
                        <p class="lead text-muted" data-i18n="skills_comparator_subtitle">
                            Compare duas habilidades do meu portfólio e veja projetos, métricas e resultados
                        </p>
                    </div>
                </div>

                <div class="row justify-content-center mb-5">
                    <div class="col-lg-8">
                        <div class="card border-0 shadow-sm">
                            <div class="card-body p-4">
                                <div class="row g-4">
                                    <div class="col-md-5">
                                        <label class="form-label fw-semibold">
                                            <i class="fas fa-search me-1"></i>Primeira Habilidade
                                        </label>
                                        <select class="form-select" id="skill1-select">
                                            <option value="">Selecione uma habilidade...</option>
                                            ${this.skills.map(skill => 
                                                `<option value="${skill.id}">${skill.name}</option>`
                                            ).join('')}
                                        </select>
                                    </div>
                                    
                                    <div class="col-md-2 text-center d-flex align-items-end justify-content-center">
                                        <div class="vs-badge">
                                            <span class="badge bg-primary fs-6 px-3 py-2">VS</span>
                                        </div>
                                    </div>
                                    
                                    <div class="col-md-5">
                                        <label class="form-label fw-semibold">
                                            <i class="fas fa-search me-1"></i>Segunda Habilidade
                                        </label>
                                        <select class="form-select" id="skill2-select">
                                            <option value="">Selecione uma habilidade...</option>
                                            ${this.skills.map(skill => 
                                                `<option value="${skill.id}">${skill.name}</option>`
                                            ).join('')}
                                        </select>
                                    </div>
                                </div>
                                
                                <div class="text-center mt-4">
                                    <button class="btn btn-primary btn-lg" onclick="skillsComparator.compareSkills()" disabled id="compare-btn">
                                        <i class="fas fa-chart-bar me-2"></i>Comparar Habilidades
                                    </button>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <div class="comparison-results" id="comparison-results" style="display: none;">
                    <!-- Results will be populated here -->
                </div>
            </div>
        `;
    }

    bindEvents() {
        const skill1Select = document.getElementById('skill1-select');
        const skill2Select = document.getElementById('skill2-select');
        const compareBtn = document.getElementById('compare-btn');

        [skill1Select, skill2Select].forEach(select => {
            select.addEventListener('change', () => {
                this.updateCompareButton();
                this.updateSkillOptions();
            });
        });
    }

    updateCompareButton() {
        const skill1 = document.getElementById('skill1-select').value;
        const skill2 = document.getElementById('skill2-select').value;
        const compareBtn = document.getElementById('compare-btn');
        
        compareBtn.disabled = !(skill1 && skill2 && skill1 !== skill2);
    }

    updateSkillOptions() {
        const skill1Value = document.getElementById('skill1-select').value;
        const skill2Value = document.getElementById('skill2-select').value;
        
        // Disable already selected options
        document.querySelectorAll('#skill1-select option, #skill2-select option').forEach(option => {
            option.disabled = false;
        });
        
        if (skill1Value) {
            const skill2Option = document.querySelector(`#skill2-select option[value="${skill1Value}"]`);
            if (skill2Option) skill2Option.disabled = true;
        }
        
        if (skill2Value) {
            const skill1Option = document.querySelector(`#skill1-select option[value="${skill2Value}"]`);
            if (skill1Option) skill1Option.disabled = true;
        }
    }

    async compareSkills() {
        const skill1Id = document.getElementById('skill1-select').value;
        const skill2Id = document.getElementById('skill2-select').value;
        
        if (!skill1Id || !skill2Id) return;

        const skill1 = this.skills.find(s => s.id == skill1Id);
        const skill2 = this.skills.find(s => s.id == skill2Id);

        if (!skill1 || !skill2) return;

        // Show loading state
        this.showLoadingState();

        try {
            // Get comparison data (with fallback to sample data)
            const comparisonData = await this.getComparisonData(skill1, skill2);
            this.displayComparison(skill1, skill2, comparisonData);
        } catch (error) {
            console.error('Comparison error:', error);
            this.showErrorState();
        }
    }

    async getComparisonData(skill1, skill2) {
        try {
            const response = await fetch('/api/skills/compare', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    skill1_id: skill1.id,
                    skill2_id: skill2.id
                })
            });

            if (response.ok) {
                return await response.json();
            }
        } catch (error) {
            console.log('Using fallback comparison data');
        }

        // Fallback comparison data
        return {
            skill1_projects: this.generateSampleProjects(skill1.name, skill1.projects),
            skill2_projects: this.generateSampleProjects(skill2.name, skill2.projects),
            metrics: {
                skill1: {
                    proficiency: skill1.level,
                    projects_count: skill1.projects,
                    experience_years: skill1.experience_years,
                    complexity_avg: Math.floor(Math.random() * 3) + 6
                },
                skill2: {
                    proficiency: skill2.level,
                    projects_count: skill2.projects,
                    experience_years: skill2.experience_years,
                    complexity_avg: Math.floor(Math.random() * 3) + 6
                }
            }
        };
    }

    generateSampleProjects(skillName, count) {
        const projectTypes = {
            'Python': ['Web API', 'Data Analysis', 'Automation Script', 'Machine Learning'],
            'JavaScript': ['Interactive UI', 'SPA Application', 'Dynamic Website', 'Real-time Chat'],
            'Flask': ['REST API', 'Web Application', 'Backend Service', 'Database Integration'],
            'React': ['Component Library', 'Dashboard', 'E-commerce Site', 'Mobile App']
        };

        const types = projectTypes[skillName] || ['Web Project', 'Application', 'System', 'Tool'];
        const projects = [];

        for (let i = 0; i < Math.min(count, 6); i++) {
            projects.push({
                id: i + 1,
                title: `${types[i % types.length]} ${i + 1}`,
                description: `Projeto desenvolvido usando ${skillName} com foco em funcionalidade e performance.`,
                completion_year: 2024 - Math.floor(Math.random() * 2),
                complexity: Math.floor(Math.random() * 5) + 5,
                url: '#'
            });
        }

        return projects;
    }

    showLoadingState() {
        const resultsContainer = document.getElementById('comparison-results');
        resultsContainer.style.display = 'block';
        resultsContainer.innerHTML = `
            <div class="text-center py-5">
                <div class="spinner-border text-primary" role="status">
                    <span class="visually-hidden">Carregando...</span>
                </div>
                <p class="mt-3 text-muted">Analisando habilidades e coletando dados...</p>
            </div>
        `;
    }

    showErrorState() {
        const resultsContainer = document.getElementById('comparison-results');
        resultsContainer.innerHTML = `
            <div class="alert alert-warning text-center">
                <i class="fas fa-exclamation-triangle me-2"></i>
                Erro ao carregar dados de comparação. Tente novamente.
            </div>
        `;
    }

    displayComparison(skill1, skill2, data) {
        const resultsContainer = document.getElementById('comparison-results');
        
        resultsContainer.innerHTML = `
            <div class="comparison-header text-center mb-5">
                <h3 class="fw-bold">
                    ${skill1.name} <span class="text-muted">vs</span> ${skill2.name}
                </h3>
                <p class="text-muted">Análise detalhada das duas habilidades</p>
            </div>

            ${this.createMetricsComparison(skill1, skill2, data.metrics)}
            ${this.createProjectsComparison(skill1, skill2, data)}
            ${this.createRecommendation(skill1, skill2, data.metrics)}
        `;

        resultsContainer.style.display = 'block';
        
        // Initialize charts if available
        setTimeout(() => {
            this.initializeCharts(data.metrics);
        }, 100);

        // Scroll to results
        resultsContainer.scrollIntoView({ behavior: 'smooth' });
    }

    createMetricsComparison(skill1, skill2, metrics) {
        return `
            <div class="row g-4 mb-5">
                <div class="col-lg-6">
                    <div class="card border-0 shadow-sm h-100">
                        <div class="card-body text-center">
                            <h4 class="text-primary mb-3">
                                <i class="fas fa-star me-2"></i>${skill1.name}
                            </h4>
                            ${this.createSkillMetrics(metrics.skill1, 'primary')}
                        </div>
                    </div>
                </div>
                <div class="col-lg-6">
                    <div class="card border-0 shadow-sm h-100">
                        <div class="card-body text-center">
                            <h4 class="text-success mb-3">
                                <i class="fas fa-star me-2"></i>${skill2.name}
                            </h4>
                            ${this.createSkillMetrics(metrics.skill2, 'success')}
                        </div>
                    </div>
                </div>
            </div>

            <div class="row mb-5">
                <div class="col-12">
                    <div class="card border-0 shadow-sm">
                        <div class="card-body">
                            <h5 class="card-title mb-4">
                                <i class="fas fa-chart-bar me-2"></i>Comparação Visual
                            </h5>
                            <canvas id="comparison-chart" width="400" height="200"></canvas>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }

    createSkillMetrics(metrics, color) {
        return `
            <div class="row g-3">
                <div class="col-6">
                    <div class="metric-item">
                        <div class="metric-value text-${color} fw-bold fs-4">${metrics.proficiency}/10</div>
                        <div class="metric-label text-muted small">Proficiência</div>
                    </div>
                </div>
                <div class="col-6">
                    <div class="metric-item">
                        <div class="metric-value text-${color} fw-bold fs-4">${metrics.projects_count}</div>
                        <div class="metric-label text-muted small">Projetos</div>
                    </div>
                </div>
                <div class="col-6">
                    <div class="metric-item">
                        <div class="metric-value text-${color} fw-bold fs-4">${metrics.experience_years}</div>
                        <div class="metric-label text-muted small">Anos Exp.</div>
                    </div>
                </div>
                <div class="col-6">
                    <div class="metric-item">
                        <div class="metric-value text-${color} fw-bold fs-4">${metrics.complexity_avg}/10</div>
                        <div class="metric-label text-muted small">Complexidade</div>
                    </div>
                </div>
            </div>
        `;
    }

    createProjectsComparison(skill1, skill2, data) {
        return `
            <div class="row g-4 mb-5">
                <div class="col-lg-6">
                    <h5 class="mb-3">
                        <i class="fas fa-project-diagram me-2 text-primary"></i>
                        Projetos com ${skill1.name}
                    </h5>
                    ${data.skill1_projects.map(project => this.createProjectCard(project, 'primary')).join('')}
                </div>
                <div class="col-lg-6">
                    <h5 class="mb-3">
                        <i class="fas fa-project-diagram me-2 text-success"></i>
                        Projetos com ${skill2.name}
                    </h5>
                    ${data.skill2_projects.map(project => this.createProjectCard(project, 'success')).join('')}
                </div>
            </div>
        `;
    }

    createProjectCard(project, color) {
        return `
            <div class="card border-0 shadow-sm mb-3">
                <div class="card-body">
                    <div class="d-flex justify-content-between align-items-start mb-2">
                        <h6 class="card-title mb-0">${project.title}</h6>
                        <span class="badge bg-${color}">${project.complexity}/10</span>
                    </div>
                    <p class="card-text text-muted small mb-2">${project.description}</p>
                    <div class="d-flex justify-content-between align-items-center">
                        <small class="text-muted">
                            <i class="fas fa-calendar me-1"></i>${project.completion_year}
                        </small>
                        <a href="${project.url}" class="btn btn-outline-${color} btn-sm">
                            <i class="fas fa-eye me-1"></i>Ver
                        </a>
                    </div>
                </div>
            </div>
        `;
    }

    createRecommendation(skill1, skill2, metrics) {
        const skill1Score = (metrics.skill1.proficiency + metrics.skill1.projects_count + metrics.skill1.experience_years * 2) / 4;
        const skill2Score = (metrics.skill2.proficiency + metrics.skill2.projects_count + metrics.skill2.experience_years * 2) / 4;
        
        const stronger = skill1Score > skill2Score ? skill1 : skill2;
        const weaker = skill1Score > skill2Score ? skill2 : skill1;

        return `
            <div class="row">
                <div class="col-12">
                    <div class="card border-0 bg-light">
                        <div class="card-body text-center">
                            <h5 class="card-title">
                                <i class="fas fa-lightbulb me-2 text-warning"></i>
                                Análise e Recomendação
                            </h5>
                            <p class="card-text">
                                Com base na análise, <strong>${stronger.name}</strong> aparece como uma habilidade mais consolidada 
                                no meu portfólio, com maior experiência prática e complexidade de projetos. 
                                <strong>${weaker.name}</strong> também é uma competência sólida, complementando 
                                muito bem o conjunto de tecnologias para desenvolvimento completo.
                            </p>
                            <div class="mt-3">
                                <span class="badge bg-primary me-2">Complementares</span>
                                <span class="badge bg-success">Experiência Prática</span>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }

    initializeCharts(metrics) {
        const canvas = document.getElementById('comparison-chart');
        if (!canvas) return;

        // Simple chart using Canvas API (fallback if Chart.js not available)
        const ctx = canvas.getContext('2d');
        const data = [
            { label: 'Proficiência', skill1: metrics.skill1.proficiency, skill2: metrics.skill2.proficiency },
            { label: 'Projetos', skill1: metrics.skill1.projects_count, skill2: metrics.skill2.projects_count },
            { label: 'Experiência', skill1: metrics.skill1.experience_years, skill2: metrics.skill2.experience_years },
            { label: 'Complexidade', skill1: metrics.skill1.complexity_avg, skill2: metrics.skill2.complexity_avg }
        ];

        this.drawComparisonChart(ctx, data, canvas.width, canvas.height);
    }

    drawComparisonChart(ctx, data, width, height) {
        ctx.clearRect(0, 0, width, height);
        
        const barHeight = 30;
        const barSpacing = 60;
        const startY = 50;
        const maxValue = 15;
        
        data.forEach((item, index) => {
            const y = startY + index * barSpacing;
            
            // Draw labels
            ctx.fillStyle = '#666';
            ctx.font = '14px Arial';
            ctx.fillText(item.label, 10, y + 20);
            
            // Draw skill1 bar
            const skill1Width = (item.skill1 / maxValue) * (width - 200);
            ctx.fillStyle = '#0d6efd';
            ctx.fillRect(120, y, skill1Width, barHeight);
            
            // Draw skill2 bar
            const skill2Width = (item.skill2 / maxValue) * (width - 200);
            ctx.fillStyle = '#198754';
            ctx.fillRect(120, y + barHeight + 5, skill2Width, barHeight);
            
            // Draw values
            ctx.fillStyle = '#333';
            ctx.font = '12px Arial';
            ctx.fillText(item.skill1, 120 + skill1Width + 5, y + 20);
            ctx.fillText(item.skill2, 120 + skill2Width + 5, y + barHeight + 20);
        });
    }
}

// Initialize Skills Comparator
document.addEventListener('DOMContentLoaded', function() {
    if (document.getElementById('skills-comparator')) {
        window.skillsComparator = new SkillsComparator();
    }
});