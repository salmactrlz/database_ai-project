# test_client.py - Script pour tester l'API
import requests
import json
from datetime import datetime

BASE_URL = 'http://localhost:5000/api'

def print_response(title, response):
    """Afficher une réponse formatée"""
    print(f"\n{'='*60}")
    print(f"📋 {title}")
    print(f"{'='*60}")
    print(f"Status Code: {response.status_code}")
    print(f"Response:\n{json.dumps(response.json(), indent=2, ensure_ascii=False)}")

def test_system():
    """Tester toutes les fonctionnalités du système"""
    
    print("🏥 Test du Système de Diagnostic Médical")
    print("="*60)
    
    # 1. Vérifier la santé du serveur
    print("\n1️⃣ Test de santé du serveur...")
    response = requests.get(f'{BASE_URL}/health')
    print_response("Health Check", response)
    
    # 2. Créer un patient
    print("\n2️⃣ Création d'un nouveau patient...")
    patient_data = {
        'nom': 'Dupont',
        'prenom': 'Marie',
        'date_naissance': '1985-03-15',
        'sexe': 'F',
        'telephone': '0612345678',
        'email': 'marie.dupont@email.com',
        'allergies': ['pénicilline'],
        'antecedents': ['asthme']
    }
    response = requests.post(f'{BASE_URL}/patients', json=patient_data)
    print_response("Création Patient", response)
    patient_id = response.json()['patient']['id']
    
    # 3. Récupérer tous les patients
    print("\n3️⃣ Récupération de tous les patients...")
    response = requests.get(f'{BASE_URL}/patients')
    print_response("Liste des Patients", response)
    
    # 4. Enregistrer des symptômes
    print("\n4️⃣ Enregistrement des symptômes...")
    symptoms_data = {
        'patient_id': patient_id,
        'symptoms': ['fièvre', 'toux', 'fatigue', 'maux de tête'],
        'severity': {
            'fièvre': 'élevée',
            'toux': 'modérée',
            'fatigue': 'élevée',
            'maux de tête': 'modérée'
        },
        'duration': '3 jours',
        'notes': 'Symptômes apparus progressivement'
    }
    response = requests.post(f'{BASE_URL}/symptoms', json=symptoms_data)
    print_response("Enregistrement Symptômes", response)
    
    # 5. Générer un diagnostic
    print("\n5️⃣ Génération du diagnostic...")
    diagnosis_data = {
        'patient_id': patient_id,
        'symptoms': ['fièvre', 'toux', 'fatigue', 'maux de tête', 'douleurs musculaires']
    }
    response = requests.post(f'{BASE_URL}/diagnose', json=diagnosis_data)
    print_response("Diagnostic Généré", response)
    
    # 6. Test avec symptômes COVID-19
    print("\n6️⃣ Test diagnostic COVID-19...")
    covid_symptoms = {
        'patient_id': patient_id,
        'symptoms': ['fièvre', 'toux sèche', 'fatigue', 'perte goût', 'difficultés respiratoires']
    }
    response = requests.post(f'{BASE_URL}/diagnose', json=covid_symptoms)
    print_response("Diagnostic COVID", response)
    
    # 7. Récupérer l'historique du patient
    print("\n7️⃣ Récupération de l'historique complet...")
    response = requests.get(f'{BASE_URL}/history/patient/{patient_id}')
    print_response("Historique Patient", response)
    
    # 8. Obtenir les statistiques
    print("\n8️⃣ Statistiques du système...")
    response = requests.get(f'{BASE_URL}/stats')
    print_response("Statistiques", response)
    
    # 9. Créer un deuxième patient
    print("\n9️⃣ Création d'un second patient...")
    patient2_data = {
        'nom': 'Martin',
        'prenom': 'Jean',
        'date_naissance': '1990-07-22',
        'sexe': 'M',
        'telephone': '0698765432',
        'email': 'jean.martin@email.com',
        'allergies': [],
        'antecedents': ['hypertension']
    }
    response = requests.post(f'{BASE_URL}/patients', json=patient2_data)
    print_response("Création Patient 2", response)
    patient2_id = response.json()['patient']['id']
    
    # 10. Test diagnostic gastro-entérite
    print("\n🔟 Test diagnostic gastro-entérite...")
    gastro_symptoms = {
        'patient_id': patient2_id,
        'symptoms': ['diarrhée', 'vomissements', 'douleurs abdominales', 'nausées']
    }
    response = requests.post(f'{BASE_URL}/diagnose', json=gastro_symptoms)
    print_response("Diagnostic Gastro", response)
    
    print("\n" + "="*60)
    print("✅ Tests terminés avec succès!")
    print("="*60)

