from flask import jsonify, request, current_app
from flask_login import current_user, login_required
import json
from datetime import datetime, date
from sqlalchemy import func, desc, or_
import re

def init_api_routes(app):
    
    @app.route('/api/recommendations', methods=['POST'])
    def get_ai_recommendations():
        """Get AI-powered project recommendations"""
        from models import Project, Tag, Category
        from app import db
        try:
            data = request.get_json()
            project_id = data.get('projectId')
            tags = data.get('tags', [])
            category = data.get('category', '')
            description = data.get('description', '')
            
            if not project_id:
                return jsonify({'error': 'Project ID required'}), 400
            
            # Get current project
            current_project = Project.query.get(project_id)
            if not current_project:
                return jsonify({'error': 'Project not found'}), 404
            
            # Find similar projects using multiple criteria
            recommendations = []
            
            # 1. Tag-based similarity
            if tags:
                tag_projects = Project.query.join(Project.tags).filter(
                    Tag.name.in_(tags),
                    Project.id != project_id,
                    Project.is_published == True
                ).distinct().all()
                
                for project in tag_projects:
                    common_tags = set(tags) & set([tag.name for tag in project.tags])
                    score = len(common_tags) / len(tags) if tags else 0
                    recommendations.append({
                        'project': project,
                        'score': score * 0.4,
                        'type': 'tag'
                    })
            
            # 2. Category-based similarity
            if category:
                category_projects = Project.query.join(Category).filter(
                    Category.name == category,
                    Project.id != project_id,
                    Project.is_published == True
                ).all()
                
                for project in category_projects:
                    recommendations.append({
                        'project': project,
                        'score': 0.3,
                        'type': 'category'
                    })
            
            # 3. Content-based similarity (simple keyword matching)
            if description:
                description_words = set(re.findall(r'\w+', description.lower()))
                content_projects = Project.query.filter(
                    Project.id != project_id,
                    Project.is_published == True
                ).all()
                
                for project in content_projects:
                    project_words = set(re.findall(r'\w+', (project.description + ' ' + (project.content or '')).lower()))
                    common_words = description_words & project_words
                    
                    if common_words:
                        score = len(common_words) / max(len(description_words), len(project_words))
                        if score > 0.1:  # Only consider if similarity > 10%
                            recommendations.append({
                                'project': project,
                                'score': score * 0.3,
                                'type': 'content'
                            })
            
            # Combine and rank recommendations
            project_scores = {}
            for rec in recommendations:
                project_id = rec['project'].id
                if project_id in project_scores:
                    project_scores[project_id]['score'] += rec['score']
                else:
                    project_scores[project_id] = {
                        'project': rec['project'],
                        'score': rec['score'],
                        'types': [rec['type']]
                    }
            
            # Sort by score and take top 3
            sorted_recommendations = sorted(
                project_scores.values(),
                key=lambda x: x['score'],
                reverse=True
            )[:3]
            
            # Format response
            response_data = []
            for rec in sorted_recommendations:
                project = rec['project']
                response_data.append({
                    'id': project.id,
                    'title': project.title,
                    'description': project.description,
                    'image_filename': project.image_filename,
                    'tags': [tag.name for tag in project.tags] if project.tags else [],
                    'category': project.category.name if project.category else '',
                    'likes_count': project.likes_count,
                    'demo_url': project.demo_url,
                    'github_url': project.github_url,
                    'similarity_score': round(rec['score'], 2),
                    'similarity_types': rec['types']
                })
            
            return jsonify({
                'recommendations': response_data,
                'total': len(response_data)
            })
            
        except Exception as e:
            current_app.logger.error(f"Recommendation error: {str(e)}")
            return jsonify({'error': 'Failed to generate recommendations'}), 500
    
    @app.route('/api/timeline')
    def get_timeline_data():
        """Get career timeline events"""
        from models import TimelineEvent
        try:
            events = TimelineEvent.query.filter_by(is_published=True).order_by(TimelineEvent.event_date).all()
            
            timeline_data = []
            for event in events:
                event_data = {
                    'id': event.id,
                    'title': event.title,
                    'description': event.description,
                    'date': event.event_date.isoformat(),
                    'type': event.event_type,
                    'importance': event.importance,
                    'image': f'/static/uploads/{event.image_filename}' if event.image_filename else None,
                    'external_url': event.external_url,
                    'project_id': event.project_id
                }
                
                # Parse event_metadata if exists
                if event.event_metadata:
                    try:
                        metadata = json.loads(event.event_metadata)
                        event_data['technologies'] = metadata.get('technologies', [])
                        event_data['achievements'] = metadata.get('achievements', [])
                    except:
                        pass
                
                timeline_data.append(event_data)
            
            return jsonify({
                'timeline': timeline_data,
                'total': len(timeline_data)
            })
            
        except Exception as e:
            current_app.logger.error(f"Timeline error: {str(e)}")
            return jsonify({'error': 'Failed to load timeline data'}), 500
    
    @app.route('/api/skills')
    def get_skills_data():
        """Get all skills data"""
        from models import Skill
        try:
            skills = Skill.query.order_by(desc(Skill.level)).all()
            
            skills_data = []
            for skill in skills:
                skills_data.append({
                    'id': skill.id,
                    'name': skill.name,
                    'level': skill.level,
                    'experience_years': skill.experience_years,
                    'description': skill.description,
                    'icon': skill.icon,
                    'color': skill.color,
                    'projects': skill.projects_count
                })
            
            return jsonify({
                'skills': skills_data,
                'total': len(skills_data)
            })
            
        except Exception as e:
            current_app.logger.error(f"Skills error: {str(e)}")
            return jsonify({'error': 'Failed to load skills data'}), 500
    
    @app.route('/api/skills/compare', methods=['POST'])
    def compare_skills():
        """Compare two skills and return detailed analysis"""
        from models import Skill, ProjectSkill, Project
        from app import db
        try:
            data = request.get_json()
            skill1_id = data.get('skill1_id')
            skill2_id = data.get('skill2_id')
            
            if not skill1_id or not skill2_id:
                return jsonify({'error': 'Both skill IDs required'}), 400
            
            skill1 = Skill.query.get(skill1_id)
            skill2 = Skill.query.get(skill2_id)
            
            if not skill1 or not skill2:
                return jsonify({'error': 'One or both skills not found'}), 404
            
            # Get projects for each skill
            skill1_projects = db.session.query(Project).join(ProjectSkill).filter(
                ProjectSkill.skill_id == skill1_id,
                Project.is_published == True
            ).all()
            
            skill2_projects = db.session.query(Project).join(ProjectSkill).filter(
                ProjectSkill.skill_id == skill2_id,
                Project.is_published == True
            ).all()
            
            # Calculate metrics
            def calculate_complexity_avg(projects, skill_id):
                if not projects:
                    return 0
                
                complexities = []
                for project in projects:
                    project_skill = ProjectSkill.query.filter_by(
                        project_id=project.id, 
                        skill_id=skill_id
                    ).first()
                    if project_skill:
                        complexities.append(project_skill.proficiency_used)
                
                return round(sum(complexities) / len(complexities) if complexities else 0, 1)
            
            # Format project data
            def format_projects(projects, skill_id):
                formatted = []
                for project in projects[:6]:  # Limit to 6 projects
                    project_skill = ProjectSkill.query.filter_by(
                        project_id=project.id,
                        skill_id=skill_id
                    ).first()
                    
                    formatted.append({
                        'id': project.id,
                        'title': project.title,
                        'description': project.description,
                        'completion_year': project.created_at.year,
                        'complexity': project_skill.proficiency_used if project_skill else 5,
                        'url': f'/project/{project.id}',
                        'is_primary': project_skill.is_primary if project_skill else False
                    })
                
                return formatted
            
            response_data = {
                'skill1_projects': format_projects(skill1_projects, skill1_id),
                'skill2_projects': format_projects(skill2_projects, skill2_id),
                'metrics': {
                    'skill1': {
                        'proficiency': skill1.level,
                        'projects_count': len(skill1_projects),
                        'experience_years': skill1.experience_years,
                        'complexity_avg': calculate_complexity_avg(skill1_projects, skill1_id)
                    },
                    'skill2': {
                        'proficiency': skill2.level,
                        'projects_count': len(skill2_projects),
                        'experience_years': skill2.experience_years,
                        'complexity_avg': calculate_complexity_avg(skill2_projects, skill2_id)
                    }
                }
            }
            
            return jsonify(response_data)
            
        except Exception as e:
            current_app.logger.error(f"Skills comparison error: {str(e)}")
            return jsonify({'error': 'Failed to compare skills'}), 500

    @app.route('/api/save-language-preference', methods=['POST'])
    @login_required
    def save_language_preference():
        """Save user language preference"""
        from app import db
        try:
            data = request.get_json()
            language = data.get('language')
            
            if language not in ['pt-BR', 'en']:
                return jsonify({'error': 'Invalid language'}), 400
            
            current_user.preferred_language = language
            db.session.commit()
            
            return jsonify({'success': True, 'language': language})
            
        except Exception as e:
            current_app.logger.error(f"Language preference save error: {str(e)}")
            return jsonify({'error': 'Failed to save language preference'}), 500

    @app.route('/api/toggle-like/<int:project_id>', methods=['POST'])
    @login_required
    def api_toggle_like(project_id):
        """Toggle like status for a project with duplicate prevention"""
        try:
            from models import Like, Project
            
            project = Project.query.get_or_404(project_id)
            
            # Check if user already liked this project
            existing_like = Like.query.filter_by(
                user_id=current_user.id,
                project_id=project_id
            ).first()
            
            if existing_like:
                # Unlike - remove the like
                db.session.delete(existing_like)
                liked = False
            else:
                # Like - add new like
                new_like = Like(user_id=current_user.id, project_id=project_id)
                db.session.add(new_like)
                liked = True
            
            db.session.commit()
            
            # Get updated like count
            likes_count = Like.query.filter_by(project_id=project_id).count()
            
            return jsonify({
                'success': True,
                'liked': liked,
                'likes_count': likes_count
            })
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Toggle like error: {str(e)}")
            return jsonify({'error': 'Erro ao processar curtida'}), 500

    @app.route('/api/add-comment/<int:project_id>', methods=['POST'])
    @login_required  
    def api_add_comment(project_id):
        """Add comment to project with validation"""
        try:
            from models import Comment, Project
            
            data = request.get_json()
            content = data.get('content', '').strip()
            
            # Validation
            if not content:
                return jsonify({'error': 'Comentário não pode estar vazio'}), 400
                
            if len(content) > 1000:
                return jsonify({'error': 'Comentário muito longo (máximo 1000 caracteres)'}), 400
            
            # Check if project exists
            project = Project.query.get_or_404(project_id)
            
            # Create new comment
            new_comment = Comment(
                content=content,
                user_id=current_user.id,
                project_id=project_id
            )
            
            db.session.add(new_comment)
            db.session.commit()
            
            # Get total comments count
            total_comments = Comment.query.filter_by(project_id=project_id).count()
            
            # Return comment data
            comment_data = {
                'id': new_comment.id,
                'content': new_comment.content,
                'author_name': current_user.full_name or current_user.username,
                'created_at': new_comment.created_at.isoformat(),
                'project_id': project_id
            }
            
            return jsonify({
                'success': True,
                'comment': comment_data,
                'total_comments': total_comments
            })
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Add comment error: {str(e)}")
            return jsonify({'error': 'Erro ao adicionar comentário'}), 500