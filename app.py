from flask import Flask, request, jsonify, render_template, flash
from datetime import datetime
from crops_data import crops_data
from flask_pymongo import PyMongo
from flask_login import LoginManager, login_required, login_user, logout_user, UserMixin, current_user
from authlib.integrations.flask_client import OAuth
from os import environ as env
from dotenv import load_dotenv
import secrets
import pyotp
from flask import redirect, url_for
import uuid

load_dotenv()
app = Flask(__name__)
app.config["SECRET_KEY"] = env.get('SECRET_KEY', secrets.token_hex(16))
app.config["MONGO_URI"] = env.get('MONGO_URI', "mongodb://127.0.0.1:27017/cropdb")
mongo = PyMongo(app)
DEV_USERS = {}


def get_db():
    """Return Mongo database handle when available, else None."""
    try:
        mongo.cx.admin.command('ping')
        return mongo.db
    except Exception as e:
        app.logger.warning(f'MongoDB connection unavailable: {e}')
        return None

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

oauth = OAuth(app)
google = oauth.register(
    'google',
    client_id=env.get('GOOGLE_CLIENT_ID'),
    client_secret=env.get('GOOGLE_CLIENT_SECRET'),
    authorize_url='https://accounts.google.com/o/oauth2/auth',
    access_token_url='https://oauth2.googleapis.com/token',
    client_kwargs={'scope': 'openid email profile', 'timeout': 10},
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration'
)

class User(UserMixin):
    def __init__(self, id, email):
        self.id = id
        self.email = email

@login_manager.user_loader
def load_user(user_id):
    db = get_db()
    if db is None:
        # Local fallback users for dev mode when MongoDB is unavailable.
        if user_id in DEV_USERS:
            return User(user_id, DEV_USERS[user_id]['email'])
        return None
    try:
        user_doc = db.users.find_one({'google_id': user_id})
        if user_doc:
            return User(user_doc['google_id'], user_doc['email'])
    except Exception as e:
        app.logger.warning(f'load_user MongoDB error: {e}')
    return None

# Sample crop data based on typical ICRISAT/agricultural guidelines (N,P,K in kg/ha, adjust to g/kg if needed)
# Rules: Score based on how well inputs match optimal ranges for each crop
import os
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.tree import DecisionTreeClassifier
from sklearn.neighbors import KNeighborsClassifier
# import shap  # Comment out until SHAP installed properly
import joblib
import numpy as np

# Match model.py: 7 features (no area) + label
model_data = np.array([
    [90, 42, 43, 20.879744, 82.002744, 6.502985, 202.935536, 0],  # rice
    [117, 67, 53, 21.299189, 73.639421, 7.101541, 112.724872, 1],  # maize
    [106, 26, 70, 24.061510, 78.197878, 5.629397, 125.737907, 2],  # chickpea
    [123, 78, 58, 25.263153, 80.481718, 6.232389, 117.870064, 1],
    [90, 42, 43, 22.613353, 81.264237, 6.502985, 202.935536, 0],
    [130, 80, 60, 28, 85, 6.5, 150, 3],  # cotton
    [120, 100, 150, 18, 80, 5.5, 600, 4],  # potato
    [30, 50, 40, 30, 60, 6.5, 800, 5],  # groundnut
] * 20)

def load_or_train(path, constructor, X_ml, y_ml):
    try:
        return joblib.load(path)
    except:
        print(f'Training fresh model: {path}')
        m = constructor()
        m.fit(X_ml, y_ml)
        joblib.dump(m, path)
        return m

X_ml = model_data[:, :-1]
y_ml = model_data[:, -1].astype(int)

rf_model = load_or_train('rf_model.pkl', lambda: RandomForestClassifier(n_estimators=100, random_state=42), X_ml, y_ml)
gb_model = load_or_train('gb_model.pkl', lambda: GradientBoostingClassifier(random_state=42), X_ml, y_ml)
nb_model = load_or_train('nb_model.pkl', lambda: GaussianNB(), X_ml, y_ml)
dt_model = load_or_train('dt_model.pkl', lambda: DecisionTreeClassifier(random_state=42), X_ml, y_ml)
knn_model = load_or_train('knn_model.pkl', lambda: KNeighborsClassifier(n_neighbors=3), X_ml, y_ml)

try:
    crop_labels_ml = joblib.load('crop_labels_ml.pkl')
except:
    crop_labels_ml = ['rice', 'maize', 'chickpea', 'cotton', 'potato', 'groundnut']
    joblib.dump(crop_labels_ml, 'crop_labels_ml.pkl')