def demo_interactive():
    """Mode interactif pour tester l'API"""
    print("\n🏥 Mode Interactif - Système de Diagnostic")
    print("="*60)
    
    while True:
        print("\n📋 Menu:")
        print("1. Créer un patient")
        print("2. Enregistrer des symptômes")
        print("3. Générer un diagnostic")
        print("4. Voir l'historique d'un patient")
        print("5. Voir les statistiques")
        print("6. Quitter")
        
        choice = input("\nChoisir une option (1-6): ")
        
        if choice == '1':
            print("\n--- Création d'un patient ---")
            nom = input("Nom: ")
            prenom = input("Prénom: ")
            date_naissance = input("Date de naissance (YYYY-MM-DD): ")
            sexe = input("Sexe (M/F): ")
            
            patient_data = {
                'nom': nom,
                'prenom': prenom,
                'date_naissance': date_naissance,
                'sexe': sexe
            }
            
            response = requests.post(f'{BASE_URL}/patients', json=patient_data)
            print_response("Patient créé", response)
            
        elif choice == '2':
            patient_id = input("ID du patient: ")
            symptoms = input("Symptômes (séparés par des virgules): ").split(',')
            symptoms = [s.strip() for s in symptoms]
            
            symptoms_data = {
                'patient_id': patient_id,
                'symptoms': symptoms
            }
            
            response = requests.post(f'{BASE_URL}/symptoms', json=symptoms_data)
            print_response("Symptômes enregistrés", response)
            
        elif choice == '3':
            patient_id = input("ID du patient (optionnel): ")
            symptoms = input("Symptômes (séparés par des virgules): ").split(',')
            symptoms = [s.strip() for s in symptoms]
            
            diagnosis_data = {
                'symptoms': symptoms
            }
            if patient_id:
                diagnosis_data['patient_id'] = patient_id
            
            response = requests.post(f'{BASE_URL}/diagnose', json=diagnosis_data)
            print_response("Diagnostic", response)
            
        elif choice == '4':
            patient_id = input("ID du patient: ")
            response = requests.get(f'{BASE_URL}/history/patient/{patient_id}')
            print_response("Historique", response)
            
        elif choice == '5':
            response = requests.get(f'{BASE_URL}/stats')
            print_response("Statistiques", response)
            
        elif choice == '6':
            print("\n👋 Au revoir!")
            break
        
        else:
            print("❌ Option invalide")

if __name__ == '__main__':
    import sys
    
    print("🏥 Client de Test - Système de Diagnostic Médical")
    print("="*60)
    print("\nAssurez-vous que le serveur Flask est démarré (python app.py)")
    print("\nModes disponibles:")
    print("1. Test automatique complet")
    print("2. Mode interactif")
    
    mode = input("\nChoisir le mode (1 ou 2): ")
    
    try:
        if mode == '1':
            test_system()
        elif mode == '2':
            demo_interactive()
        else:
            print("Mode invalide")
    except requests.exceptions.ConnectionError:
        print("\n❌ Erreur: Impossible de se connecter au serveur")
        print("Assurez-vous que le serveur Flask est démarré sur http://localhost:5000")# test_client.py - Script pour tester l'API
