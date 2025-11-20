import sqlite3
import pandas as pd
import os
from pathlib import Path

class MedicalDatabaseImporter:
    """Classe pour importer les données nettoyées dans SQLite"""
    
    def __init__(self, db_path='dataset/ai_medical.db', data_folder='data_clean'):
        self.db_path = db_path
        self.data_folder = data_folder
        self.conn = None
        self.cursor = None
        
        # Crée le dossier dataset s'il n'existe pas
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
    def print_separator(self, title, char="="):
        """Affiche un séparateur"""
        print("\n" + char*70)
        print(f"  {title}")
        print(char*70)
        
    def connect(self):
        """Connexion à la base de données"""
        # Supprime l'ancienne base si elle existe
        if os.path.exists(self.db_path):
            response = input(f"\n⚠️  La base '{self.db_path}' existe déjà. Écraser ? (o/n): ")
            if response.lower() != 'o':
                print("❌ Importation annulée")
                return False
            os.remove(self.db_path)
            print(f"🗑️  Ancienne base supprimée")
        
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()
        
        # Active les clés étrangères
        self.cursor.execute("PRAGMA foreign_keys = ON")
        
        print(f"\n✅ Connecté à la base : {self.db_path}")
        return True
        
    def create_schema(self):
        """Crée le schéma de la base de données"""
        self.print_separator("🏗️  CRÉATION DU SCHÉMA")
        
        schema = """
        -- Table des maladies
        CREATE TABLE IF NOT EXISTS maladies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nom VARCHAR(100) NOT NULL UNIQUE,
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        -- Table des symptômes
        CREATE TABLE IF NOT EXISTS symptomes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nom VARCHAR(100) NOT NULL UNIQUE,
            severite INTEGER DEFAULT 1 CHECK(severite BETWEEN 1 AND 7),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        -- Table de liaison maladies-symptômes
        CREATE TABLE IF NOT EXISTS maladie_symptomes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            maladie_id INTEGER NOT NULL,
            symptome_id INTEGER NOT NULL,
            ordre INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (maladie_id) REFERENCES maladies(id) ON DELETE CASCADE,
            FOREIGN KEY (symptome_id) REFERENCES symptomes(id) ON DELETE CASCADE,
            UNIQUE(maladie_id, symptome_id)
        );

        -- Table des précautions
        CREATE TABLE IF NOT EXISTS precautions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            maladie_id INTEGER NOT NULL,
            precaution TEXT NOT NULL,
            ordre INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (maladie_id) REFERENCES maladies(id) ON DELETE CASCADE
        );

        -- Table historique des consultations
        CREATE TABLE IF NOT EXISTS consultations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id VARCHAR(50),
            date_consultation TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            symptomes_detectes TEXT,
            maladies_suggerees TEXT,
            conversation TEXT,
            user_feedback INTEGER
        );

        -- Index pour optimisation
        CREATE INDEX IF NOT EXISTS idx_maladie_symptomes_maladie 
            ON maladie_symptomes(maladie_id);
        CREATE INDEX IF NOT EXISTS idx_maladie_symptomes_symptome 
            ON maladie_symptomes(symptome_id);
        CREATE INDEX IF NOT EXISTS idx_precautions_maladie 
            ON precautions(maladie_id);
        CREATE INDEX IF NOT EXISTS idx_consultations_session 
            ON consultations(session_id);
        CREATE INDEX IF NOT EXISTS idx_symptomes_nom 
            ON symptomes(nom);
        CREATE INDEX IF NOT EXISTS idx_maladies_nom 
            ON maladies(nom);
        """
        
        print("\n🔨 Création des tables et index...")
        self.cursor.executescript(schema)
        self.conn.commit()
        print("✅ Schéma créé avec succès")
        
    def import_descriptions(self, csv_path):
        """Importe symptom_Description_clean.csv"""
        self.print_separator("📥 IMPORTATION : Descriptions des maladies", "-")
        
        if not os.path.exists(csv_path):
            print(f"❌ Fichier introuvable : {csv_path}")
            return 0
        
        print(f"\n📂 Lecture de : {csv_path}")
        df = pd.read_csv(csv_path)
        print(f"   {len(df)} lignes à importer")
        
        imported = 0
        errors = 0
        
        print("\n⏳ Importation en cours...")
        for idx, row in df.iterrows():
            try:
                disease = str(row['Disease']).strip()
                description = str(row['Description']).strip() if pd.notna(row['Description']) else ""
                
                self.cursor.execute(
                    "INSERT OR IGNORE INTO maladies (nom, description) VALUES (?, ?)",
                    (disease, description)
                )
                
                if self.cursor.rowcount > 0:
                    imported += 1
                    if imported % 10 == 0 or imported == len(df):
                        print(f"   [{imported}/{len(df)}] {disease[:40]}...", end='\r')
                    
            except Exception as e:
                errors += 1
                print(f"\n   ⚠️  Erreur ligne {idx}: {e}")
        
        self.conn.commit()
        print(f"\n\n✅ {imported} maladies importées")
        if errors > 0:
            print(f"⚠️  {errors} erreur(s)")
        
        return imported
        
    def import_severity(self, csv_path):
        """Importe Symptom-severity_clean.csv"""
        self.print_separator("📥 IMPORTATION : Sévérité des symptômes", "-")
        
        if not os.path.exists(csv_path):
            print(f"❌ Fichier introuvable : {csv_path}")
            return 0
        
        print(f"\n📂 Lecture de : {csv_path}")
        df = pd.read_csv(csv_path)
        print(f"   {len(df)} lignes à importer")
        
        imported = 0
        errors = 0
        
        print("\n⏳ Importation en cours...")
        for idx, row in df.iterrows():
            try:
                symptom = str(row['Symptom']).strip()
                weight = int(row['weight']) if pd.notna(row['weight']) else 1
                
                self.cursor.execute(
                    "INSERT OR IGNORE INTO symptomes (nom, severite) VALUES (?, ?)",
                    (symptom, weight)
                )
                
                if self.cursor.rowcount > 0:
                    imported += 1
                    if imported % 10 == 0 or imported == len(df):
                        print(f"   [{imported}/{len(df)}] {symptom[:40]}...", end='\r')
                    
            except Exception as e:
                errors += 1
                print(f"\n   ⚠️  Erreur ligne {idx}: {e}")
        
        self.conn.commit()
        print(f"\n\n✅ {imported} symptômes importés")
        if errors > 0:
            print(f"⚠️  {errors} erreur(s)")
        
        return imported
        
    def import_dataset(self, csv_path):
        """Importe dataset_clean.csv (relations maladies-symptômes)"""
        self.print_separator("📥 IMPORTATION : Relations maladies-symptômes", "-")
        
        if not os.path.exists(csv_path):
            print(f"❌ Fichier introuvable : {csv_path}")
            return 0
        
        print(f"\n📂 Lecture de : {csv_path}")
        df = pd.read_csv(csv_path)
        print(f"   {len(df)} lignes à traiter")
        
        # Colonnes de symptômes
        symptom_cols = [col for col in df.columns if col.startswith('Symptom_')]
        print(f"   {len(symptom_cols)} colonnes de symptômes détectées")
        
        imported = 0
        errors = 0
        
        print("\n⏳ Importation en cours...")
        for idx, row in df.iterrows():
            try:
                disease = str(row['Disease']).strip()
                
                # Récupère ou crée la maladie
                self.cursor.execute("SELECT id FROM maladies WHERE nom = ?", (disease,))
                result = self.cursor.fetchone()
                
                if not result:
                    # Crée la maladie si elle n'existe pas
                    self.cursor.execute(
                        "INSERT INTO maladies (nom) VALUES (?)", 
                        (disease,)
                    )
                    maladie_id = self.cursor.lastrowid
                else:
                    maladie_id = result[0]
                
                # Traite chaque symptôme
                for ordre, col in enumerate(symptom_cols, start=1):
                    symptom = row[col]
                    
                    if pd.isna(symptom) or not str(symptom).strip():
                        continue
                    
                    symptom = str(symptom).strip()
                    
                    # Récupère ou crée le symptôme
                    self.cursor.execute("SELECT id FROM symptomes WHERE nom = ?", (symptom,))
                    result = self.cursor.fetchone()
                    
                    if not result:
                        self.cursor.execute(
                            "INSERT INTO symptomes (nom) VALUES (?)", 
                            (symptom,)
                        )
                        symptome_id = self.cursor.lastrowid
                    else:
                        symptome_id = result[0]
                    
                    # Crée la relation
                    try:
                        self.cursor.execute("""
                            INSERT OR IGNORE INTO maladie_symptomes 
                            (maladie_id, symptome_id, ordre) 
                            VALUES (?, ?, ?)
                        """, (maladie_id, symptome_id, ordre))
                        
                        if self.cursor.rowcount > 0:
                            imported += 1
                            
                    except Exception as e:
                        errors += 1
                
                if (idx + 1) % 5 == 0 or idx == len(df) - 1:
                    print(f"   [{idx+1}/{len(df)}] {disease[:30]}... - {imported} relations", end='\r')
                
            except Exception as e:
                errors += 1
                print(f"\n   ⚠️  Erreur ligne {idx}: {e}")
        
        self.conn.commit()
        print(f"\n\n✅ {imported} relations maladie-symptôme créées")
        if errors > 0:
            print(f"⚠️  {errors} erreur(s)")
        
        return imported
        
    def import_precautions(self, csv_path):
        """Importe symptom_precaution_clean.csv"""
        self.print_separator("📥 IMPORTATION : Précautions", "-")
        
        if not os.path.exists(csv_path):
            print(f"❌ Fichier introuvable : {csv_path}")
            return 0
        
        print(f"\n📂 Lecture de : {csv_path}")
        df = pd.read_csv(csv_path)
        print(f"   {len(df)} lignes à importer")
        
        # Colonnes de précautions
        precaution_cols = [col for col in df.columns if col.startswith('Precaution_')]
        print(f"   {len(precaution_cols)} colonnes de précautions détectées")
        
        imported = 0
        errors = 0
        not_found = 0
        
        print("\n⏳ Importation en cours...")
        for idx, row in df.iterrows():
            try:
                disease = str(row['Disease']).strip()
                
                # Récupère l'ID de la maladie
                self.cursor.execute("SELECT id FROM maladies WHERE nom = ?", (disease,))
                result = self.cursor.fetchone()
                
                if not result:
                    not_found += 1
                    continue
                
                maladie_id = result[0]
                
                # Traite chaque précaution
                for ordre, col in enumerate(precaution_cols, start=1):
                    precaution = row[col]
                    
                    if pd.isna(precaution) or not str(precaution).strip():
                        continue
                    
                    precaution = str(precaution).strip()
                    
                    try:
                        self.cursor.execute("""
                            INSERT INTO precautions (maladie_id, precaution, ordre) 
                            VALUES (?, ?, ?)
                        """, (maladie_id, precaution, ordre))
                        
                        imported += 1
                        
                    except Exception as e:
                        errors += 1
                
                if (idx + 1) % 10 == 0 or idx == len(df) - 1:
                    print(f"   [{idx+1}/{len(df)}] {disease[:30]}... - {imported} précautions", end='\r')
                
            except Exception as e:
                errors += 1
                print(f"\n   ⚠️  Erreur ligne {idx}: {e}")
        
        self.conn.commit()
        print(f"\n\n✅ {imported} précautions importées")
        if not_found > 0:
            print(f"ℹ️  {not_found} maladie(s) non trouvée(s)")
        if errors > 0:
            print(f"⚠️  {errors} erreur(s)")
        
        return imported
        
    def show_statistics(self):
        """Affiche les statistiques de la base"""
        self.print_separator("📊 STATISTIQUES DE LA BASE DE DONNÉES")
        
        stats = {}
        
        # Nombre de maladies
        self.cursor.execute("SELECT COUNT(*) FROM maladies")
        stats['maladies'] = self.cursor.fetchone()[0]
        
        # Nombre de symptômes
        self.cursor.execute("SELECT COUNT(*) FROM symptomes")
        stats['symptomes'] = self.cursor.fetchone()[0]
        
        # Nombre de relations
        self.cursor.execute("SELECT COUNT(*) FROM maladie_symptomes")
        stats['relations'] = self.cursor.fetchone()[0]
        
        # Nombre de précautions
        self.cursor.execute("SELECT COUNT(*) FROM precautions")
        stats['precautions'] = self.cursor.fetchone()[0]
        
        print("\n📈 Contenu de la base :")
        print(f"   • Maladies : {stats['maladies']}")
        print(f"   • Symptômes : {stats['symptomes']}")
        print(f"   • Relations : {stats['relations']}")
        print(f"   • Précautions : {stats['precautions']}")
        
        # Statistiques détaillées
        self.cursor.execute("""
            SELECT AVG(cnt) FROM (
                SELECT COUNT(*) as cnt 
                FROM maladie_symptomes 
                GROUP BY maladie_id
            )
        """)
        avg_symptoms = self.cursor.fetchone()[0]
        if avg_symptoms:
            print(f"   • Moyenne symptômes/maladie : {avg_symptoms:.1f}")
        
        # Taille de la base
        db_size = os.path.getsize(self.db_path)
        print(f"   • Taille : {db_size:,} octets ({db_size/1024:.2f} Ko)")
        
        # Exemple de données
        print("\n👀 Aperçu des données :")
        
        # Une maladie au hasard
        self.cursor.execute("""
            SELECT m.nom, m.description, COUNT(ms.symptome_id) as nb_symptomes
            FROM maladies m
            LEFT JOIN maladie_symptomes ms ON m.id = ms.maladie_id
            GROUP BY m.id
            ORDER BY RANDOM()
            LIMIT 1
        """)
        
        result = self.cursor.fetchone()
        if result:
            print(f"\n   📋 Exemple de maladie : {result[0]}")
            print(f"      Nombre de symptômes : {result[2]}")
            if result[1]:
                desc = result[1][:100] + "..." if len(result[1]) > 100 else result[1]
                print(f"      Description : {desc}")
        
    def close(self):
        """Ferme la connexion"""
        if self.conn:
            self.conn.close()
            print("\n✅ Connexion fermée")
            

