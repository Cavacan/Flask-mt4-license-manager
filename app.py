from flask import Flask, render_template, redirect, url_for, request, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
import os

# --- 設定 ---
basedir = os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-goes-here'  # 秘密鍵を設定
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'app.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# --- データベースモデル ---
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    licenses = db.relationship('License', backref='user', lazy=True)

class EA(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    licenses = db.relationship('License', backref='ea', lazy=True)

class License(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    ea_id = db.Column(db.Integer, db.ForeignKey('ea.id'), nullable=False)

# --- ユーザーローダー ---
@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

# --- ルーティングとビュー関数 ---
@app.route('/')
def index():
    if current_user.is_authenticated:
        if current_user.is_admin:
            return redirect(url_for('admin_dashboard'))
        else:
            return redirect(url_for('user_licenses'))
    return redirect(url_for('login'))

# ログインページ
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:  # 本番環境ではハッシュ化が必要
            login_user(user)
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password')
    return render_template('login.html')

# ログアウト
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

# ユーザー画面
@app.route('/user/licenses')
@login_required
def user_licenses():
    if current_user.is_admin:
        return redirect(url_for('admin_dashboard'))
    licenses = current_user.licenses
    return render_template('user_licenses.html', licenses=licenses)

# 管理者画面
@app.route('/admin/dashboard')
@login_required
def admin_dashboard():
    if not current_user.is_admin:
        return redirect(url_for('user_licenses'))
    
    users = User.query.all()
    eas = EA.query.all()
    return render_template('admin_dashboard.html', users=users, eas=eas)

# ユーザー追加
@app.route('/admin/add_user', methods=['POST'])
@login_required
def add_user():
    if not current_user.is_admin:
        return redirect(url_for('index'))
    
    username = request.form['username']
    password = request.form['password']
    is_admin = 'is_admin' in request.form
    
    new_user = User(username=username, password=password, is_admin=is_admin)
    db.session.add(new_user)
    db.session.commit()
    return redirect(url_for('admin_dashboard'))

# ライセンス付与
@app.route('/admin/assign_license/<user_id>', methods=['POST'])
@login_required
def assign_license(user_id):
    if not current_user.is_admin:
        return redirect(url_for('index'))
    
    ea_id = request.form['ea_id']
    new_license = License(user_id=user_id, ea_id=ea_id)
    db.session.add(new_license)
    db.session.commit()
    return redirect(url_for('admin_dashboard'))


# ライセンス削除
@app.route('/admin/delete_license/<license_id>')
@login_required
def delete_license(license_id):
    if not current_user.is_admin:
        return redirect(url_for('index'))
    
    license = License.query.get(license_id)
    if license:
        db.session.delete(license)
        db.session.commit()
    return redirect(url_for('admin_dashboard'))


if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # データベースとテーブルを作成
        if not User.query.filter_by(username='admin').first():
            admin_user = User(username='admin', password='password', is_admin=True)
            db.session.add(admin_user)
            db.session.commit()
    app.run(debug=True)