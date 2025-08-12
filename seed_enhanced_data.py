#!/usr/bin/env python3
"""
Enhanced data seeder for the digital portfolio
Creates sample data for all new features: skills, timeline events, etc.
"""

import json
from datetime import datetime, date
from app import app, db
from models import (
    User, Project, Category, Tag, project_tags, 
    Skill, ProjectSkill, TimelineEvent, Recommendation,
    AboutMe
)

def create_sample_skills():
    """Create sample skills data"""
    skills_data = [
        {'name': 'Python', 'level': 9, 'experience_years': 3, 'description': 'Linguagem principal para desenvolvimento backend', 'icon': 'fab fa-python', 'color': '#3776ab'},
        {'name': 'JavaScript', 'level': 8, 'experience_years': 4, 'description': 'Desenvolvimento frontend e fullstack', 'icon': 'fab fa-js-square', 'color': '#f7df1e'},
        {'name': 'Flask', 'level': 9, 'experience_years': 2.5, 'description': 'Framework web Python para APIs e aplicações', 'icon': 'fas fa-flask', 'color': '#000000'},
        {'name': 'React', 'level': 7, 'experience_years': 2, 'description': 'Biblioteca para interfaces de usuário', 'icon': 'fab fa-react', 'color': '#61dafb'},
        {'name': 'SQL', 'level': 8, 'experience_years': 3, 'description': 'Banco de dados relacional e consultas avançadas', 'icon': 'fas fa-database', 'color': '#336791'},
        {'name': 'HTML/CSS', 'level': 9, 'experience_years': 4, 'description': 'Marcação e estilização web moderna', 'icon': 'fab fa-html5', 'color': '#e34f26'},
        {'name': 'Bootstrap', 'level': 8, 'experience_years': 3, 'description': 'Framework CSS responsivo', 'icon': 'fab fa-bootstrap', 'color': '#7952b3'},
        {'name': 'Git', 'level': 8, 'experience_years': 3.5, 'description': 'Controle de versão e colaboração', 'icon': 'fab fa-git-alt', 'color': '#f05032'},
    ]
    
    created_skills = []
    for skill_data in skills_data:
        existing_skill = Skill.query.filter_by(name=skill_data['name']).first()
        if not existing_skill:
            skill = Skill(**skill_data)
            db.session.add(skill)
            created_skills.append(skill)
    
    db.session.commit()
    print(f"Created {len(created_skills)} skills")
    return Skill.query.all()

def create_timeline_events():
    """Create sample timeline events"""
    events_data = [
        {
            'title': 'Início na Programação',
            'description': 'Primeiros passos no mundo da programação com Python básico',
            'event_date': date(2022, 3, 15),
            'event_type': 'education',
            'importance': 5,
            'event_metadata': json.dumps({
                'technologies': ['Python', 'HTML'],
                'achievements': ['Primeiro programa funcional', 'Conceitos básicos de lógica']
            })
        },
        {
            'title': 'Primeiro Projeto Web',
            'description': 'Desenvolvimento do primeiro website responsivo usando HTML, CSS e JavaScript',
            'event_date': date(2022, 8, 20),
            'event_type': 'project',
            'importance': 4,
            'event_metadata': json.dumps({
                'technologies': ['HTML', 'CSS', 'JavaScript'],
                'achievements': ['Website totalmente responsivo', 'Primeira experiência com DOM']
            })
        },
        {
            'title': 'Certificação Python Avançado',
            'description': 'Concluído curso avançado de Python para desenvolvimento web',
            'event_date': date(2023, 2, 10),
            'event_type': 'achievement',
            'importance': 3,
            'event_metadata': json.dumps({
                'technologies': ['Python', 'Flask', 'SQLAlchemy'],
                'achievements': ['Certificado com nota máxima', 'Projeto final aprovado']
            })
        },
        {
            'title': 'Sistema de E-commerce',
            'description': 'Desenvolvimento completo de plataforma de vendas online com painel administrativo',
            'event_date': date(2023, 7, 5),
            'event_type': 'project',
            'importance': 5,
            'event_metadata': json.dumps({
                'technologies': ['Python', 'Flask', 'SQLAlchemy', 'Bootstrap', 'JavaScript'],
                'achievements': ['Sistema completo de pagamento', 'Painel admin avançado', 'API RESTful']
            })
        },
        {
            'title': 'Portfólio Digital Interativo',
            'description': 'Criação deste portfólio com funcionalidades avançadas e IA integrada',
            'event_date': date(2024, 1, 15),
            'event_type': 'project',
            'importance': 5,
            'event_metadata': json.dumps({
                'technologies': ['Python', 'Flask', 'SQLite', 'Bootstrap', 'JavaScript', 'IA'],
                'achievements': ['Sistema de recomendação IA', 'Timeline interativa', 'Comparador de habilidades']
            })
        }
    ]
    
    created_events = []
    for event_data in events_data:
        existing_event = TimelineEvent.query.filter_by(title=event_data['title']).first()
        if not existing_event:
            event = TimelineEvent(**event_data)
            db.session.add(event)
            created_events.append(event)
    
    db.session.commit()
    print(f"Created {len(created_events)} timeline events")
    return created_events

