// Language Switcher for Portuguese/English
class LanguageSwitcher {
    constructor() {
        this.currentLanguage = localStorage.getItem('language') || 'pt-BR';
        this.translations = {};
        this.init();
    }

    init() {
        this.loadTranslations();
        this.createLanguageButton();
        this.applyLanguage();
    }

    loadTranslations() {
        // Translations for the interface
        this.translations = {
            'pt-BR': {
                'nav_home': 'Início',
                'nav_projects': 'Projetos',
                'nav_about': 'Sobre',
                'nav_contact': 'Contato',
                'nav_login': 'Entrar',
                'nav_register': 'Cadastrar',
                'nav_admin': 'Admin',
                'nav_logout': 'Sair',
                'btn_view_project': 'Ver Projeto',
                'btn_view_all': 'Ver Todos',
                'btn_demo': 'Demo',
                'btn_code': 'Código',
                'label_featured': 'Destaque',
                'label_projects': 'Projetos',
                'label_featured_count': 'Destaques',
                'label_since': 'Desde',
                'title_featured_projects': 'Projetos em Destaque',
                'subtitle_featured': 'Destacando meus melhores trabalhos e inovações',
                'title_recent_projects': 'Projetos Recentes',
                'subtitle_recent': 'Adições mais recentes ao meu portfólio',
                'welcome_title': 'Bem-vindo ao Meu Portfólio Digital',
                'welcome_subtitle': 'Apresentando criatividade, inovação e excelência técnica através de projetos e experiências cuidadosamente elaborados.'
            },
            'en': {
                'nav_home': 'Home',
                'nav_projects': 'Projects',
                'nav_about': 'About',
                'nav_contact': 'Contact',
                'nav_login': 'Login',
                'nav_register': 'Register',
                'nav_admin': 'Admin',
                'nav_logout': 'Logout',
                'btn_view_project': 'View Project',
                'btn_view_all': 'View All',
                'btn_demo': 'Demo',
                'btn_code': 'Code',
                'label_featured': 'Featured',
                'label_projects': 'Projects',
                'label_featured_count': 'Featured',
                'label_since': 'Since',
                'title_featured_projects': 'Featured Projects',
                'subtitle_featured': 'Highlighting my best work and innovations',
                'title_recent_projects': 'Recent Projects',
                'subtitle_recent': 'Latest additions to my portfolio',
                'welcome_title': 'Welcome to My Digital Portfolio',
                'welcome_subtitle': 'Showcasing creativity, innovation, and technical excellence through carefully crafted projects and experiences.'
            }
        };
    }

    createLanguageButton() {
        const navbar = document.querySelector('.navbar-nav');
        if (navbar) {
            const langButton = document.createElement('li');
            langButton.className = 'nav-item dropdown';
            langButton.innerHTML = `
                <a class="nav-link dropdown-toggle" href="#" id="languageDropdown" role="button" data-bs-toggle="dropdown" aria-expanded="false">
                    <i class="fas fa-globe me-1"></i>${this.currentLanguage === 'pt-BR' ? 'PT' : 'EN'}
                </a>
                <ul class="dropdown-menu" aria-labelledby="languageDropdown">
                    <li><a class="dropdown-item" href="#" onclick="languageSwitcher.switchLanguage('pt-BR')">
                        <i class="fas fa-flag me-2"></i>Português (BR)
                    </a></li>
                    <li><a class="dropdown-item" href="#" onclick="languageSwitcher.switchLanguage('en')">
                        <i class="fas fa-flag me-2"></i>English (US)
                    </a></li>
                </ul>
            `;
            navbar.appendChild(langButton);
        }
    }

    switchLanguage(language) {
        this.currentLanguage = language;
        localStorage.setItem('language', language);
        this.applyLanguage();
        
        // Update language button text
        const langButton = document.querySelector('#languageDropdown');
        if (langButton) {
            langButton.innerHTML = `<i class="fas fa-globe me-1"></i>${language === 'pt-BR' ? 'PT' : 'EN'}`;
        }
    }

    applyLanguage() {
        const translations = this.translations[this.currentLanguage];
        
        // Apply translations to elements with data-i18n attributes
        document.querySelectorAll('[data-i18n]').forEach(element => {
            const key = element.getAttribute('data-i18n');
            if (translations[key]) {
                if (element.tagName === 'INPUT' || element.tagName === 'TEXTAREA') {
                    element.placeholder = translations[key];
                } else {
                    element.textContent = translations[key];
                }
            }
        });
    }

    t(key) {
        return this.translations[this.currentLanguage][key] || key;
    }
}

// Initialize language switcher when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    window.languageSwitcher = new LanguageSwitcher();
});