import requests
import json
from datetime import datetime

BASE_URL = 'http://localhost:5000/api'

def print_response(title, response):
    """Afficher une réponse formatée"""
    print(f"\n{'='*60}")
    print(f"📋 {title}")
    print(f"{'='*60}")
    print(f"Status Code: {response.status_code}")
    print(f"Response:\n{json.dumps(response.json(), indent=2, ensure_ascii=False)}")

def test_system():
    """Tester toutes les fonctionnalités du système"""
    
    print("🏥 Test du Système de Diagnostic Médical")
    print("="*60)
    
    # 1. Vérifier la santé du serveur
    print("\n1️⃣ Test de santé du serveur...")
    response = requests.get(f'{BASE_URL}/health')
    print_response("Health Check", response)
    
    # 2. Créer un patient
    print("\n2️⃣ Création d'un nouveau patient...")
    patient_data = {
        'nom': 'Dupont',
        'prenom': 'Marie',
        'date_naissance': '1985-03-15',
        'sexe': 'F',
        'telephone': '0612345678',
        'email': 'marie.dupont@email.com',
        'allergies': ['pénicilline'],
        'antecedents': ['asthme']
    }
    response = requests.post(f'{BASE_URL}/patients', json=patient_data)
    print_response("Création Patient", response)
    patient_id = response.json()['patient']['id']
    
    # 3. Récupérer tous les patients
    print("\n3️⃣ Récupération de tous les patients...")
    response = requests.get(f'{BASE_URL}/patients')
    print_response("Liste des Patients", response)
    
    # 4. Enregistrer des symptômes
    print("\n4️⃣ Enregistrement des symptômes...")
    symptoms_data = {
        'patient_id': patient_id,
        'symptoms': ['fièvre', 'toux', 'fatigue', 'maux de tête'],
        'severity': {
            'fièvre': 'élevée',
            'toux': 'modérée',
            'fatigue': 'élevée',
            'maux de tête': 'modérée'
        },
        'duration': '3 jours',
        'notes': 'Symptômes apparus progressivement'
    }
    response = requests.post(f'{BASE_URL}/symptoms', json=symptoms_data)
    print_response("Enregistrement Symptômes", response)
    
    # 5. Générer un diagnostic
    print("\n5️⃣ Génération du diagnostic...")
    diagnosis_data = {
        'patient_id': patient_id,
        'symptoms': ['fièvre', 'toux', 'fatigue', 'maux de tête', 'douleurs musculaires']
    }
    response = requests.post(f'{BASE_URL}/diagnose', json=diagnosis_data)
    print_response("Diagnostic Généré", response)
    
    # 6. Test avec symptômes COVID-19
    print("\n6️⃣ Test diagnostic COVID-19...")
    covid_symptoms = {
        'patient_id': patient_id,
        'symptoms': ['fièvre', 'toux sèche', 'fatigue', 'perte goût', 'difficultés respiratoires']
    }
    response = requests.post(f'{BASE_URL}/diagnose', json=covid_symptoms)
    print_response("Diagnostic COVID", response)
    
    # 7. Récupérer l'historique du patient
    print("\n7️⃣ Récupération de l'historique complet...")
    response = requests.get(f'{BASE_URL}/history/patient/{patient_id}')
    print_response("Historique Patient", response)
    
    # 8. Obtenir les statistiques
    print("\n8️⃣ Statistiques du système...")
    response = requests.get(f'{BASE_URL}/stats')
    print_response("Statistiques", response)
    
    # 9. Créer un deuxième patient
    print("\n9️⃣ Création d'un second patient...")
    patient2_data = {
        'nom': 'Martin',
        'prenom': 'Jean',
        'date_naissance': '1990-07-22',
        'sexe': 'M',
        'telephone': '0698765432',
        'email': 'jean.martin@email.com',
        'allergies': [],
        'antecedents': ['hypertension']
    }
    response = requests.post(f'{BASE_URL}/patients', json=patient2_data)
    print_response("Création Patient 2", response)
    patient2_id = response.json()['patient']['id']
    
    # 10. Test diagnostic gastro-entérite
    print("\n🔟 Test diagnostic gastro-entérite...")
    gastro_symptoms = {
        'patient_id': patient2_id,
        'symptoms': ['diarrhée', 'vomissements', 'douleurs abdominales', 'nausées']
    }
    response = requests.post(f'{BASE_URL}/diagnose', json=gastro_symptoms)
    print_response("Diagnostic Gastro", response)
    
    print("\n" + "="*60)
    print("✅ Tests terminés avec succès!")
    print("="*60)