MODELS = {
    'rf': rf_model,
    'gb': gb_model,
    'nb': nb_model,
    'dt': dt_model,
    'knn': knn_model
}

# XGBoost (optional, same file as model.py)
try:
    MODELS['xgboost'] = joblib.load('crop_model.pkl')
except:
    print('XGBoost model not available')


DEFAULT_ECONOMICS = {'yield_ton_per_ha': 3.0, 'price_per_ton': 20000, 'base_cost_per_ha': 32000}
ECONOMICS_BY_CROP = {c['name'].strip().lower(): c.get('economics', {}) for c in crops_data}


def estimate_profit(crop_name, area, score, n_deficit, p_deficit, k_deficit):
    econ = {**DEFAULT_ECONOMICS, **ECONOMICS_BY_CROP.get(crop_name.lower(), {})}

    # Suitability affects likely realized yield (0.6x to 1.0x baseline).
    suitability_factor = 0.6 + (max(0, min(score, 100)) / 100.0) * 0.4
    expected_yield = econ['yield_ton_per_ha'] * suitability_factor * area
    gross_revenue = expected_yield * econ['price_per_ton']

    # Approx fertilizer correction cost from nutrient deficits.
    fert_cost = (n_deficit * 25) + (p_deficit * 55) + (k_deficit * 30)
    total_cost = (econ['base_cost_per_ha'] * area) + fert_cost

    net_profit = gross_revenue - total_cost
    return round(net_profit, 2)


def calculate_score(inputs, optimal):
    score = 0
    params = ['N', 'P', 'K', 'temp', 'humidity', 'ph', 'rainfall', 'area']
    for param in params:
        if param in optimal:
            low, high = optimal[param]
            val = inputs.get(param, 0)
            if low <= val <= high:
                score += 1
            elif val < low:
                score += (val / low) * 0.5 if low > 0 else 0
            else:
                score += (high / val) * 0.5 if val > 0 else 0
    return score / len(params) * 100

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/predict')
def predict_page():
    return render_template('predict.html')

@app.route('/history')
@login_required
def history():
    hist = []
    db = get_db()
    if db is None:
        flash('MongoDB is not connected. Start MongoDB to view history.', 'error')
        return render_template('history.html', history=hist)
    if current_user.is_authenticated:
        try:
            hist = list(db.history.find({'user_id': current_user.id}).sort('timestamp', -1).limit(20))
        except Exception as e:
            flash(f'Could not load history: {e}', 'error')
    return render_template('history.html', history=hist)

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/auth/google')
def google_login():
    if not env.get('GOOGLE_CLIENT_ID') or not env.get('GOOGLE_CLIENT_SECRET'):
        flash('Google login is not configured. Use quick login with email below.', 'error')
        return redirect(url_for('login'))
    redirect_uri = url_for('auth_callback', _external=True)
    return google.authorize_redirect(redirect_uri)

@app.route('/auth/google/callback')
def auth_callback():
    db = get_db()

    try:
        token = google.authorize_access_token()
    except Exception as e:
        flash(f'Google authentication failed: {e}', 'error')
        return redirect(url_for('login'))

    # Try multiple ways to retrieve userinfo (authlib versions vary)
    userinfo = None
    try:
        userinfo = token.get('userinfo')
    except Exception:
        pass
    if not userinfo:
        try:
            resp = google.get('https://openidconnect.googleapis.com/v1/userinfo')
            userinfo = resp.json()
        except Exception:
            try:
                userinfo = google.parse_id_token(token, nonce=None)
            except Exception as e:
                flash(f'Failed to retrieve user info from Google: {e}', 'error')
                return redirect(url_for('login'))

    google_id = userinfo.get('sub')
    email = userinfo.get('email')
    if not google_id or not email:
        flash('Could not retrieve required account information from Google.', 'error')
        return redirect(url_for('login'))

    # Save basic user info
    if db is not None:
        try:
            db.users.update_one(
                {'google_id': google_id},
                {'$set': {'email': email, 'last_login': datetime.now()}},
                upsert=True
            )
        except Exception as e:
            flash(f'Database warning: could not save user session ({e}).', 'error')
    else:
        # Fallback login path when DB is down.
        DEV_USERS[google_id] = {'email': email, 'last_login': datetime.now()}
        login_user(User(google_id, email))
        flash('Logged in without database persistence (MongoDB unavailable).', 'warning')
        return redirect(url_for('home'))

    return redirect(url_for('otp_setup', google_id=google_id, email=email))

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route('/otp-setup/<google_id>')
def otp_setup(google_id):
    db = get_db()
    if db is None:
        flash('MongoDB is not connected. Please start MongoDB and try login again.', 'error')
        return redirect(url_for('login'))

    email_fallback = request.args.get('email')
    try:
        user_doc = db.users.find_one({'google_id': google_id})
        if not user_doc or 'otp_secret' not in user_doc:
            otp_secret = pyotp.random_base32()
            # Upsert so the document is created even if the user is missing
            db.users.update_one(
                {'google_id': google_id},
                {'$set': {
                    'google_id': google_id,
                    'otp_secret': otp_secret,
                    'email': user_doc.get('email') if user_doc else (email_fallback or 'unknown@example.com')
                }},
                upsert=True
            )
            user_doc = db.users.find_one({'google_id': google_id})

        if not user_doc:
            flash('User record could not be created. Please check the database connection.', 'error')
            return redirect(url_for('login'))

        email = user_doc.get('email') or email_fallback or 'unknown@example.com'
        totp_uri = pyotp.totp.TOTP(user_doc['otp_secret']).provisioning_uri(
            name=email, issuer_name='CropRec AI'
        )
        return render_template(
            'otp.html',
            user_id=google_id,
            totp_uri=totp_uri,
            otp_secret=user_doc['otp_secret']
        )
    except Exception as e:
        flash(f'OTP setup failed: {e}', 'error')
        return redirect(url_for('login'))

