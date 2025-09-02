import os
import uuid
import json
from datetime import datetime, timedelta
from PIL import Image
from flask import render_template, request, redirect, url_for, session, flash, jsonify
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from openai import OpenAI
from app import app, db
from models import Property, Post, AdminSession, PropertyImage, ChatbotConversation

# Try to import magic with fallback
try:
    import magic
    MAGIC_AVAILABLE = True
except ImportError:
    MAGIC_AVAILABLE = False
    print("Warning: python-magic not available. File type validation will be limited.")

# File configuration - optimized for better performance
ALLOWED_IMAGE_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
ALLOWED_VIDEO_EXTENSIONS = {'mp4', 'avi', 'mov', 'webm'}
ALLOWED_EXTENSIONS = ALLOWED_IMAGE_EXTENSIONS | ALLOWED_VIDEO_EXTENSIONS

# MIME type validation for security
ALLOWED_IMAGE_MIMES = {
    'image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'image/webp'
}
ALLOWED_VIDEO_MIMES = {
    'video/mp4', 'video/avi', 'video/quicktime', 'video/webm'
}

# Optimized file size limits (reduced for better performance)
MAX_IMAGE_SIZE = 10 * 1024 * 1024  # 10MB for images
MAX_VIDEO_SIZE = 30 * 1024 * 1024  # 30MB for videos

ADMIN_PASSWORD = "4731v8"

# Initialize OpenAI
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
openai_client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def is_safe_file(file):
    """Enhanced file validation with optional MIME type checking"""
    try:
        # Check file extension first
        if not file or not file.filename:
            return False, "Nenhum arquivo selecionado"
        
        if not allowed_file(file.filename):
            return False, "Tipo de arquivo não permitido"
        
        # Get file size efficiently
        file.seek(0, 2)
        file_size = file.tell()
        file.seek(0)
        
        file_ext = file.filename.rsplit('.', 1)[1].lower()
        
        # Validate MIME type if magic is available
        if MAGIC_AVAILABLE:
            try:
                # Read first chunk to detect MIME type
                chunk = file.read(1024)
                file.seek(0)
                
                mime_type = magic.from_buffer(chunk, mime=True)
                
                # Validate MIME type matches extension
                if file_ext in ALLOWED_IMAGE_EXTENSIONS:
                    if mime_type not in ALLOWED_IMAGE_MIMES:
                        return False, f"Arquivo de imagem inválido (detectado: {mime_type})"
                elif file_ext in ALLOWED_VIDEO_EXTENSIONS:
                    if mime_type not in ALLOWED_VIDEO_MIMES:
                        return False, f"Arquivo de vídeo inválido (detectado: {mime_type})"
            except Exception as e:
                print(f"Warning: MIME type validation failed: {e}")
        
        # Check file sizes
        if file_ext in ALLOWED_IMAGE_EXTENSIONS:
            if file_size > MAX_IMAGE_SIZE:
                return False, f"Imagem muito grande. Máximo {MAX_IMAGE_SIZE // (1024*1024)}MB permitido"
        elif file_ext in ALLOWED_VIDEO_EXTENSIONS:
            if file_size > MAX_VIDEO_SIZE:
                return False, f"Vídeo muito grande. Máximo {MAX_VIDEO_SIZE // (1024*1024)}MB permitido"
        
        return True, "Arquivo válido"
    except Exception as e:
        print(f"Error validating file: {e}")
        return False, "Erro ao validar arquivo"

def compress_image(file_path, quality=85):
    """Compress image to reduce file size while maintaining quality"""
    try:
        with Image.open(file_path) as img:
            # Convert RGBA to RGB if necessary (for JPEG)
            if img.mode in ('RGBA', 'LA', 'P'):
                background = Image.new('RGB', img.size, (255, 255, 255))
                if img.mode == 'P':
                    img = img.convert('RGBA')
                background.paste(img, mask=img.split()[-1] if img.mode in ('RGBA', 'LA') else None)
                img = background
            
            # Resize if image is too large (maintain aspect ratio)
            max_size = (1920, 1080)
            if img.size[0] > max_size[0] or img.size[1] > max_size[1]:
                img.thumbnail(max_size, Image.Resampling.LANCZOS)
            
            # Save with compression
            img.save(file_path, 'JPEG', quality=quality, optimize=True)
            return True
    except Exception as e:
        print(f"Error compressing image {file_path}: {e}")
        return False

