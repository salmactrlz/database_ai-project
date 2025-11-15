import pandas as pd
import numpy as np
import os
from pathlib import Path

class MedicalDataCleaner:
    """Classe pour analyser et nettoyer les données médicales"""
    
    def __init__(self, data_folder, output_folder='data_clean'):
        self.data_folder = data_folder
        self.output_folder = output_folder
        self.cleaning_report = []
        
    def print_separator(self, title, char="="):
        """Affiche un séparateur visuel"""
        print("\n" + char*70)
        print(f"  {title}")
        print(char*70)
        
    def log_action(self, action):
        """Enregistre une action de nettoyage"""
        self.cleaning_report.append(action)
        
    def analyze_file(self, file_path, file_name):
        """Analyse complète d'un fichier CSV"""
        self.print_separator(f"📊 ANALYSE : {file_name}")
        
        try:
            # Lecture du fichier
            df = pd.read_csv(file_path)
            
            print(f"\n📏 Dimensions : {df.shape[0]} lignes × {df.shape[1]} colonnes")
            
            # Colonnes
            print(f"\n📋 Colonnes ({len(df.columns)}) :")
            for i, col in enumerate(df.columns, 1):
                print(f"   {i}. {col}")
            
            # Valeurs manquantes
            print(f"\n🔍 Analyse des valeurs manquantes :")
            missing = df.isnull().sum()
            total_missing = missing.sum()
            
            if total_missing > 0:
                print(f"   ⚠️  Total : {total_missing} valeur(s) manquante(s)")
                for col in df.columns:
                    if missing[col] > 0:
                        pct = (missing[col] / len(df)) * 100
                        print(f"      • {col}: {missing[col]} ({pct:.1f}%)")
            else:
                print("   ✅ Aucune valeur manquante")
            
            # Doublons
            print(f"\n🔢 Analyse des doublons :")
            duplicates = df.duplicated().sum()
            if duplicates > 0:
                print(f"   ⚠️  {duplicates} ligne(s) complètement dupliquée(s)")
            else:
                print("   ✅ Aucune ligne dupliquée")
            
            # Types de données
            print(f"\n🔤 Types de données :")
            for col in df.columns:
                dtype = df[col].dtype
                unique_count = df[col].nunique()
                print(f"   • {col}: {dtype} ({unique_count} valeurs uniques)")
            
            # Aperçu
            print(f"\n👀 Aperçu (5 premières lignes) :")
            print(df.head().to_string())
            
            # Statistiques pour colonnes numériques
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            if len(numeric_cols) > 0:
                print(f"\n📊 Statistiques numériques :")
                print(df[numeric_cols].describe().to_string())
            
            return df
            
        except Exception as e:
            print(f"❌ Erreur lors de la lecture : {e}")
            return None
    
    def clean_text_column(self, series, column_name):
        """Nettoie une colonne de texte"""
        if series.dtype != 'object':
            return series
        
        cleaned = series.copy()
        changes = 0
        
        # Supprime les espaces avant/après
        cleaned = cleaned.str.strip()
        
        # Remplace les underscores par des espaces (pour symptômes)
        if 'symptom' in column_name.lower() or 'symptome' in column_name.lower():
            before = cleaned.copy()
            cleaned = cleaned.str.replace('_', ' ')
            changes += (before != cleaned).sum()
        
        # Remplace les valeurs vides par NaN
        cleaned = cleaned.replace('', np.nan)
        
        return cleaned
    
    def clean_descriptions(self, df):
        """Nettoie symptom_Description.csv"""
        self.print_separator("🧹 NETTOYAGE : Descriptions", "-")
        
        df_clean = df.copy()
        initial_rows = len(df_clean)
        
        print("\n1️⃣ Nettoyage des colonnes texte...")
        df_clean['Disease'] = self.clean_text_column(df_clean['Disease'], 'Disease')
        df_clean['Description'] = self.clean_text_column(df_clean['Description'], 'Description')
        
        print("2️⃣ Suppression des doublons de maladies...")
        before_dedup = len(df_clean)
        df_clean = df_clean.drop_duplicates(subset=['Disease'], keep='first')
        duplicates_removed = before_dedup - len(df_clean)
        if duplicates_removed > 0:
            print(f"   ✅ {duplicates_removed} doublon(s) supprimé(s)")
            self.log_action(f"Descriptions: {duplicates_removed} doublons supprimés")
        else:
            print("   ✅ Aucun doublon trouvé")
        
        print("3️⃣ Gestion des valeurs manquantes...")
        missing_desc = df_clean['Description'].isnull().sum()
        if missing_desc > 0:
            print(f"   ⚠️  {missing_desc} description(s) manquante(s)")
            df_clean['Description'] = df_clean['Description'].fillna("Description non disponible")
            self.log_action(f"Descriptions: {missing_desc} descriptions manquantes remplacées")
        else:
            print("   ✅ Aucune valeur manquante")
        
        print("4️⃣ Uniformisation de la casse...")
        # Conserve les acronymes en majuscules (GERD, AIDS, etc.)
        df_clean['Disease'] = df_clean['Disease'].apply(
            lambda x: x if x.isupper() and len(x) <= 5 else x.title()
        )
        
        print("5️⃣ Vérification finale...")
        # Supprime les lignes avec maladie manquante
        before_final = len(df_clean)
        df_clean = df_clean.dropna(subset=['Disease'])
        removed_final = before_final - len(df_clean)
        if removed_final > 0:
            print(f"   ⚠️  {removed_final} ligne(s) sans nom de maladie supprimée(s)")
        
        final_rows = len(df_clean)
        print(f"\n✅ Nettoyage terminé : {initial_rows} → {final_rows} lignes")
        self.log_action(f"Descriptions: {initial_rows} → {final_rows} lignes conservées")
        
        return df_clean
    
    def clean_severity(self, df):
        """Nettoie Symptom-severity.csv"""
        self.print_separator("🧹 NETTOYAGE : Sévérité des symptômes", "-")
        
        df_clean = df.copy()
        initial_rows = len(df_clean)
        
        print("\n1️⃣ Nettoyage des noms de symptômes...")
        df_clean['Symptom'] = self.clean_text_column(df_clean['Symptom'], 'Symptom')
        
        print("2️⃣ Suppression des doublons...")
        before_dedup = len(df_clean)
        df_clean = df_clean.drop_duplicates(subset=['Symptom'], keep='first')
        duplicates_removed = before_dedup - len(df_clean)
        if duplicates_removed > 0:
            print(f"   ✅ {duplicates_removed} doublon(s) supprimé(s)")
            self.log_action(f"Severity: {duplicates_removed} doublons supprimés")
        
        print("3️⃣ Validation et nettoyage des poids...")
        if 'weight' in df_clean.columns:
            # Convertit en numérique
            df_clean['weight'] = pd.to_numeric(df_clean['weight'], errors='coerce')
            
            # Remplace les valeurs manquantes
            missing_weight = df_clean['weight'].isnull().sum()
            if missing_weight > 0:
                print(f"   ⚠️  {missing_weight} poid(s) manquant(s) → remplacé(s) par 1")
                df_clean['weight'] = df_clean['weight'].fillna(1)
                self.log_action(f"Severity: {missing_weight} poids manquants")
            
            # Ajuste les valeurs hors limites
            invalid_low = (df_clean['weight'] < 1).sum()
            invalid_high = (df_clean['weight'] > 7).sum()
            
            if invalid_low > 0 or invalid_high > 0:
                print(f"   ⚠️  {invalid_low + invalid_high} poid(s) invalide(s) → ajusté(s)")
                df_clean.loc[df_clean['weight'] < 1, 'weight'] = 1
                df_clean.loc[df_clean['weight'] > 7, 'weight'] = 7
                self.log_action(f"Severity: {invalid_low + invalid_high} poids ajustés")
            
            print(f"   ✅ Poids : min={df_clean['weight'].min()}, max={df_clean['weight'].max()}")
        
        print("4️⃣ Suppression des lignes sans symptôme...")
        before_final = len(df_clean)
        df_clean = df_clean.dropna(subset=['Symptom'])
        removed_final = before_final - len(df_clean)
        if removed_final > 0:
            print(f"   ⚠️  {removed_final} ligne(s) supprimée(s)")
        
        final_rows = len(df_clean)
        print(f"\n✅ Nettoyage terminé : {initial_rows} → {final_rows} lignes")
        self.log_action(f"Severity: {initial_rows} → {final_rows} lignes conservées")
        
        return df_clean
    
    def clean_dataset(self, df):
        """Nettoie dataset.csv"""
        self.print_separator("🧹 NETTOYAGE : Dataset principal", "-")
        
        df_clean = df.copy()
        initial_rows = len(df_clean)
        
        print("\n1️⃣ Nettoyage des noms de maladies...")
        df_clean['Disease'] = self.clean_text_column(df_clean['Disease'], 'Disease')
        df_clean['Disease'] = df_clean['Disease'].apply(
            lambda x: x if pd.isna(x) or (x.isupper() and len(x) <= 5) else x.title()
        )
        
        print("2️⃣ Nettoyage des symptômes...")
        symptom_cols = [col for col in df_clean.columns if col.startswith('Symptom_')]
        print(f"   Colonnes de symptômes trouvées : {len(symptom_cols)}")
        
        for col in symptom_cols:
            df_clean[col] = self.clean_text_column(df_clean[col], col)
        
        print("3️⃣ Suppression des lignes sans maladie...")
        before_disease = len(df_clean)
        df_clean = df_clean.dropna(subset=['Disease'])
        removed_disease = before_disease - len(df_clean)
        if removed_disease > 0:
            print(f"   ⚠️  {removed_disease} ligne(s) sans maladie supprimée(s)")
        
        print("4️⃣ Vérification du nombre de symptômes par maladie...")
        empty_rows = 0
        for idx, row in df_clean.iterrows():
            symptom_count = sum(pd.notna(row[col]) and row[col] != '' for col in symptom_cols)
            if symptom_count == 0:
                empty_rows += 1
        
        if empty_rows > 0:
            print(f"   ⚠️  {empty_rows} maladie(s) sans aucun symptôme détecté(e)s")
            # Garde quand même ces lignes, elles seront filtrées à l'importation
        else:
            print("   ✅ Toutes les maladies ont au moins un symptôme")
        
        print("5️⃣ Suppression des doublons complets...")
        before_dedup = len(df_clean)
        df_clean = df_clean.drop_duplicates()
        duplicates_removed = before_dedup - len(df_clean)
        if duplicates_removed > 0:
            print(f"   ✅ {duplicates_removed} doublon(s) supprimé(s)")
            self.log_action(f"Dataset: {duplicates_removed} doublons supprimés")
        
        final_rows = len(df_clean)
        print(f"\n✅ Nettoyage terminé : {initial_rows} → {final_rows} lignes")
        self.log_action(f"Dataset: {initial_rows} → {final_rows} lignes conservées")
        
        return df_clean
    
    def clean_precautions(self, df):
        """Nettoie symptom_precaution.csv"""
        self.print_separator("🧹 NETTOYAGE : Précautions", "-")
        
        df_clean = df.copy()
        initial_rows = len(df_clean)
        
        print("\n1️⃣ Nettoyage des noms de maladies...")
        df_clean['Disease'] = self.clean_text_column(df_clean['Disease'], 'Disease')
        df_clean['Disease'] = df_clean['Disease'].apply(
            lambda x: x if pd.isna(x) or (x.isupper() and len(x) <= 5) else x.title()
        )
        
        print("2️⃣ Nettoyage des précautions...")
        precaution_cols = [col for col in df_clean.columns if col.startswith('Precaution_')]
        print(f"   Colonnes de précautions trouvées : {len(precaution_cols)}")
        
        for col in precaution_cols:
            df_clean[col] = self.clean_text_column(df_clean[col], col)
        
        print("3️⃣ Suppression des doublons de maladies...")
        before_dedup = len(df_clean)
        df_clean = df_clean.drop_duplicates(subset=['Disease'], keep='first')
        duplicates_removed = before_dedup - len(df_clean)
        if duplicates_removed > 0:
            print(f"   ✅ {duplicates_removed} doublon(s) supprimé(s)")
            self.log_action(f"Precautions: {duplicates_removed} doublons supprimés")
        
        print("4️⃣ Suppression des lignes sans maladie...")
        before_disease = len(df_clean)
        df_clean = df_clean.dropna(subset=['Disease'])
        removed_disease = before_disease - len(df_clean)
        if removed_disease > 0:
            print(f"   ⚠️  {removed_disease} ligne(s) supprimée(s)")
        
        final_rows = len(df_clean)
        print(f"\n✅ Nettoyage terminé : {initial_rows} → {final_rows} lignes")
        self.log_action(f"Precautions: {initial_rows} → {final_rows} lignes conservées")
        
        return df_clean
    
    def save_cleaned_data(self, df, filename):
        """Sauvegarde les données nettoyées"""
        os.makedirs(self.output_folder, exist_ok=True)
        output_path = os.path.join(self.output_folder, filename)
        df.to_csv(output_path, index=False, encoding='utf-8')
        print(f"💾 Sauvegardé : {output_path}")
    
    def generate_cleaning_report(self):
        """Génère un rapport de nettoyage"""
        self.print_separator("📋 RAPPORT DE NETTOYAGE")
        
        if not self.cleaning_report:
            print("\n✅ Aucune action de nettoyage nécessaire")
            return
        
        print("\n📝 Actions effectuées :")
        for i, action in enumerate(self.cleaning_report, 1):
            print(f"   {i}. {action}")
    
    def run_full_cleaning(self):
        """Exécute le nettoyage complet"""
        self.print_separator("🚀 NETTOYAGE DES DONNÉES MÉDICALES", "=")
        
        print("\nCe script va :")
        print("  1. Analyser chaque fichier CSV")
        print("  2. Détecter les problèmes (doublons, valeurs manquantes, etc.)")
        print("  3. Nettoyer les données")
        print("  4. Sauvegarder les versions propres dans 'data_clean/'")
        
        files = {
            'descriptions': 'symptom_Description.csv',
            'severity': 'Symptom-severity.csv',
            'dataset': 'dataset.csv',
            'precautions': 'symptom_precaution.csv'
        }
        
        # Vérifie les fichiers
        print("\n🔍 Vérification des fichiers...")
        missing_files = []
        for key, filename in files.items():
            filepath = os.path.join(self.data_folder, filename)
            if os.path.exists(filepath):
                print(f"  ✅ {filename}")
            else:
                print(f"  ❌ {filename} - INTROUVABLE")
                missing_files.append(filename)
        
        if missing_files:
            print(f"\n❌ Fichiers manquants : {', '.join(missing_files)}")
            print(f"   Placez-les dans le dossier '{self.data_folder}/'")
            return
        
        input("\n▶️  Appuyez sur Entrée pour commencer le nettoyage...")
        
        cleaned_data = {}
        
        # 1. Descriptions
        df_desc = self.analyze_file(
            os.path.join(self.data_folder, files['descriptions']),
            'symptom_Description.csv'
        )
        if df_desc is not None:
            cleaned_data['descriptions'] = self.clean_descriptions(df_desc)
            self.save_cleaned_data(cleaned_data['descriptions'], 'symptom_Description_clean.csv')
        
        # 2. Sévérité
        df_sev = self.analyze_file(
            os.path.join(self.data_folder, files['severity']),
            'Symptom-severity.csv'
        )
        if df_sev is not None:
            cleaned_data['severity'] = self.clean_severity(df_sev)
            self.save_cleaned_data(cleaned_data['severity'], 'Symptom-severity_clean.csv')
        
        # 3. Dataset
        df_data = self.analyze_file(
            os.path.join(self.data_folder, files['dataset']),
            'dataset.csv'
        )
        if df_data is not None:
            cleaned_data['dataset'] = self.clean_dataset(df_data)
            self.save_cleaned_data(cleaned_data['dataset'], 'dataset_clean.csv')
        
        # 4. Précautions
        df_prec = self.analyze_file(
            os.path.join(self.data_folder, files['precautions']),
            'symptom_precaution.csv'
        )
        if df_prec is not None:
            cleaned_data['precautions'] = self.clean_precautions(df_prec)
            self.save_cleaned_data(cleaned_data['precautions'], 'symptom_precaution_clean.csv')
        
        # Rapport
        self.generate_cleaning_report()
        
        # Statistiques finales
        self.print_separator("📊 STATISTIQUES FINALES")
        
        print("\n✅ Nettoyage terminé avec succès !")
        print(f"\n📁 Les fichiers nettoyés sont dans : {self.output_folder}/")
        print("\n📋 Résumé :")
        
        for key, df in cleaned_data.items():
            print(f"   • {key}: {len(df)} lignes, {len(df.columns)} colonnes")
        
        print("\n💡 Prochaine étape :")
        print("   Modifiez import_database.py pour utiliser les fichiers de data_clean/")
        print("   Puis lancez : python import_database.py")
        
        return cleaned_data


def main():
    """Fonction principale"""
    cleaner = MedicalDataCleaner(data_folder='dataset', output_folder='data_clean')
    cleaner.run_full_cleaning()


if __name__ == "__main__":
    main()