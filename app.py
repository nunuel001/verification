import gspread
from google.oauth2.service_account import Credentials
import re
import unicodedata
import streamlit as st
import pandas as pd

# Fonction pour normaliser les noms (accents, majuscules)
def normalize_string(s):
    if not isinstance(s, str):
        return ""
    s = s.strip().lower()
    s = unicodedata.normalize('NFD', s)
    s = ''.join(c for c in s if unicodedata.category(c) != 'Mn')  # retire les accents
    return s

# CONFIG
st.set_page_config(page_title="Vérification Invités", layout="centered")

# Titre
st.markdown("""
<h1 style='text-align: center; color: #2c3e50; font-size: 2.2em;'>🎤 Vérification des invités</h1>
<hr style='border-top: 2px solid #4CAF50;'>
""", unsafe_allow_html=True)

# Lien Google Sheets
st.markdown("### 🔗 Lien Google Sheets (CSV publié)")
sheet_url = st.text_input("Collez ici le lien du fichier Google Sheets", placeholder="https://docs.google.com/spreadsheets/d/...")

if not sheet_url:
    st.info("Veuillez coller un lien Google Sheets.")
    st.stop()

# Authentification avec gspread
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = Credentials.from_service_account_info(st.secrets["google_service_account"], scopes=scope)
client = gspread.authorize(creds)

# Lecture de la feuille
sheet_id_match = re.search(r"/d/([a-zA-Z0-9-_]+)", sheet_url)
if not sheet_id_match:
    st.error("Lien Google Sheets invalide.")
    st.stop()

sheet_id = sheet_id_match.group(1)
sheet = client.open_by_key(sheet_id)
worksheet = sheet.sheet1
data = worksheet.get_all_records()
df = pd.DataFrame(data)

# Champ texte + bouton de validation
st.markdown("### 🧠 Entrez le nom complet de l'invité")
nom_reconnu = st.text_input("", placeholder="Nom Prénom", key="nom_vocal", label_visibility="collapsed")
valider = st.button("✅ Vérifier", type="primary")

# Vérification
if valider and nom_reconnu:
    nom_reconnu_complet = normalize_string(nom_reconnu)
    df['full_name'] = (df['Nom'].astype(str) + " " + df['Prénoms'].astype(str)).apply(normalize_string)
    match = df[df['full_name'] == nom_reconnu_complet]

    if not match.empty:
        st.success(f"✅ {nom_reconnu_complet.title()} est sur la liste des invités.")
        info = match.iloc[0]
        st.markdown(f"""
        <div style='border: 2px solid #4CAF50; border-radius: 12px; padding: 20px; background-color: #f0fdf4; margin-top: 30px; box-shadow: 0px 2px 5px rgba(0,0,0,0.05);'>
            <h3 style='color: #2c3e50;'>🪪 Carte d'invité</h3>
            <p><strong>Nom :</strong> {info['Nom']}</p>
            <p><strong>Prénoms :</strong> {info['Prénoms']}</p>
            <p><strong>Entreprise :</strong> {info.get('Entreprise', 'Non spécifié')}</p>
            <p><strong>Fonction :</strong> {info.get('Fonction', 'Non spécifié')}</p>
            <p><strong>Contact :</strong> {info.get('Contact téléph', 'Non spécifié')}</p>
            <p><strong>Email :</strong> {info.get('Email', 'Non spécifié')}</p>
            <p><strong>VVIP :</strong> {info.get('VVIP', 'Non')}</p>
            <p><strong>Accompagné :</strong> {info.get('Seriez-vous accompagné ?', 'Non spécifié')}</p>
        </div>
        """, unsafe_allow_html=True)

        # Mise à jour du statut si la colonne existe
        if "Statut" in df.columns:
            row_index = match.index[0] + 2
            col_statut = df.columns.get_loc("Statut") + 1
            worksheet.update_cell(row_index, col_statut, "Vérifié ✅")
        else:
            st.warning("Colonne 'Statut' absente. Aucune mise à jour effectuée.")
    else:
        st.error(f"❌ {nom_reconnu_complet.title()} n'est pas sur la liste.")
