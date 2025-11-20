from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from datetime import datetime

app = Flask(__name__)
CORS(app)

# 👉 Utilisation de TA base déjà existante
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///MedicalAI.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# --------------------------
#       MODELS
# --------------------------

class Symptom(db.Model):
    __tablename__ = 'symptomes'
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(200), unique=True)
    description = db.Column(db.String(500))


class Disease(db.Model):
    __tablename__ = 'maladies'
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(200), unique=True)
    description = db.Column(db.String(500))
    severite = db.Column(db.String(50))


class DiseaseSymptom(db.Model):
    __tablename__ = 'maladies_symptomes'
    id = db.Column(db.Integer, primary_key=True)
    maladie_id = db.Column(db.Integer)
    symptome_id = db.Column(db.Integer)
    importance = db.Column(db.Integer)


class Precaution(db.Model):
    __tablename__ = 'precautions'
    id = db.Column(db.Integer, primary_key=True)
    maladie_id = db.Column(db.Integer)
    texte = db.Column(db.String(500))


class Consultation(db.Model):
    __tablename__ = 'consultations'
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(100))
    prenom = db.Column(db.String(100))
    date_naissance = db.Column(db.String(20))
    sexe = db.Column(db.String(10))
    telephone = db.Column(db.String(20))
    date_consultation = db.Column(db.String(30))
    symptomes = db.Column(db.String(500))
    maladie_diagnostiquee = db.Column(db.String(200))
    confiance = db.Column(db.Float)

# --------------------------------
#           API ROUTES
# --------------------------------

@app.route('/api/health')
def health():
    return jsonify({"status": "API is running"})


@app.route('/api/symptomes')
def get_symptomes():
    sympt = Symptom.query.all()
    return jsonify([{"id": s.id, "nom": s.nom, "description": s.description} for s in sympt])


@app.route('/api/maladies')
def get_maladies():
    maladies = Disease.query.all()
    results = []

    for m in maladies:
        sympt_links = DiseaseSymptom.query.filter_by(maladie_id=m.id).all()
        sympt_info = []
        for link in sympt_links:
            s = Symptom.query.get(link.symptome_id)
            if s:
                sympt_info.append({"nom": s.nom, "importance": link.importance})

        precs = Precaution.query.filter_by(maladie_id=m.id).all()

        results.append({
            "id": m.id,
            "nom": m.nom,
            "description": m.description,
            "severite": m.severite,
            "symptomes": sympt_info,
            "precautions": [p.texte for p in precs]
        })

    return jsonify(results)


@app.route('/api/consultations', methods=['POST'])
def add_consultation():
    data = request.json
    consultation = Consultation(
        nom=data.get("nom"),
        prenom=data.get("prenom"),
        date_naissance=data.get("date_naissance"),
        sexe=data.get("sexe"),
        telephone=data.get("telephone"),
        date_consultation=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    )
    db.session.add(consultation)
    db.session.commit()
    return jsonify({"message": "Consultation créée", "id": consultation.id})


@app.route('/api/diagnose', methods=['POST'])
def diagnose():
    data = request.json
    user_symptoms = data.get("symptomes", [])
    consultation_id = data.get("consultation_id")

    if not user_symptoms:
        return jsonify({"error": "Aucun symptôme saisi"}), 400

    matched = Symptom.query.filter(Symptom.nom.in_(user_symptoms)).all()
    if not matched:
        return jsonify({"error": "Aucun symptôme reconnu"}), 400

    diseases_data = []

    for disease in Disease.query.all():
        links = DiseaseSymptom.query.filter_by(maladie_id=disease.id).all()
        disease_symps = [Symptom.query.get(l.symptome_id).nom for l in links]

        match_count = len(set(user_symptoms) & set(disease_symps))
        total = len(disease_symps)
        confidence = (match_count / total) * 100 if total > 0 else 0

        if confidence > 0:
            diseases_data.append({
                "maladie": disease.nom,
                "confiance": confidence,
                "symptomes_matches": list(set(user_symptoms) & set(disease_symps)),
                "precautions": [p.texte for p in Precaution.query.filter_by(maladie_id=disease.id).all()]
            })

    diseases_data = sorted(diseases_data, key=lambda x: x["confiance"], reverse=True)

    if consultation_id:
        cons = Consultation.query.get(consultation_id)
        if cons:
            cons.symptomes = ", ".join(user_symptoms)
            if diseases_data:
                cons.maladie_diagnostiquee = diseases_data[0]["maladie"]
                cons.confiance = diseases_data[0]["confiance"]
            db.session.commit()

    return jsonify({"resultats": diseases_data})


if __name__ == '__main__':
    app.run(debug=True)
