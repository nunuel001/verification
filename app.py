
import streamlit as st
import pandas as pd
import streamlit.components.v1 as components
import os

st.set_page_config(page_title="Vérification Invités", layout="centered")
st.title("🎤 Vérification vocale des invités")

# 1. Upload de la liste
uploaded_file = st.file_uploader("📁 Téléversez le fichier des invités (.csv ou .xlsx)", type=["csv", "xlsx"])

if uploaded_file is not None:
    filename = uploaded_file.name
    extension = os.path.splitext(filename)[1]

    try:
        if extension == ".csv":
            df = pd.read_csv(uploaded_file)
        elif extension in [".xlsx", ".xls"]:
            df = pd.read_excel(uploaded_file)
        else:
            st.error("❌ Format de fichier non pris en charge.")
            st.stop()
        
        st.success("✅ Liste chargée. Vous pouvez utiliser la reconnaissance vocale ci-dessous.")

        if 'Nom' not in df.columns:
            st.error("❌ Le fichier ne contient pas de colonne intitulée exactement 'Nom'. Veuillez corriger votre fichier.")
            st.stop()

    except Exception as e:
        st.error(f"Erreur de lecture du fichier : {e}")
        st.stop()
else:
    st.warning("Veuillez téléverser un fichier CSV ou Excel.")
    st.stop()

# 2. Zone d'affichage du résultat
st.markdown("### 🧠 Nom reconnu par la voix")
nom_reconnu = st.text_input("Nom reconnu :", key="nom_vocal")

# 3. Bouton de validation manuelle
if st.button("Vérifier ce nom"):
    if nom_reconnu:
        noms_bdd = df["Nom"].str.lower().str.strip()
        if nom_reconnu.lower().strip() in noms_bdd.values:
            st.success(f"✅ {nom_reconnu} est sur la liste des invités.")
        else:
            st.error(f"❌ {nom_reconnu} n'a pas été trouvé.")
    else:
        st.warning("Aucun nom n'a été reconnu.")

# 4. Composant JS pour la reconnaissance vocale
st.markdown("### 🎙️ Appuyez sur le bouton pour parler")

components.html(
    """
    <button onclick="startRecognition()" style="padding: 10px 20px; font-size: 18px;">🎤 Parler</button>
    <p id="result" style="font-size: 18px; font-weight: bold;"></p>
    
    <script>
        function startRecognition() {
            const recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
            recognition.lang = "fr-FR";
            recognition.interimResults = false;
            recognition.maxAlternatives = 1;
            
            recognition.start();
            recognition.onresult = function(event) {
                const nom = event.results[0][0].transcript;
                document.getElementById("result").innerText = "Nom reconnu : " + nom;

                const streamlitInput = window.parent.document.querySelector('input[data-testid="stTextInput"]');
                if (streamlitInput) {
                    const nativeInputValueSetter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, "value").set;
                    nativeInputValueSetter.call(streamlitInput, nom);
                    streamlitInput.dispatchEvent(new Event("input", { bubbles: true }));
                }
            };
        }
    </script>
    """,
    height=200,
)