@app.route('/otp-verify', methods=['POST'])
def otp_verify():
    google_id = request.form.get('user_id')
    otp_code = (request.form.get('otp') or '').strip().replace(' ', '')

    if not google_id or not otp_code:
        flash('Missing OTP or user information.', 'error')
        return redirect(url_for('login'))

    db = get_db()
    if db is None:
        flash('MongoDB is not connected. Please start MongoDB and try login again.', 'error')
        return redirect(url_for('login'))

    try:
        user_doc = db.users.find_one({'google_id': google_id})
    except Exception as e:
        flash(f'Database error during login: {e}', 'error')
        return redirect(url_for('login'))

    if not user_doc:
        flash('User not found. Please restart the login process.', 'error')
        return redirect(url_for('login'))

    if 'otp_secret' not in user_doc:
        flash('OTP is not set for this account. Please scan QR again.', 'error')
        return redirect(url_for('otp_setup', google_id=google_id, email=user_doc.get('email')))

    # valid_window=1 allows one 30-second time step drift.
    totp = pyotp.TOTP(user_doc['otp_secret'])
    if totp.verify(otp_code, valid_window=1):
        user = User(google_id, user_doc['email'])
        login_user(user)
        return redirect(url_for('home'))

    flash('Invalid OTP. Check device time sync and try again.', 'error')
    return redirect(url_for('otp_setup', google_id=google_id))


@app.route('/login/local', methods=['POST'])
def local_login():
    email = (request.form.get('email') or '').strip().lower()
    if not email or '@' not in email:
        flash('Enter a valid email for quick login.', 'error')
        return redirect(url_for('login'))

    user_id = f'local-{uuid.uuid4().hex[:10]}'
    db = get_db()
    if db is not None:
        try:
            db.users.update_one(
                {'google_id': user_id},
                {'$set': {'email': email, 'last_login': datetime.now(), 'is_local_login': True}},
                upsert=True
            )
        except Exception as e:
            app.logger.warning(f'Local login DB write failed: {e}')
    DEV_USERS[user_id] = {'email': email, 'last_login': datetime.now()}
    login_user(User(user_id, email))
    flash('Logged in successfully.', 'success')
    return redirect(url_for('home'))