def demo_interactive():
    """Mode interactif pour tester l'API"""
    print("\n🏥 Mode Interactif - Système de Diagnostic")
    print("="*60)
    
    while True:
        print("\n📋 Menu:")
        print("1. Créer un patient")
        print("2. Enregistrer des symptômes")
        print("3. Générer un diagnostic")
        print("4. Voir l'historique d'un patient")
        print("5. Voir les statistiques")
        print("6. Quitter")
        
        choice = input("\nChoisir une option (1-6): ")
        
        if choice == '1':
            print("\n--- Création d'un patient ---")
            nom = input("Nom: ")
            prenom = input("Prénom: ")
            date_naissance = input("Date de naissance (YYYY-MM-DD): ")
            sexe = input("Sexe (M/F): ")
            
            patient_data = {
                'nom': nom,
                'prenom': prenom,
                'date_naissance': date_naissance,
                'sexe': sexe
            }
            
            response = requests.post(f'{BASE_URL}/patients', json=patient_data)
            print_response("Patient créé", response)
            
        elif choice == '2':
            patient_id = input("ID du patient: ")
            symptoms = input("Symptômes (séparés par des virgules): ").split(',')
            symptoms = [s.strip() for s in symptoms]
            
            symptoms_data = {
                'patient_id': patient_id,
                'symptoms': symptoms
            }
            
            response = requests.post(f'{BASE_URL}/symptoms', json=symptoms_data)
            print_response("Symptômes enregistrés", response)
            
        elif choice == '3':
            patient_id = input("ID du patient (optionnel): ")
            symptoms = input("Symptômes (séparés par des virgules): ").split(',')
            symptoms = [s.strip() for s in symptoms]
            
            diagnosis_data = {
                'symptoms': symptoms
            }
            if patient_id:
                diagnosis_data['patient_id'] = patient_id
            
            response = requests.post(f'{BASE_URL}/diagnose', json=diagnosis_data)
            print_response("Diagnostic", response)
            
        elif choice == '4':
            patient_id = input("ID du patient: ")
            response = requests.get(f'{BASE_URL}/history/patient/{patient_id}')
            print_response("Historique", response)
            
        elif choice == '5':
            response = requests.get(f'{BASE_URL}/stats')
            print_response("Statistiques", response)
            
        elif choice == '6':
            print("\n👋 Au revoir!")
            break
        
        else:
            print("❌ Option invalide")

if __name__ == '__main__':
    import sys
    
    print("🏥 Client de Test - Système de Diagnostic Médical")
    print("="*60)
    print("\nAssurez-vous que le serveur Flask est démarré (python app.py)")
    print("\nModes disponibles:")
    print("1. Test automatique complet")
    print("2. Mode interactif")
    
    mode = input("\nChoisir le mode (1 ou 2): ")
    
    try:
        if mode == '1':
            test_system()
        elif mode == '2':
            demo_interactive()
        else:
            print("Mode invalide")
    except requests.exceptions.ConnectionError:
        print("\n❌ Erreur: Impossible de se connecter au serveur")
        print("Assurez-vous que le serveur Flask est démarré sur http://localhost:5000")