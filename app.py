import gspread
from google.oauth2.service_account import Credentials
import re
import unicodedata
import streamlit as st
import pandas as pd
import streamlit.components.v1 as components

# ✅ Fonctions utilitaires
def normalize_string(s):
    if not isinstance(s, str):
        return ""
    s = s.strip().lower()
    s = unicodedata.normalize('NFD', s)
    s = ''.join(c for c in s if unicodedata.category(c) != 'Mn')
    return s

# ✅ Mise en page
st.set_page_config(page_title="Vérification Invités", layout="centered")
st.markdown("""
<h1 style='text-align: center; color: #2c3e50; font-size: 2.2em;'>🎤 Vérification vocale des invités</h1>
<hr style='border-top: 2px solid #4CAF50;'>
""", unsafe_allow_html=True)

# ✅ Lien Google Sheets
st.markdown("""
<div style='margin-bottom: 10px;'>
    <label style='font-weight: bold; color: #333;'>🔗 Lien Google Sheets (CSV publié)</label>
</div>
""", unsafe_allow_html=True)
sheet_url = st.text_input("", placeholder="https://docs.google.com/spreadsheets/d/...")

if not sheet_url:
    st.info("Veuillez coller un lien Google Sheets publié en CSV.")
    st.stop()

# ✅ Authentification
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = Credentials.from_service_account_info(st.secrets["google_service_account"], scopes=scope)
client = gspread.authorize(creds)

# ✅ Extraction Google Sheets
sheet_id_match = re.search(r"/d/([a-zA-Z0-9-_]+)", sheet_url)
if not sheet_id_match:
    st.error("Lien Google Sheets invalide.")
    st.stop()

sheet_id = sheet_id_match.group(1)
sheet = client.open_by_key(sheet_id)
worksheet = sheet.sheet1
data = worksheet.get_all_records()
df = pd.DataFrame(data)

# ✅ Champ vocal et bouton
st.markdown("<div style='margin-top:20px; font-weight:bold;'>🧠 Nom détecté :</div>", unsafe_allow_html=True)
col1, col2 = st.columns([3, 1])
with col1:
    nom_reconnu = st.text_input("", key="nom_vocal", placeholder="Nom Prénom", label_visibility="collapsed")
with col2:
    st.markdown("""
    <div style="text-align:center;">
        <button id="speakBtn" onmousedown="startRecognition()" onmouseup="stopRecognition()"
            style="
                padding: 16px 18px;
                font-size: 16px;
                border-radius: 50px;
                background-color: #4CAF50;
                color: white;
                border: none;
                width: 100%;
                box-shadow: 0 2px 5px rgba(0,0,0,0.2);
            ">
            🎤
        </button>
    </div>
    """, unsafe_allow_html=True)

# ✅ Vérification
if st.session_state.nom_vocal:
    nom_reconnu_complet = normalize_string(st.session_state.nom_vocal)
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

        # ✅ Mise à jour dans la feuille
        if "Statut" in df.columns:
            row_index = match.index[0] + 2
            col_statut = df.columns.get_loc("Statut") + 1
            worksheet.update_cell(row_index, col_statut, "Vérifié ✅")
        else:
            st.warning("Colonne 'Statut' absente. Aucune mise à jour effectuée.")
    else:
        st.error(f"❌ {nom_reconnu_complet.title()} n'est pas sur la liste.")

# ✅ JS pour reconnaissance vocale
components.html("""
<script>
    let recognition;
    function startRecognition() {
        recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
        recognition.lang = "fr-FR";
        recognition.interimResults = false;
        recognition.maxAlternatives = 1;

        recognition.onresult = function(event) {
            const nom = event.results[0][0].transcript;
            const input = window.parent.document.querySelector('input[data-testid="stTextInput"]');
            if (input) {
                input.value = nom;
                const event = new Event('input', { bubbles: true });
                input.dispatchEvent(event);
            }
        };
        recognition.start();
    }

    function stopRecognition() {
        if (recognition) {
            recognition.stop();
        }
    }
</script>
""", height=0)
