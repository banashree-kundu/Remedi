from flask import Flask, request, jsonify, session, render_template, redirect, url_for, flash
from services import firebase_service , upload
from firebase_admin import auth
import os
import dotenv
from werkzeug.utils import secure_filename

# Load environment variables from .env file
dotenv.load_dotenv()
# Initialize Flask
app = Flask(__name__)
app.secret_key = "supersecretkey"  # change this before deployment

# Routes
@app.route('/')
def home():
    if 'user' in session:
       
        return render_template("home.html", user=session['user'])

    return render_template("home.html")
@app.route('/about')
def about():
    return render_template("aboutus.html",user=session['user'] if 'user' in session else None)
@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect(url_for('getstarted'))
    
    return render_template("dashboard.html", user=session['user'])
@app.route('/profile')
def profile():
    if 'user' not in session:
        return redirect(url_for('getstarted'))
    
    email = session['user']['email']
    user_data = firebase_service.get_user(email)
    
    # Update session while we are here to keep it fresh
    if user_data:
        session['user'] = user_data
    return render_template("profilepage_copy.html", user=user_data)    
    #return render_template("profilepage_copy.html", user=session['user'])    
@app.route('/update_profile', methods=['POST'])
def update_profile():
    if 'user' not in session:
        return redirect('/')

    print("--- UPDATE PROFILE STARTED ---") # Debug 1

    email = session['user']['email']
    
    # 1. Collect Text Data
    updates = {
        "username": request.form.get('username'),
        "age": request.form.get('age'),
        "gender": request.form.get('gender'),
        "emergency_contact": request.form.get('emergency_contact')
    }

    # 2. Check for File
    print(f"Files in request: {request.files}") # Debug 2
    
    if 'profile_pic' in request.files:
        
        profile_pic = request.files.get("profile_pic")

        if profile_pic and profile_pic.filename:
            filename = secure_filename(profile_pic.filename)

            # READ THE BYTES HERE SAFEL

            # UPLOAD TO IMAGEKIT
            try:
                image_url = upload.upload_document(profile_pic, filename)
                updates["photo_url"] = image_url
            except Exception as e:
                print("ImageKit upload failed:", e)
                flash("Profile picture could not be uploaded.")
                return redirect("/profile")
    
    # 3. Update Firestore
    firebase_service.update_user(email, updates)

    # 4. Refresh Session
    updated_user = firebase_service.get_user(email)
    session['user'] = updated_user
    session.modified = True
    
    print("--- UPDATE FINISHED ---")
    return redirect('/profile')



@app.route('/getstarted')
def getstarted():
    return render_template("getstarted.html")
# ---------- EMAIL LOGIN (PYTHON ONLY) ----------

@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    id_token = data.get("idToken")

    if not id_token:
        return jsonify({"success": False, "error": "Missing token"}), 400

    try:
        decoded = auth.verify_id_token(id_token)
    except Exception as e:
        print("Token verification error:", e)
        return jsonify({"success": False, "error": "Invalid token"}), 401

    email = decoded.get("email")
    name = decoded.get("name") or email.split("@")[0]
    uid = decoded.get("uid")

    # Check / create user document in Firestore (no password)
    user = firebase_service.get_user(email)
    if not user:
        firebase_service.add_user(email=email, username=name)
        user_data = {"email": email, "username": name, "photo_url": decoded.get("picture", "https://ik.imagekit.io/RemediRX/pngwing.com.png?updatedAt=1764494288724")}

    session["user"] = user_data
    return jsonify({"success": True})


# ---------- GOOGLE LOGIN (CALLED BY JS) ----------

@app.route("/google-login", methods=["POST"])
def google_login():
    data = request.get_json()
    id_token = data.get("idToken")

    if not id_token:
        return jsonify({"success": False, "error": "Missing token"}), 400

    try:
        decoded = auth.verify_id_token(id_token)
    except Exception as e:
        print("Token verification error:", e)
        return jsonify({"success": False, "error": "Invalid token"}), 401

    email = decoded.get("email")
    name = decoded.get("name") or email.split("@")[0]

    # Check if user exists in Firestore; if not, create
    user_data = firebase_service.get_user(email)
    if not user_data:
        photo=decoded.get("picture", "https://ik.imagekit.io/RemediRX/pngwing.com.png?updatedAt=1764494288724")
        firebase_service.add_user(email=email, username=name,photo_url=photo)
        user_data = {"email": email, "username": name, "photo_url": photo}

    session["user"] = user_data    

    return jsonify({"success": True})

@app.route('/api/get_firebase_config', methods=['GET'])
def get_firebase_config():
    firebase_config = {
        "apiKey": os.getenv("FIREBASE_API_KEY"),
        "authDomain": os.getenv("FIREBASE_AUTH_DOMAIN"),
        "projectId": os.getenv("FIREBASE_PROJECT_ID"),
        "storageBucket": os.getenv("FIREBASE_STORAGE_BUCKET"),
        "messagingSenderId": os.getenv("FIREBASE_MESSAGING_SENDER_ID"),
        "appId": os.getenv("FIREBASE_APP_ID"),
    }
    return jsonify(firebase_config)
@app.route('/api/upload_image', methods=['POST'])
def upload_image():
    if 'user' not in session:
        return jsonify({"success": False, "error": "Unauthorized"}), 401

    if 'image' not in request.files:
        return jsonify({"success": False, "error": "No image provided"}), 400

    image = request.files['image']

    # Use the same helper as profile upload:
    from werkzeug.utils import secure_filename
    filename = secure_filename(image.filename)

    image_url = upload.upload_document(image, filename)  # ✅ pass file object + name

    if not image_url:
        return jsonify({"success": False, "error": "Upload to ImageKit failed"}), 500

    return jsonify({"success": True, "image_url": image_url})




@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect('/')


if __name__ == '__main__':
    app.run(debug=True)
