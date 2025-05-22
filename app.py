import gspread
from google.oauth2.service_account import Credentials
import re
import streamlit as st
import pandas as pd
import streamlit.components.v1 as components

st.set_page_config(page_title="Vérification Invités", layout="centered")
st.markdown("<h1 style='text-align: center;'>🎤 Vérification vocale des invités</h1>", unsafe_allow_html=True)

# Lien CSV à coller
st.markdown("### 🔗 Lien Google Sheets (format CSV publié)")
sheet_url = st.text_input("Collez ici le lien du fichier Google Sheets (CSV partagé)", placeholder="https://docs.google.com/spreadsheets/d/...")

if not sheet_url:
    st.info("Veuillez coller un lien Google Sheets publié en CSV.")
    st.stop()

# Authentification Google Sheets
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = Credentials.from_service_account_info(
    st.secrets["google_service_account"], scopes=scope
)
client = gspread.authorize(creds)

# Extraire ID du Google Sheets depuis l'URL collée
sheet_id_match = re.search(r"/d/([a-zA-Z0-9-_]+)", sheet_url)
if not sheet_id_match:
    st.error("Lien Google Sheets invalide.")
    st.stop()

sheet_id = sheet_id_match.group(1)
sheet = client.open_by_key(sheet_id)
worksheet = sheet.sheet1  # ou .worksheet("Form_Responses1") si besoin

# Charger la feuille en DataFrame
data = worksheet.get_all_records()
df = pd.DataFrame(data)


# Zone d'entrée + bouton vocal
col1, col2 = st.columns([3, 1])
with col1:
    nom_reconnu = st.text_input("🧠 Nom détecté :", key="nom_vocal", label_visibility="visible")
with col2:
    st.markdown("<div style='height: 30px;'></div>", unsafe_allow_html=True)
    st.markdown("""
    <button id="speakBtn" onmousedown="startRecognition()" onmouseup="stopRecognition()"
        style="padding: 12px 15px; font-size: 16px; border-radius: 8px; background-color: #4CAF50; color: white; border: none; width: 100%; height: 53px;">
        🎤 Maintenir
    </button>
    """, unsafe_allow_html=True)

if st.session_state.nom_vocal:
    nom_reconnu_complet = st.session_state.nom_vocal.strip().lower()
    df['full_name'] = (df['Nom'].astype(str) + " " + df['Prénoms'].astype(str)).str.lower().str.strip()
    match = df[df['full_name'] == nom_reconnu_complet]

    if not match.empty:
        st.success(f"✅ {nom_reconnu_complet.title()} est sur la liste des invités.")
        info = match.iloc[0]
        st.markdown("### 🪪 Carte d'identité de l'invité")
        st.markdown(f"""
        <div style='border:2px solid #4CAF50; border-radius:10px; padding:20px; background-color:#f9f9f9'>
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
            st.warning("Colonne 'Statut' absente. Aucune mise à jour faite.")

    else:
        st.error(f"❌ {nom_reconnu_complet.title()} n'est pas sur la liste.")



# JS : reconnaissance vocale
components.html(
    """
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
    """,
    height=0
)
