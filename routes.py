import os
import uuid
import json
from datetime import datetime, timedelta
from flask import render_template, request, redirect, url_for, session, flash, jsonify
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from openai import OpenAI
from app import app, db
from models import Property, Post, AdminSession, PropertyImage, ChatbotConversation

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'mp4', 'avi', 'mov'}
ADMIN_PASSWORD = "4731v8"

# Initialize OpenAI
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
openai_client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    # Get 3 most recent properties and posts for homepage
    recent_properties = Property.query.order_by(Property.created_at.desc()).limit(3).all()
    recent_posts = Post.query.order_by(Post.created_at.desc()).limit(3).all()
    return render_template('index.html', properties=recent_properties, posts=recent_posts)

@app.route('/sobre')
def about():
    return render_template('about.html')

@app.route('/servicos')
def services():
    return render_template('services.html')

@app.route('/galeria')
def gallery():
    properties = Property.query.order_by(Property.created_at.desc()).all()
    return render_template('gallery.html', properties=properties)

@app.route('/contato')
def contact():
    return render_template('contact.html')

@app.route('/posts')
def posts():
    all_posts = Post.query.order_by(Post.created_at.desc()).all()
    return render_template('posts.html', posts=all_posts)

@app.route('/post/<int:post_id>')
def view_post(post_id):
    post = Post.query.get_or_404(post_id)
    # Get other posts for related posts section
    related_posts = Post.query.filter(Post.id != post_id).order_by(Post.created_at.desc()).limit(3).all()
    return render_template('post.html', post=post, related_posts=related_posts)

