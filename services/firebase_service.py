import firebase_admin
from firebase_admin import credentials, firestore, auth, storage
import os

cred = credentials.Certificate("firebase_config.json")
firebase_admin.initialize_app(cred)

db = firestore.client()


# --- User Functions ---
def add_user(email, username,photo_url=None):
    user_ref = db.collection("users").document(email)
    user_ref.set({
        "username": username,
        "email": email,
        "created_at": firestore.SERVER_TIMESTAMP,
        "hydration_enabled": False,
        "photo_url": photo_url
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
def update_user(email, data):
    """
    Updates an existing user document.
    :param email: The user's email (Document ID)
    :param data: A dictionary of fields to update (e.g., {'age': '20', 'gender': 'male'})
    """
    try:
        user_ref = db.collection("users").document(email)
        user_ref.update(data)
        return True
    except Exception as e:
        print(f"Error updating user {email}: {e}")
        return False