def save_uploaded_file(file, upload_folder):
    """Save uploaded file with optimization and error handling"""
    try:
        # Validate file
        is_valid, message = is_safe_file(file)
        if not is_valid:
            return None, message
        
        # Generate unique filename
        filename = secure_filename(file.filename)
        unique_filename = f"{uuid.uuid4()}_{filename}"
        file_path = os.path.join(upload_folder, unique_filename)
        
        # Save file
        file.save(file_path)
        
        # Compress image if it's an image file
        file_ext = filename.rsplit('.', 1)[1].lower()
        if file_ext in ALLOWED_IMAGE_EXTENSIONS:
            if not compress_image(file_path):
                # If compression fails, keep original but log warning
                print(f"Warning: Could not compress image {filename}")
        
        return file_path, "Upload realizado com sucesso"
    except Exception as e:
        print(f"Error saving file: {e}")
        return None, "Erro ao fazer upload do arquivo"

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
    # Add pagination for better performance
    page = request.args.get('page', 1, type=int)
    per_page = 12  # Show 12 properties per page
    properties = Property.query.order_by(Property.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False)
    return render_template('gallery.html', properties=properties)

@app.route('/contato')
def contact():
    return render_template('contact.html')

@app.route('/posts')
def posts():
    # Add pagination for better performance
    page = request.args.get('page', 1, type=int)
    per_page = 12  # Show 12 posts per page
    all_posts = Post.query.order_by(Post.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False)
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
    
    # Optimized queries - limit results for better performance
    properties = Property.query.order_by(Property.created_at.desc()).limit(20).all()
    posts = Post.query.order_by(Post.created_at.desc()).limit(20).all()
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
    
    try:
        title = request.form.get('title')
        description = request.form.get('description')
        property_type = request.form.get('property_type')
        price = request.form.get('price')
        location = request.form.get('location')
        featured = 'featured' in request.form
        
        if not title:
            flash('Título é obrigatório!', 'error')
            return redirect(url_for('admin_panel'))
        
        video_path = None
        
        # Handle video upload with new optimized system
        if 'video' in request.files:
            file = request.files['video']
            if file and file.filename:
                video_path, message = save_uploaded_file(file, app.config['UPLOAD_FOLDER'])
                if video_path is None:
                    flash(f'Erro no vídeo: {message}', 'error')
                    return redirect(url_for('admin_panel'))
                print(f"Property video uploaded successfully: {message}")
        
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
        
        # Handle multiple image uploads with new optimized system
        uploaded_images = []
        if 'images' in request.files:
            files = request.files.getlist('images')
            for i, file in enumerate(files[:10]):  # Limit to 10 images
                if file and file.filename:
                    image_path, message = save_uploaded_file(file, app.config['UPLOAD_FOLDER'])
                    if image_path is None:
                        flash(f'Erro na imagem {file.filename}: {message}', 'error')
                        return redirect(url_for('admin_panel'))
                    
                    # Create PropertyImage record
                    property_image = PropertyImage(
                        property_id=property_obj.id,
                        image_path=image_path,
                        is_primary=(i == 0),  # First image is primary
                        order_index=i
                    )
                    db.session.add(property_image)
                    uploaded_images.append(image_path)
                    print(f"Property image {i+1} uploaded successfully: {message}")
        
        # Set first image as main image for backward compatibility
        if uploaded_images:
            property_obj.image_path = uploaded_images[0]
            db.session.commit()
    
        flash('Propriedade adicionada com sucesso!', 'success')
        print(f"Property created successfully: {property_obj.id}")
        
    except Exception as e:
        print(f"Error in add_property: {e}")
        db.session.rollback()
        flash('Erro ao criar propriedade. Tente novamente.', 'error')
    
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
    
    try:
        property_obj = Property.query.get_or_404(property_id)
        
        # Delete all associated PropertyImage records and their files
        property_images = PropertyImage.query.filter_by(property_id=property_id).all()
        for img in property_images:
            # Delete the physical file
            if img.image_path and os.path.exists(img.image_path):
                try:
                    os.remove(img.image_path)
                    print(f"Deleted image file: {img.image_path}")
                except Exception as e:
                    print(f"Error deleting image file {img.image_path}: {e}")
            # Delete the database record
            db.session.delete(img)
        
        # Delete main property image file (backward compatibility)
        if property_obj.image_path and os.path.exists(property_obj.image_path):
            try:
                os.remove(property_obj.image_path)
                print(f"Deleted main property image: {property_obj.image_path}")
            except Exception as e:
                print(f"Error deleting main property image: {e}")
        
        # Delete video file
        if property_obj.video_path and os.path.exists(property_obj.video_path):
            try:
                os.remove(property_obj.video_path)
                print(f"Deleted property video: {property_obj.video_path}")
            except Exception as e:
                print(f"Error deleting property video: {e}")
        
        # Delete the property itself
        db.session.delete(property_obj)
        db.session.commit()
        
        print(f"Property {property_id} deleted successfully")
        flash('Propriedade removida com sucesso!', 'success')
        
    except Exception as e:
        print(f"Error deleting property {property_id}: {e}")
        db.session.rollback()
        flash('Erro ao excluir propriedade. Tente novamente.', 'error')
    
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
    
    try:
        title = request.form.get('title')
        content = request.form.get('content')
        featured = 'featured' in request.form
        
        if not title or not content:
            flash('Título e conteúdo são obrigatórios!', 'error')
            return redirect(url_for('admin_panel'))
        
        image_path = None
        video_path = None
        
        # Handle image upload with new optimized system
        if 'image' in request.files:
            file = request.files['image']
            if file and file.filename:
                image_path, message = save_uploaded_file(file, app.config['UPLOAD_FOLDER'])
                if image_path is None:
                    flash(f'Erro na imagem: {message}', 'error')
                    return redirect(url_for('admin_panel'))
                print(f"Post image uploaded successfully: {message}")
        
        # Handle video upload with new optimized system
        if 'video' in request.files:
            file = request.files['video']
            if file and file.filename:
                video_path, message = save_uploaded_file(file, app.config['UPLOAD_FOLDER'])
                if video_path is None:
                    flash(f'Erro no vídeo: {message}', 'error')
                    return redirect(url_for('admin_panel'))
                print(f"Post video uploaded successfully: {message}")
        
        # Create post
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
        print(f"Post created successfully: {post_obj.id}")
        
    except Exception as e:
        print(f"Error in add_post: {e}")
        db.session.rollback()
        flash('Erro ao criar post. Tente novamente.', 'error')
    
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
    
    try:
        post_obj = Post.query.get_or_404(post_id)
        
        # Delete associated files with error handling
        if post_obj.image_path and os.path.exists(post_obj.image_path):
            try:
                os.remove(post_obj.image_path)
                print(f"Deleted post image: {post_obj.image_path}")
            except Exception as e:
                print(f"Error deleting post image: {e}")
        
        if post_obj.video_path and os.path.exists(post_obj.video_path):
            try:
                os.remove(post_obj.video_path)
                print(f"Deleted post video: {post_obj.video_path}")
            except Exception as e:
                print(f"Error deleting post video: {e}")
        
        # Delete the post
        db.session.delete(post_obj)
        db.session.commit()
        
        print(f"Post {post_id} deleted successfully")
        flash('Post removido com sucesso!', 'success')
        
    except Exception as e:
        print(f"Error deleting post {post_id}: {e}")
        db.session.rollback()
        flash('Erro ao excluir post. Tente novamente.', 'error')
    
    return redirect(url_for('admin_panel'))

