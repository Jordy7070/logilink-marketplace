import streamlit as st
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader
import pandas as pd
from datetime import datetime
import hashlib
import uuid
import json

# Configuration de la page
st.set_page_config(
    page_title="LogiLink - Marketplace Logistique Anonyme",
    page_icon="🚚",
    layout="wide"
)

# Fonction pour générer un ID anonyme
def generate_anonymous_id(real_id, salt="LogiLink"):
    return hashlib.sha256(f"{real_id}{salt}".encode()).hexdigest()[:8]

# Fonction pour masquer les informations sensibles
def anonymize_data(data, sensitive_fields):
    anonymized = data.copy()
    for field in sensitive_fields:
        if field in anonymized:
            if isinstance(anonymized[field], str) and len(anonymized[field]) > 4:
                anonymized[field] = f"{anonymized[field][:2]}{'*' * (len(anonymized[field])-4)}{anonymized[field][-2:]}"
    return anonymized

# Classe pour gérer les besoins logistiques
class LogisticsNeed:
    def __init__(self, title, description, volume, weight, start_date, end_date, location, user_id):
        self.id = str(uuid.uuid4())
        self.anonymous_id = generate_anonymous_id(self.id)
        self.title = title
        self.description = description
        self.volume = volume
        self.weight = weight
        self.start_date = start_date
        self.end_date = end_date
        self.location = location
        self.user_id = user_id
        self.anonymous_user_id = generate_anonymous_id(user_id)
        self.status = "Nouveau"
        self.created_at = datetime.now()
        self.proposals = []

# Classe pour gérer les propositions
class LogisticsProposal:
    def __init__(self, need_id, provider_id, price, description):
        self.id = str(uuid.uuid4())
        self.anonymous_id = generate_anonymous_id(self.id)
        self.need_id = need_id
        self.provider_id = provider_id
        self.anonymous_provider_id = generate_anonymous_id(provider_id)
        self.price = price
        self.description = description
        self.status = "En attente"
        self.created_at = datetime.now()

def init_session_state():
    if 'login_status' not in st.session_state:
        st.session_state['login_status'] = False
    if 'user_type' not in st.session_state:
        st.session_state['user_type'] = None
    if 'user_id' not in st.session_state:
        st.session_state['user_id'] = None
    if 'needs' not in st.session_state:
        st.session_state['needs'] = []
    if 'proposals' not in st.session_state:
        st.session_state['proposals'] = []
    if 'messages' not in st.session_state:
        st.session_state['messages'] = []

def show_hero_section():
    st.markdown("""
    <div style='text-align: center; background-color: #f0f2f6; padding: 2rem; border-radius: 10px;'>
        <h1 style='color: #1f77b4;'>LogiLink Anonymous</h1>
        <h3>La première marketplace logistique 100% anonyme</h3>
        <p>Échangez en toute confidentialité avec vos futurs partenaires logistiques</p>
    </div>
    """, unsafe_allow_html=True)

def create_new_need():
    st.header("Publication anonyme d'un besoin logistique")
    with st.form("new_need_form"):
        title = st.text_input("Titre de la demande")
        description = st.text_area("Description (sans informations identifiantes)")
        col1, col2 = st.columns(2)
        with col1:
            volume = st.number_input("Volume estimé (m³)", min_value=0.0)
            start_date = st.date_input("Date de début")
        with col2:
            weight = st.number_input("Poids estimé (kg)", min_value=0.0)
            end_date = st.date_input("Date de fin")
        
        location = st.text_input("Zone géographique (région/département)")
        
        submit = st.form_submit_button("Publier anonymement")
        if submit:
            need = LogisticsNeed(
                title=title,
                description=description,
                volume=volume,
                weight=weight,
                start_date=start_date,
                end_date=end_date,
                location=location,
                user_id=st.session_state['user_id']
            )
            st.session_state['needs'].append(need)
            st.success("Votre besoin a été publié anonymement! Votre identifiant de suivi: " + need.anonymous_id)

def show_my_needs():
    st.header("Mes besoins publiés")
    if not st.session_state['needs']:
        st.info("Vous n'avez pas encore publié de besoins")
        return

    for need in st.session_state['needs']:
        if need.user_id == st.session_state['user_id']:
            with st.expander(f"📦 {need.title} (ID: {need.anonymous_id})"):
                col1, col2 = st.columns(2)
                with col1:
                    st.write("**Status:** ", need.status)
                    st.write("**Volume:** ", need.volume, "m³")
                    st.write("**Poids:** ", need.weight, "kg")
                with col2:
                    st.write("**Localisation:** ", need.location)
                    st.write("**Date début:** ", need.start_date)
                    st.write("**Date fin:** ", need.end_date)
                
                # Affichage des propositions reçues
                st.subheader("Propositions reçues")
                for proposal in st.session_state['proposals']:
                    if proposal.need_id == need.id:
                        with st.container():
                            st.markdown(f"""
                            ---
                            **Proposition de:** Prestataire #{proposal.anonymous_provider_id}  
                            **Prix proposé:** {proposal.price} €  
                            **Description:** {proposal.description}  
                            """)
                            if proposal.status == "En attente":
                                col1, col2 = st.columns(2)
                                with col1:
                                    if st.button("Accepter", key=f"accept_{proposal.id}"):
                                        proposal.status = "Accepté"
                                        need.status = "En cours"
                                with col2:
                                    if st.button("Refuser", key=f"refuse_{proposal.id}"):
                                        proposal.status = "Refusé"