def associate_skills_with_projects():
    """Associate existing skills with projects"""
    skills = Skill.query.all()
    projects = Project.query.all()
    
    if not skills or not projects:
        print("No skills or projects found to associate")
        return
    
    # Define skill associations for different project types
    skill_associations = {
        'Python': ['Flask', 'SQL', 'Git'],
        'JavaScript': ['HTML/CSS', 'Bootstrap', 'Git'],
        'Flask': ['Python', 'SQL', 'HTML/CSS'],
        'React': ['JavaScript', 'HTML/CSS', 'Git'],
    }
    
    created_associations = 0
    
    for project in projects:
        # Randomly assign 2-4 skills per project
        import random
        
        # Primary skill (usually related to project title/description)
        primary_skills = [s for s in skills if s.name in ['Python', 'JavaScript', 'Flask', 'React']]
        if primary_skills:
            primary_skill = random.choice(primary_skills)
            
            # Check if association already exists
            existing = ProjectSkill.query.filter_by(
                project_id=project.id, 
                skill_id=primary_skill.id
            ).first()
            
            if not existing:
                project_skill = ProjectSkill(
                    project_id=project.id,
                    skill_id=primary_skill.id,
                    proficiency_used=random.randint(7, 10),
                    is_primary=True
                )
                db.session.add(project_skill)
                created_associations += 1
                
                # Add related skills
                related_skill_names = skill_associations.get(primary_skill.name, [])
                for skill_name in related_skill_names[:2]:  # Limit to 2 related skills
                    related_skill = next((s for s in skills if s.name == skill_name), None)
                    if related_skill:
                        existing_related = ProjectSkill.query.filter_by(
                            project_id=project.id,
                            skill_id=related_skill.id
                        ).first()
                        
                        if not existing_related:
                            project_skill_related = ProjectSkill(
                                project_id=project.id,
                                skill_id=related_skill.id,
                                proficiency_used=random.randint(5, 8),
                                is_primary=False
                            )
                            db.session.add(project_skill_related)
                            created_associations += 1
    
    db.session.commit()
    print(f"Created {created_associations} skill-project associations")

def create_sample_about_me():
    """Create or update About Me section"""
    existing_about = AboutMe.query.first()
    
    if not existing_about:
        about_me = AboutMe(
            title="Desenvolvedor Full Stack & Entusiasta de IA",
            content="""
            <p>Olá! Sou um desenvolvedor apaixonado por tecnologia e inovação, especializado em criar soluções web modernas e inteligentes. Com mais de 3 anos de experiência em desenvolvimento, tenho focado em <strong>Python</strong> e <strong>JavaScript</strong> para construir aplicações robustas e escaláveis.</p>
            
            <p>Minha jornada na programação começou com a curiosidade de entender como as coisas funcionam por trás das telas. Desde então, venho desenvolvendo projetos que combinam <strong>funcionalidade</strong>, <strong>design</strong> e <strong>experiência do usuário</strong>.</p>
            
            <h5>💡 O que me motiva:</h5>
            <ul>
                <li>Resolver problemas complexos com soluções elegantes</li>
                <li>Integrar inteligência artificial em aplicações práticas</li>
                <li>Criar interfaces intuitivas e responsivas</li>
                <li>Aprender continuamente novas tecnologias</li>
            </ul>
            
            <h5>🚀 Especialidades:</h5>
            <ul>
                <li><strong>Backend:</strong> Python, Flask, APIs RESTful, Banco de dados</li>
                <li><strong>Frontend:</strong> JavaScript, HTML/CSS, Bootstrap, UI/UX</li>
                <li><strong>Ferramentas:</strong> Git, SQLite, Deployment, Testes</li>
                <li><strong>Soft Skills:</strong> Resolução de problemas, Trabalho em equipe, Comunicação</li>
            </ul>
            
            <p>Estou sempre em busca de novos desafios e oportunidades para aplicar meu conhecimento em projetos que façam a diferença. Se você tem uma ideia ou projeto interessante, adoraria conversar!</p>
            """,
            linkedin_url="https://linkedin.com/in/developer",
            github_url="https://github.com/developer",
            email="dev@portfolio.com",
            phone="+55 11 99999-9999"
        )
        db.session.add(about_me)
        db.session.commit()
        print("Created About Me section")
    else:
        print("About Me section already exists")

def main():
    """Run the enhanced data seeder"""
    with app.app_context():
        print("🌱 Seeding enhanced data...")
        
        # Create skills
        skills = create_sample_skills()
        
        # Create timeline events
        create_timeline_events()
        
        # Associate skills with existing projects
        associate_skills_with_projects()
        
        # Create/update About Me
        create_sample_about_me()
        
        print("✅ Enhanced data seeding completed!")
        
        # Print summary
        total_skills = Skill.query.count()
        total_events = TimelineEvent.query.count()
        total_associations = ProjectSkill.query.count()
        
        print(f"\n📊 Database Summary:")
        print(f"   Skills: {total_skills}")
        print(f"   Timeline Events: {total_events}")
        print(f"   Skill-Project Associations: {total_associations}")
        print(f"   Projects: {Project.query.count()}")
        print(f"   Categories: {Category.query.count()}")

if __name__ == '__main__':
    main()