def main():
    """Fonction principale"""
    print("="*70)
    print("📥 IMPORTATION DES DONNÉES VERS SQLITE")
    print("="*70)
    
    print("\nCe script va :")
    print("  1. Créer le schéma de la base de données")
    print("  2. Importer les données nettoyées depuis data_clean/")
    print("  3. Créer les relations entre maladies et symptômes")
    print("  4. Générer les statistiques")
    
    # Vérifie que le dossier data_clean existe
    if not os.path.exists('data_clean'):
        print("\n❌ Le dossier 'data_clean/' n'existe pas")
        print("   Lance d'abord : python clean_data.py")
        return
    
    # Vérifie les fichiers
    required_files = [
        'symptom_Description_clean.csv',
        'Symptom-severity_clean.csv',
        'dataset_clean.csv',
        'symptom_precaution_clean.csv'
    ]
    
    print("\n🔍 Vérification des fichiers...")
    missing = []
    for file in required_files:
        path = os.path.join('data_clean', file)
        if os.path.exists(path):
            print(f"  ✅ {file}")
        else:
            print(f"  ❌ {file} - MANQUANT")
            missing.append(file)
    
    if missing:
        print(f"\n❌ Fichiers manquants : {', '.join(missing)}")
        return
    
    # Démarre l'importation
    importer = MedicalDatabaseImporter(
        db_path='dataset/ai_medical.db',
        data_folder='data_clean'
    )
    
    try:
        if not importer.connect():
            return
        
        # Crée le schéma
        importer.create_schema()
        
        # Importe les données
        importer.import_descriptions('data_clean/symptom_Description_clean.csv')
        importer.import_severity('data_clean/Symptom-severity_clean.csv')
        importer.import_dataset('data_clean/dataset_clean.csv')
        importer.import_precautions('data_clean/symptom_precaution_clean.csv')
        
        # Affiche les stats
        importer.show_statistics()
        
        print("\n" + "="*70)
        print("🎉 IMPORTATION TERMINÉE AVEC SUCCÈS !")
        print("="*70)
        print(f"\n📁 Base de données créée : dataset/ai_medical.db")
        print("\n💡 Prochaines étapes :")
        print("   • Tester la base : sqlite3 dataset/ai_medical.db")
        print("   • Lancer l'application : streamlit run app.py")
        
    except Exception as e:
        print(f"\n❌ Erreur : {e}")
        import traceback
        traceback.print_exc()
    finally:
        importer.close()


if __name__ == "__main__":
    main()