@app.route('/admin/edit-property/<int:property_id>')
def edit_property(property_id):
    # Check admin authentication
    admin_token = session.get('admin_token')
    if not admin_token:
        return redirect(url_for('admin_login'))
    
    admin_session = AdminSession.query.filter_by(session_token=admin_token).first()
    if not admin_session or admin_session.expires_at < datetime.utcnow():
        session.pop('admin_token', None)
        return redirect(url_for('admin_login'))
    
    property_obj = Property.query.get_or_404(property_id)
    
    # GET request - render edit form with optimized queries
    properties = Property.query.order_by(Property.created_at.desc()).limit(20).all()
    posts = Post.query.order_by(Post.created_at.desc()).limit(20).all()
    return render_template('admin_panel.html', properties=properties, posts=posts, edit_property=property_obj)

@app.route('/admin/update-property/<int:property_id>', methods=['POST'])
def update_property(property_id):
    # Check admin authentication
    admin_token = session.get('admin_token')
    if not admin_token:
        return redirect(url_for('admin_login'))
    
    admin_session = AdminSession.query.filter_by(session_token=admin_token).first()
    if not admin_session or admin_session.expires_at < datetime.utcnow():
        session.pop('admin_token', None)
        return redirect(url_for('admin_login'))
    
    try:
        property_obj = Property.query.get_or_404(property_id)
        
        # Update basic fields
        property_obj.title = request.form.get('title') or property_obj.title
        property_obj.description = request.form.get('description') or property_obj.description
        property_obj.property_type = request.form.get('property_type') or property_obj.property_type
        property_obj.price = request.form.get('price') or property_obj.price
        property_obj.location = request.form.get('location') or property_obj.location
        property_obj.featured = 'featured' in request.form
        
        db.session.commit()
        flash('Propriedade atualizada com sucesso!', 'success')
        print(f"Property {property_id} updated successfully")
        
    except Exception as e:
        print(f"Error updating property: {e}")
        db.session.rollback()
        flash('Erro ao atualizar propriedade. Tente novamente.', 'error')
    
    return redirect(url_for('admin_panel'))

