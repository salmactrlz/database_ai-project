import sqlite3
# Nom du fichier SQLite
db_name = "ai_medical.db"

# Connexion à la base
conn = sqlite3.connect(db_name)
cursor = conn.cursor()

# Liste des requêtes SQL
sql_commands = [

    """CREATE TABLE IF NOT EXISTS maladies (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nom VARCHAR(100) NOT NULL UNIQUE,
        description TEXT
    );""",

    """CREATE TABLE IF NOT EXISTS symptomes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nom VARCHAR(100) NOT NULL UNIQUE,
        severite INTEGER DEFAULT 1
    );""",

    """CREATE TABLE IF NOT EXISTS maladie_symptomes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        maladie_id INTEGER NOT NULL,
        symptome_id INTEGER NOT NULL,
        ordre INTEGER,
        FOREIGN KEY (maladie_id) REFERENCES maladies(id) ON DELETE CASCADE,
        FOREIGN KEY (symptome_id) REFERENCES symptomes(id) ON DELETE CASCADE,
        UNIQUE(maladie_id, symptome_id)
    );""",

    """CREATE TABLE IF NOT EXISTS precautions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        maladie_id INTEGER NOT NULL,
        precaution TEXT NOT NULL,
        ordre INTEGER,
        FOREIGN KEY (maladie_id) REFERENCES maladies(id) ON DELETE CASCADE
    );""",

    """CREATE TABLE IF NOT EXISTS consultations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        session_id VARCHAR(50),
        date_consultation TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        symptomes_detectes TEXT,
        maladies_suggerees TEXT,
        conversation TEXT
    );""",

    "CREATE INDEX IF NOT EXISTS idx_maladie_symptomes_maladie ON maladie_symptomes(maladie_id);",
    "CREATE INDEX IF NOT EXISTS idx_maladie_symptomes_symptome ON maladie_symptomes(symptome_id);",
    "CREATE INDEX IF NOT EXISTS idx_precautions_maladie ON precautions(maladie_id);"
]

# Exécuter toutes les commandes
for cmd in sql_commands:
    cursor.execute(cmd)

conn.commit()
conn.close()

print("Base de données créée avec succès !")

