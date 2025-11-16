import firebase_admin
from firebase_admin import credentials, firestore, auth, storage

cred = credentials.Certificate("firebase_config.json")
firebase_admin.initialize_app(cred, {
    'storageBucket': 'remedi_bucket1.appspot.com'
})

db = firestore.client()
bucket = storage.bucket()

# --- User Functions ---
def add_user(email, username, password):
    user_ref = db.collection("users").document(email)
    user_ref.set({
        "username": username,
        "email": email,
        "hydration_enabled": False
    })

def get_user(email):
    return db.collection("users").document(email).get().to_dict()

# --- Medicine Functions ---
def add_medicine(email, medicine_data):
    med_ref = db.collection("users").document(email).collection("medicines").document()
    med_ref.set(medicine_data)

def get_medicines(email):
    meds = db.collection("users").document(email).collection("medicines").stream()
    return [m.to_dict() for m in meds]

def update_medicine(email, med_id, data):
    db.collection("users").document(email).collection("medicines").document(med_id).update(data)