@app.route('/predict', methods=['POST'])
def predict():
    db = get_db()

    data = request.json
    n = float(data.get('N', 0))
    p = float(data.get('P', 0))
    k = float(data.get('K', 0))
    temp = float(data.get('temperature', 0))
    humidity = float(data.get('humidity', 0))
    ph = float(data.get('ph', 0))
    rainfall = float(data.get('rainfall', 0))
    area = float(data.get('area', 1.0))
    location = data.get('location', 'Unknown')
    
    # ML prediction
    model_key = data.get('model', 'rf')
    selected_model = MODELS.get(model_key, rf_model)
    if selected_model is None:
        selected_model = rf_model

    input_features = np.array([[n, p, k, temp, humidity, ph, rainfall]])  # 7 features to match model
    probs = selected_model.predict_proba(input_features)[0]
    
    # Location filter for rule-based
    region_crops = [c for c in crops_data if location.lower() in c['name'].lower() or len(c.get('regions', [])) == 0]
    if not region_crops:
        region_crops = crops_data
    
    # ML top recommendations
    top_indices = np.argsort(probs)[::-1]
    top_recs = []
    top_explain = {'N': 0.1, 'P': 0.05, 'K': 0.2, 'Temp': 0.15, 'Humidity': 0.1, 'pH': 0.05, 'Rainfall': 0.25}
    allowed_names = {c['name'].strip().lower() for c in crops_data}

    for idx in top_indices:
        if idx >= len(crop_labels_ml):
            continue
        crop_name = str(crop_labels_ml[idx]).strip()
        if crop_name.lower() not in allowed_names:
            continue
        score = probs[idx] * 100
        
        # Fertilizer rec
        n_deficit = max(0, 100 - n) * area
        p_deficit = max(0, 50 - p) * area
        k_deficit = max(0, 80 - k) * area
        fert_type = 'NPK 10-26-26' if p_deficit > n_deficit and p_deficit > k_deficit else 'Urea (46-0-0)' if n_deficit > p_deficit and n_deficit > k_deficit else 'MOP (0-0-60)'
        fert_qty = round((n_deficit * 0.046 + p_deficit * 0.26 + k_deficit * 0.6) / 100 * area, 1)
        
        next_crop = 'Wheat' if 'rice' in crop_name.lower() else 'Maize' if 'cotton' in crop_name.lower() else 'Rice'
        water_usage = 5000 * area if 'rice' in crop_name.lower() else 3000 * area
        env_score = 8 if crop_name.lower() in ['chickpea', 'groundnut'] else 6 if 'maize' in crop_name.lower() else 4
        top_explain_str = '; '.join([f'{k}: {v:.2f}' for k,v in sorted(top_explain.items(), key=lambda x: x[1], reverse=True)[:3]])
        top_recs.append({
            'name': crop_name.title(), 
            'score': round(score, 2), 
            'suitability': f'Fert: {fert_type} {fert_qty}kg/ha | Next: {next_crop}',
            'water': round(water_usage), 'env_score': env_score, 'shap': top_explain_str,
            'estimated_profit': estimate_profit(crop_name, area, score, n_deficit, p_deficit, k_deficit)
        })
        if len(top_recs) == 3:
            break

    if not top_recs:
        for rr in sorted([
            {'name': c['name'], 'score': calculate_score({'N': n, 'P': p, 'K': k, 'temp': temp, 'humidity': humidity, 'ph': ph, 'rainfall': rainfall, 'area': area}, c['optimal'])}
            for c in crops_data
        ], key=lambda x: x['score'], reverse=True)[:3]:
            top_recs.append({
                'name': rr['name'],
                'score': round(rr['score'], 2),
                'suitability': f'ML fallback | Fert: Balanced NPK as per soil test | Next: Rotate with legumes',
                'water': round(3000 * area),
                'env_score': 6,
                'shap': 'Fallback recommendation',
                'estimated_profit': estimate_profit(rr['name'], area, rr['score'], 0, 0, 0)
            })
    
    avg_profit = sum(r.get('estimated_profit', 0) for r in top_recs) / len(top_recs) if top_recs else 0
    
    # Rule-based recs
    inputs = {'N': n, 'P': p, 'K': k, 'temp': temp, 'humidity': humidity, 'ph': ph, 'rainfall': rainfall, 'area': area}
    rule_recs = sorted([
        {'name': c['name'], 'score': calculate_score(inputs, c['optimal']), 'suitability': c['suitability'] + f' ({location})'} 
        for c in region_crops
    ], key=lambda x: x['score'], reverse=True)[:3]
    
    # Save to history (logged in users only)
    try:
        if current_user.is_authenticated and db is not None:
            prediction_doc = {
                'user_id': current_user.id,
                'timestamp': datetime.now(),
                'n': n, 'p': p, 'k': k, 'temp': temp, 'humidity': humidity, 
                'ph': ph, 'rainfall': rainfall, 'area': area, 'location': location,
                'ml_recommendations': top_recs,
                'rule_recommendations': rule_recs
            }
            db.history.insert_one(prediction_doc)
    except Exception as e:
        print(f"History save failed: {e}")

    return jsonify({
        'ml_recommendations': top_recs, 
        'rule_recommendations': rule_recs, 
        'avg_profit_estimate': round(avg_profit, 2)
    })


if __name__ == '__main__':
    # Production: debug=False, use gunicorn for production deployments
    app.run(host='0.0.0.0', port=5000)