@app.route('/admin/edit-post/<int:post_id>')
def edit_post(post_id):
    # Check admin authentication
    admin_token = session.get('admin_token')
    if not admin_token:
        return redirect(url_for('admin_login'))
    
    admin_session = AdminSession.query.filter_by(session_token=admin_token).first()
    if not admin_session or admin_session.expires_at < datetime.utcnow():
        session.pop('admin_token', None)
        return redirect(url_for('admin_login'))
    
    post_obj = Post.query.get_or_404(post_id)
    
    # GET request - render edit form with optimized queries
    properties = Property.query.order_by(Property.created_at.desc()).limit(20).all()
    posts = Post.query.order_by(Post.created_at.desc()).limit(20).all()
    return render_template('admin_panel.html', properties=properties, posts=posts, edit_post=post_obj)

@app.route('/admin/update-post/<int:post_id>', methods=['POST'])
def update_post(post_id):
    # Check admin authentication
    admin_token = session.get('admin_token')
    if not admin_token:
        return redirect(url_for('admin_login'))
    
    admin_session = AdminSession.query.filter_by(session_token=admin_token).first()
    if not admin_session or admin_session.expires_at < datetime.utcnow():
        session.pop('admin_token', None)
        return redirect(url_for('admin_login'))
    
    try:
        post_obj = Post.query.get_or_404(post_id)
        
        # Update basic fields
        post_obj.title = request.form.get('title') or post_obj.title
        post_obj.content = request.form.get('content') or post_obj.content
        post_obj.featured = 'featured' in request.form
        
        db.session.commit()
        flash('Post atualizado com sucesso!', 'success')
        print(f"Post {post_id} updated successfully")
        
    except Exception as e:
        print(f"Error updating post: {e}")
        db.session.rollback()
        flash('Erro ao atualizar post. Tente novamente.', 'error')
    
    return redirect(url_for('admin_panel'))

# Route for serving uploaded files
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    from flask import send_from_directory
    import os
    if os.path.exists(os.path.join(app.config['UPLOAD_FOLDER'], filename)):
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename)
    else:
        return "File not found", 404

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
