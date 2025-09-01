import os
import uuid
from datetime import datetime, timedelta
from flask import render_template, request, redirect, url_for, session, flash, jsonify
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from app import app, db
from models import Property, AdminSession

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'mp4', 'avi', 'mov'}
ADMIN_PASSWORD = "4731v8"

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    # Get featured properties for homepage
    featured_properties = Property.query.filter_by(featured=True).limit(6).all()
    return render_template('index.html', properties=featured_properties)

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
    return render_template('admin_panel.html', properties=properties)

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
    
    image_path = None
    video_path = None
    
    # Handle file uploads
    if 'image' in request.files:
        file = request.files['image']
        if file and file.filename != '' and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            unique_filename = f"{uuid.uuid4()}_{filename}"
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
            file.save(image_path)
    
    if 'video' in request.files:
        file = request.files['video']
        if file and file.filename != '' and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            unique_filename = f"{uuid.uuid4()}_{filename}"
            video_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
            file.save(video_path)
    
    property_obj = Property(
        title=title,
        description=description,
        image_path=image_path,
        video_path=video_path,
        property_type=property_type,
        price=price,
        location=location,
        featured=featured
    )
    
    db.session.add(property_obj)
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

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    from flask import send_from_directory
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)