def show_available_needs():
    st.header("Opportunités logistiques disponibles")
    if not st.session_state['needs']:
        st.info("Aucune opportunité disponible pour le moment")
        return

    for need in st.session_state['needs']:
        if need.status == "Nouveau":
            with st.expander(f"🔍 Besoin #{need.anonymous_id} - {need.title}"):
                col1, col2 = st.columns(2)
                with col1:
                    st.write("**Volume:** ", need.volume, "m³")
                    st.write("**Poids:** ", need.weight, "kg")
                with col2:
                    st.write("**Localisation:** ", need.location)
                    st.write("**Période:** ", f"{need.start_date} - {need.end_date}")
                
                st.write("**Description:**", need.description)
                
                # Formulaire de proposition
                with st.form(f"proposal_form_{need.id}"):
                    st.write("Faire une proposition anonyme")
                    price = st.number_input("Prix proposé (€)", min_value=0.0)
                    proposal_description = st.text_area("Description de votre proposition")
                    
                    if st.form_submit_button("Envoyer la proposition"):
                        proposal = LogisticsProposal(
                            need_id=need.id,
                            provider_id=st.session_state['user_id'],
                            price=price,
                            description=proposal_description
                        )
                        st.session_state['proposals'].append(proposal)
                        st.success("Votre proposition a été envoyée anonymement!")

def show_my_proposals():
    st.header("Mes propositions envoyées")
    has_proposals = False
    
    for proposal in st.session_state['proposals']:
        if proposal.provider_id == st.session_state['user_id']:
            has_proposals = True
            # Trouver le besoin correspondant
            need = next((n for n in st.session_state['needs'] if n.id == proposal.need_id), None)
            if need:
                with st.expander(f"💼 Proposition pour {need.title} (ID: {need.anonymous_id})"):
                    st.write("**Status:** ", proposal.status)
                    st.write("**Prix proposé:** ", proposal.price, "€")
                    st.write("**Description:** ", proposal.description)
                    st.write("**Date d'envoi:** ", proposal.created_at.strftime("%Y-%m-%d %H:%M"))
    
    if not has_proposals:
        st.info("Vous n'avez pas encore fait de propositions")

def main():
    init_session_state()
    
    # Barre latérale avec connexion
    with st.sidebar:
        if not st.session_state['login_status']:
            st.title("Connexion")
            user_type = st.radio("Je suis un:", ["E-commerçant", "Logisticien"])
            with st.form("login_form"):
                email = st.text_input("Email")
                password = st.text_input("Mot de passe", type="password")
                submit = st.form_submit_button("Se connecter")
                
                if submit:
                    # Simuler une connexion réussie
                    st.session_state['login_status'] = True
                    st.session_state['user_type'] = user_type
                    st.session_state['user_id'] = str(uuid.uuid4())  # Simulé
                    st.success(f"Connexion réussie en tant que {user_type}")
                    st.rerun()
        else:
            st.write(f"Connecté en tant que: {st.session_state['user_type']}")
            st.write(f"ID anonyme: {generate_anonymous_id(st.session_state['user_id'])}")
            if st.button("Déconnexion"):
                for key in st.session_state.keys():
                    del st.session_state[key]
                st.rerun()

    # Contenu principal
    if not st.session_state['login_status']:
        show_hero_section()
        st.markdown("### Comment fonctionne notre système d'anonymisation?")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("""
            🔒 **Publication anonyme**
            - ID unique masqué pour chaque besoin
            - Données sensibles cryptées
            - Localisation par zone uniquement
            """)
        
        with col2:
            st.markdown("""
            🤝 **Mise en relation sécurisée**
            - Propositions anonymes
            - Communication via chat crypté
            - Pas d'échange direct d'informations
            """)
        
        with col3:
            st.markdown("""
            ✅ **Révélation contrôlée**
            - Identités révélées après accord mutuel
            - Processus de vérification
            - Protection contre le démarchage
            """)
            
    else:
        if st.session_state['user_type'] == "E-commerçant":
            tab1, tab2 = st.tabs(["Publier un besoin", "Mes besoins"])
            
            with tab1:
                create_new_need()
            
            with tab2:
                show_my_needs()
                
        else:  # Logisticien
            tab1, tab2 = st.tabs(["Opportunités disponibles", "Mes propositions"])
            
            with tab1:
                show_available_needs()
            
            with tab2:
                show_my_proposals()

if __name__ == "__main__":
    main()