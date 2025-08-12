from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, TextAreaField, PasswordField, BooleanField, SelectField, SubmitField, HiddenField
from wtforms.validators import DataRequired, Email, Length, EqualTo, URL, Optional
from models import Category

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Senha', validators=[DataRequired()])
    remember_me = BooleanField('Lembrar-me')
    submit = SubmitField('Entrar')

class RegisterForm(FlaskForm):
    username = StringField('Nome de Usuário', validators=[DataRequired(), Length(min=4, max=20)])
    full_name = StringField('Nome Completo', validators=[DataRequired(), Length(min=2, max=100)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Senha', validators=[DataRequired(), Length(min=6)])
    password2 = PasswordField('Repetir Senha', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Cadastrar')

class ProjectForm(FlaskForm):
    title = StringField('Título', validators=[DataRequired(), Length(max=200)])
    description = TextAreaField('Descrição', validators=[DataRequired()])
    content = TextAreaField('Conteúdo')
    image = FileField('Imagem do Projeto', validators=[FileAllowed(['jpg', 'png', 'gif', 'jpeg'], 'Apenas imagens!')])
    demo_url = StringField('URL de Demonstração', validators=[Optional(), URL()])
    github_url = StringField('URL do GitHub', validators=[Optional(), URL()])
    category_id = SelectField('Categoria', coerce=int)
    tags = StringField('Tags (separadas por vírgula)')
    is_published = BooleanField('Publicado')
    is_featured = BooleanField('Em Destaque')
    submit = SubmitField('Salvar Projeto')
    
    def __init__(self, *args, **kwargs):
        super(ProjectForm, self).__init__(*args, **kwargs)
        self.category_id.choices = [(c.id, c.name) for c in Category.query.all()]

class CategoryForm(FlaskForm):
    name = StringField('Nome', validators=[DataRequired(), Length(max=100)])
    description = TextAreaField('Descrição')
    submit = SubmitField('Salvar Categoria')

class CommentForm(FlaskForm):
    content = TextAreaField('Comentário', validators=[DataRequired(), Length(min=10, max=500)])
    submit = SubmitField('Adicionar Comentário')

class SearchForm(FlaskForm):
    query = StringField('Buscar', validators=[DataRequired()])
    submit = SubmitField('Pesquisar')

class AboutMeForm(FlaskForm):
    title = StringField('Título', validators=[DataRequired(), Length(max=200)])
    content = TextAreaField('Conteúdo', validators=[DataRequired()])
    image = FileField('Foto de Perfil', validators=[FileAllowed(['jpg', 'png', 'gif', 'jpeg'], 'Apenas imagens!')])
    linkedin_url = StringField('URL do LinkedIn', validators=[Optional(), URL()])
    github_url = StringField('URL do GitHub', validators=[Optional(), URL()])
    email = StringField('Email', validators=[Optional(), Email()])
    phone = StringField('Telefone', validators=[Optional(), Length(max=20)])
    submit = SubmitField('Salvar')

# Admin Forms
class UserPromoteForm(FlaskForm):
    user_id = HiddenField('ID do Usuário', validators=[DataRequired()])
    submit = SubmitField('Promover a Admin')

class UserDemoteForm(FlaskForm):
    user_id = HiddenField('ID do Usuário', validators=[DataRequired()])
    submit = SubmitField('Remover Admin')

class UserDeactivateForm(FlaskForm):
    user_id = HiddenField('ID do Usuário', validators=[DataRequired()])
    submit = SubmitField('Desativar Usuário')

class UserActivateForm(FlaskForm):
    user_id = HiddenField('ID do Usuário', validators=[DataRequired()])
    submit = SubmitField('Activate User')
