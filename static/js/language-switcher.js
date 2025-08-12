// Language Switcher for Portuguese/English
class LanguageSwitcher {
    constructor() {
        // Check if user is authenticated and has a language preference
        const userLang = document.body.dataset.userLanguage;
        this.currentLanguage = userLang || localStorage.getItem('language') || 'pt-BR';
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
                'nav_timeline': 'Timeline',
                'nav_comparator': 'Comparador',
                'nav_login': 'Entrar',
                'nav_register': 'Cadastrar',
                'nav_admin': 'Admin',
                'nav_logout': 'Sair',
                'btn_view_project': 'Ver Projeto',
                'btn_view_all': 'Ver Todos',
                'btn_demo': 'Demo',
                'btn_code': 'Código',
                'btn_login': 'Entrar',
                'btn_register': 'Cadastrar',
                'label_featured': 'Destaque',
                'label_projects': 'Projetos',
                'label_featured_count': 'Destaques',
                'label_since': 'Desde',
                'title_featured_projects': 'Projetos em Destaque',
                'subtitle_featured': 'Destacando meus melhores trabalhos e inovações',
                'title_recent_projects': 'Projetos Recentes',
                'subtitle_recent': 'Adições mais recentes ao meu portfólio',
                'welcome_title': 'Bem-vindo ao Meu Portfólio Digital',
                'welcome_subtitle': 'Apresentando criatividade, inovação e excelência técnica através de projetos e experiências cuidadosamente elaborados.',
                'btn_view_projects': 'Ver Projetos',
                'btn_about_me': 'Sobre Mim',
                'label_featured_badge': 'Destaque',
                'footer_copyright': 'Todos os direitos reservados.',
                'footer_built_with': 'Construído com',
                'search_placeholder': 'Buscar projetos...',
                'timeline_title': 'Linha do Tempo da Carreira',
                'timeline_subtitle': 'Acompanhe a evolução dos meus projetos e conquistas',
                'comparator_title': 'Comparador de Habilidades',
                'comparator_subtitle': 'Compare duas habilidades do meu portfólio',
                'btn_explore': 'Explorar Projeto',
                'btn_view_all_projects': 'Ver Todos os Projetos',
                'label_collaboration': 'Colaboração',
                'cta_title_primary': 'Vamos Trabalhar',
                'cta_title_accent': 'Juntos',
                'cta_subtitle': 'Transforme suas ideias em realidade. Estou aqui para criar soluções inovadoras e impactantes que elevem seus projetos ao próximo nível.',
                'feature_innovation': 'Inovação',
                'feature_collaboration': 'Colaboração',
                'feature_results': 'Resultados',
                'btn_send_email': 'Enviar E-mail',
                'btn_email_subtitle': 'Resposta em 24h',
                'btn_schedule_meeting': 'Agendar Reunião',
                'btn_meeting_subtitle': '30 min gratuitos',
                'btn_connect_linkedin': 'Conectar LinkedIn',
                'btn_linkedin_subtitle': 'Vamos nos conectar',
                'trust_secure': '100% Seguro',
                'trust_response': 'Resposta Rápida',
                'trust_quality': 'Alta Qualidade'
            },
            'en': {
                'nav_home': 'Home',
                'nav_projects': 'Projects',
                'nav_about': 'About',
                'nav_contact': 'Contact',
                'nav_timeline': 'Timeline',
                'nav_comparator': 'Comparator',
                'nav_login': 'Login',
                'nav_register': 'Register',
                'nav_admin': 'Admin',
                'nav_logout': 'Logout',
                'btn_view_project': 'View Project',
                'btn_view_all': 'View All',
                'btn_demo': 'Demo',
                'btn_code': 'Code',
                'btn_login': 'Login',
                'btn_register': 'Register',
                'label_featured': 'Featured',
                'label_projects': 'Projects',
                'label_featured_count': 'Featured',
                'label_since': 'Since',
                'title_featured_projects': 'Featured Projects',
                'subtitle_featured': 'Highlighting my best work and innovations',
                'title_recent_projects': 'Recent Projects',
                'subtitle_recent': 'Latest additions to my portfolio',
                'welcome_title': 'Welcome to My Digital Portfolio',
                'welcome_subtitle': 'Showcasing creativity, innovation, and technical excellence through carefully crafted projects and experiences.',
                'btn_view_projects': 'View Projects',
                'btn_about_me': 'About Me',
                'label_featured_badge': 'Featured',
                'footer_copyright': 'All rights reserved.',
                'footer_built_with': 'Built with',
                'search_placeholder': 'Search projects...',
                'timeline_title': 'Career Timeline',
                'timeline_subtitle': 'Follow the evolution of my projects and achievements',
                'comparator_title': 'Skills Comparator',
                'comparator_subtitle': 'Compare two skills from my portfolio',
                'btn_explore': 'Explore Project',
                'btn_view_all_projects': 'View All Projects',
                'label_collaboration': 'Collaboration',
                'cta_title_primary': 'Let\'s Work',
                'cta_title_accent': 'Together',
                'cta_subtitle': 'Transform your ideas into reality. I\'m here to create innovative and impactful solutions that take your projects to the next level.',
                'feature_innovation': 'Innovation',
                'feature_collaboration': 'Collaboration',
                'feature_results': 'Results',
                'btn_send_email': 'Send Email',
                'btn_email_subtitle': 'Response in 24h',
                'btn_schedule_meeting': 'Schedule Meeting',
                'btn_meeting_subtitle': '30 min free',
                'btn_connect_linkedin': 'Connect LinkedIn',
                'btn_linkedin_subtitle': 'Let\'s connect',
                'trust_secure': '100% Secure',
                'trust_response': 'Quick Response',
                'trust_quality': 'High Quality'
            }
        };
    }

    createLanguageButton() {
        const navbar = document.querySelector('.navbar-nav:last-child');
        if (navbar) {
            const langButton = document.createElement('li');
            langButton.className = 'nav-item dropdown me-2';
            langButton.innerHTML = `
                <a class="nav-link dropdown-toggle" href="javascript:void(0)" id="languageDropdown" role="button" data-bs-toggle="dropdown" aria-expanded="false">
                    <i class="fas fa-globe me-1"></i>${this.currentLanguage === 'pt-BR' ? 'PT' : 'EN'}
                </a>
                <ul class="dropdown-menu" aria-labelledby="languageDropdown">
                    <li><a class="dropdown-item" href="javascript:void(0)" onclick="languageSwitcher.switchLanguage('pt-BR')">
                        <i class="fas fa-flag me-2"></i>Português (BR)
                    </a></li>
                    <li><a class="dropdown-item" href="javascript:void(0)" onclick="languageSwitcher.switchLanguage('en')">
                        <i class="fas fa-flag me-2"></i>English (US)
                    </a></li>
                </ul>
            `;
            // Insert before the first nav item (login/register or user menu)
            navbar.insertBefore(langButton, navbar.firstChild);
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

        // Save language preference for authenticated users
        if (document.body.dataset.authenticated === 'true') {
            fetch('/api/save-language-preference', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-Requested-With': 'XMLHttpRequest'
                },
                body: JSON.stringify({ language: language })
            }).catch(err => console.log('Language preference not saved:', err));
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

        // Update document language attribute
        document.documentElement.lang = this.currentLanguage;
        
        // Update page title
        const titleElement = document.querySelector('title');
        if (titleElement && titleElement.dataset.i18n) {
            const titleKey = titleElement.dataset.i18n;
            if (translations[titleKey]) {
                titleElement.textContent = translations[titleKey];
            }
        }
    }

    t(key) {
        return this.translations[this.currentLanguage][key] || key;
    }
}

// Initialize language switcher when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    window.languageSwitcher = new LanguageSwitcher();
});