@app.route('/admin-login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        password = request.form.get('password')
        if password == ADMIN_PASSWORD:
            # Create session
            session_token = str(uuid.uuid4())
            expires_at = datetime.utcnow() + timedelta(hours=2)
            
            admin_session = AdminSession(
                session_token=session_token,
                expires_at=expires_at
            )
            db.session.add(admin_session)
            db.session.commit()
            
            session['admin_token'] = session_token
            flash('Login realizado com sucesso!', 'success')
            return redirect(url_for('admin_panel'))
        else:
            flash('Senha incorreta!', 'error')
    
    return render_template('admin_login.html')

@app.route('/admin')
def admin_panel():
    # Check if admin is logged in
    admin_token = session.get('admin_token')
    if not admin_token:
        return redirect(url_for('admin_login'))
    
    # Verify token
    admin_session = AdminSession.query.filter_by(session_token=admin_token).first()
    if not admin_session or admin_session.expires_at < datetime.utcnow():
        session.pop('admin_token', None)
        flash('Sessão expirada. Faça login novamente.', 'error')
        return redirect(url_for('admin_login'))
    
    properties = Property.query.order_by(Property.created_at.desc()).all()
    posts = Post.query.order_by(Post.created_at.desc()).all()
    return render_template('admin_panel.html', properties=properties, posts=posts)

@app.route('/admin/add-property', methods=['POST'])
def add_property():
    # Check admin authentication
    admin_token = session.get('admin_token')
    if not admin_token:
        return redirect(url_for('admin_login'))
    
    admin_session = AdminSession.query.filter_by(session_token=admin_token).first()
    if not admin_session or admin_session.expires_at < datetime.utcnow():
        session.pop('admin_token', None)
        return redirect(url_for('admin_login'))
    
    title = request.form.get('title')
    description = request.form.get('description')
    property_type = request.form.get('property_type')
    price = request.form.get('price')
    location = request.form.get('location')
    featured = 'featured' in request.form
    
    video_path = None
    
    # Handle video upload
    if 'video' in request.files:
        file = request.files['video']
        if file and file.filename and file.filename != '' and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            unique_filename = f"{uuid.uuid4()}_{filename}"
            video_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
            file.save(video_path)
    
    # Create property first
    property_obj = Property(
        title=title,
        description=description,
        video_path=video_path,
        property_type=property_type,
        price=price,
        location=location,
        featured=featured
    )
    
    db.session.add(property_obj)
    db.session.commit()
    
    # Handle multiple image uploads
    uploaded_images = []
    if 'images' in request.files:
        files = request.files.getlist('images')
        for i, file in enumerate(files[:10]):  # Limit to 10 images
            if file and file.filename and file.filename != '' and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                unique_filename = f"{uuid.uuid4()}_{filename}"
                image_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
                file.save(image_path)
                
                # Create PropertyImage record
                property_image = PropertyImage(
                    property_id=property_obj.id,
                    image_path=image_path,
                    is_primary=(i == 0),  # First image is primary
                    order_index=i
                )
                db.session.add(property_image)
                uploaded_images.append(image_path)
        
        # Set first image as main image for backward compatibility
        if uploaded_images:
            property_obj.image_path = uploaded_images[0]
            db.session.commit()
    
    flash('Propriedade adicionada com sucesso!', 'success')
    return redirect(url_for('admin_panel'))

@app.route('/admin/delete-property/<int:property_id>')
def delete_property(property_id):
    # Check admin authentication
    admin_token = session.get('admin_token')
    if not admin_token:
        return redirect(url_for('admin_login'))
    
    admin_session = AdminSession.query.filter_by(session_token=admin_token).first()
    if not admin_session or admin_session.expires_at < datetime.utcnow():
        session.pop('admin_token', None)
        return redirect(url_for('admin_login'))
    
    property_obj = Property.query.get_or_404(property_id)
    
    # Delete associated files
    if property_obj.image_path and os.path.exists(property_obj.image_path):
        os.remove(property_obj.image_path)
    if property_obj.video_path and os.path.exists(property_obj.video_path):
        os.remove(property_obj.video_path)
    
    db.session.delete(property_obj)
    db.session.commit()
    
    flash('Propriedade removida com sucesso!', 'success')
    return redirect(url_for('admin_panel'))

@app.route('/admin/logout')
def admin_logout():
    admin_token = session.get('admin_token')
    if admin_token:
        AdminSession.query.filter_by(session_token=admin_token).delete()
        db.session.commit()
        session.pop('admin_token', None)
    
    flash('Logout realizado com sucesso!', 'success')
    return redirect(url_for('index'))

@app.route('/admin/add-post', methods=['POST'])
def add_post():
    # Check admin authentication
    admin_token = session.get('admin_token')
    if not admin_token:
        return redirect(url_for('admin_login'))
    
    admin_session = AdminSession.query.filter_by(session_token=admin_token).first()
    if not admin_session or admin_session.expires_at < datetime.utcnow():
        session.pop('admin_token', None)
        return redirect(url_for('admin_login'))
    
    title = request.form.get('title')
    content = request.form.get('content')
    featured = 'featured' in request.form
    
    image_path = None
    video_path = None
    
    # Handle file uploads
    if 'image' in request.files:
        file = request.files['image']
        if file and file.filename and file.filename != '' and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            unique_filename = f"{uuid.uuid4()}_{filename}"
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
            file.save(image_path)
    
    if 'video' in request.files:
        file = request.files['video']
        if file and file.filename and file.filename != '' and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            unique_filename = f"{uuid.uuid4()}_{filename}"
            video_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
            file.save(video_path)
    
    post_obj = Post(
        title=title,
        content=content,
        image_path=image_path,
        video_path=video_path,
        featured=featured
    )
    
    db.session.add(post_obj)
    db.session.commit()
    
    flash('Post adicionado com sucesso!', 'success')
    return redirect(url_for('admin_panel'))

@app.route('/admin/delete-post/<int:post_id>')
def delete_post(post_id):
    # Check admin authentication
    admin_token = session.get('admin_token')
    if not admin_token:
        return redirect(url_for('admin_login'))
    
    admin_session = AdminSession.query.filter_by(session_token=admin_token).first()
    if not admin_session or admin_session.expires_at < datetime.utcnow():
        session.pop('admin_token', None)
        return redirect(url_for('admin_login'))
    
    post_obj = Post.query.get_or_404(post_id)
    
    # Delete associated files
    if post_obj.image_path and os.path.exists(post_obj.image_path):
        os.remove(post_obj.image_path)
    if post_obj.video_path and os.path.exists(post_obj.video_path):
        os.remove(post_obj.video_path)
    
    db.session.delete(post_obj)
    db.session.commit()
    
    flash('Post removido com sucesso!', 'success')
    return redirect(url_for('admin_panel'))

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    from flask import send_from_directory
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/chatbot/message', methods=['POST'])
def chatbot_message():
    try:
        data = request.get_json()
        message = data.get('message', '')
        user_name = data.get('user_name', '')
        user_phone = data.get('user_phone', '')
        
        if not openai_client:
            return jsonify({'response': 'Desculpe, o sistema de chat está temporariamente indisponível.'})
        
        # Create context about the real estate company
        context = """
        Você é a assistente virtual da Maeva Investimentos Imobiliários, uma consultoria imobiliária de São Paulo especializada em imóveis de médio e alto padrão.

        Informações da empresa:
        - Especializada em imóveis de alto padrão em São Paulo
        - Mais de 13 anos de experiência no mercado
        - Consultora principal: Rose Ventura
        - Regiões de atuação: Jardins, Vila Olímpia, Itaim Bibi, Moema, Brooklin, Pinheiros, Vila Madalena, Morumbi
        - Tipos de imóveis: Apartamentos, casas, coberturas, imóveis comerciais
        - Serviços: Consultoria especializada, assessoria para investidores, acompanhamento completo do processo
        - Contato: WhatsApp (11) 98755-7913, Instagram @Roseaventura
        
        Seja sempre cordial, profissional e útil. Forneça informações sobre imóveis, bairros de São Paulo, processo de compra, documentação, financiamento imobiliário e investimentos. Sempre incentive o contato direto para agendamento de visitas.
        """
        
        # the newest OpenAI model is "gpt-5" which was released August 7, 2025.
        # do not change this unless explicitly requested by the user
        response = openai_client.chat.completions.create(
            model="gpt-5",
            messages=[
                {"role": "system", "content": context},
                {"role": "user", "content": message}
            ],
            max_tokens=300,
            temperature=0.7
        )
        
        bot_response = response.choices[0].message.content
        
        # Save conversation to database
        conversation = ChatbotConversation(
            name=user_name,
            phone=user_phone,
            message=message,
            bot_response=bot_response
        )
        
        db.session.add(conversation)
        db.session.commit()
        
        return jsonify({
            'response': bot_response,
            'conversation_id': conversation.id
        })
        
    except Exception as e:
        print(f"Chatbot error: {e}")
        return jsonify({'response': 'Desculpe, ocorreu um erro. Tente novamente ou entre em contato pelo WhatsApp (11) 98755-7913.'})

@app.route('/admin/conversations')
def admin_conversations():
    # Check admin authentication
    admin_token = session.get('admin_token')
    if not admin_token:
        return redirect(url_for('admin_login'))
    
    admin_session = AdminSession.query.filter_by(session_token=admin_token).first()
    if not admin_session or admin_session.expires_at < datetime.utcnow():
        session.pop('admin_token', None)
        return redirect(url_for('admin_login'))
    
    conversations = ChatbotConversation.query.order_by(ChatbotConversation.created_at.desc()).all()
    
    return render_template('admin_conversations.html', conversations=conversations)
