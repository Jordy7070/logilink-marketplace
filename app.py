# Ajouter l'import au début du fichier avec les autres imports
import streamlit as st
import streamlit_authenticator as stauth
from streamlit_option_menu import option_menu
import plotly.express as px
import plotly.graph_objects as go
import yaml
from yaml.loader import SafeLoader
import pandas as pd
from datetime import datetime, timedelta
import hashlib
import uuid
import json
import random  # Ajout de l'import manquant

def show_activity_charts():
    col1, col2 = st.columns(2)
    
    with col1:
        # Créer des données d'exemple de manière plus robuste
        dates = pd.date_range(end=datetime.now(), periods=7)
        data = pd.DataFrame({
            'Date': dates,
            'Besoins': [max(0, len(st.session_state.get('needs', [])) + random.randint(-2, 2)) for _ in range(7)],
            'Propositions': [max(0, len(st.session_state.get('proposals', [])) + random.randint(-3, 3)) for _ in range(7)]
        })
        
        fig = px.line(data, x='Date', y=['Besoins', 'Propositions'],
                     title="Activité des 7 derniers jours")
        fig.update_layout(
            height=300,
            margin=dict(l=20, r=20, t=30, b=20),
            xaxis_title="Date",
            yaxis_title="Nombre",
            legend_title="Type"
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Calculer les vrais statuts depuis les données de session
        needs = st.session_state.get('needs', [])
        proposals = st.session_state.get('proposals', [])
        
        status_counts = {
            'Nouveau': len([n for n in needs if n.status == "Nouveau"]),
            'En cours': len([n for n in needs if n.status == "En cours"]),
            'Finalisé': len([n for n in needs if n.status == "Finalisé"]),
            'En attente': len([p for p in proposals if p.status == "En attente"])
        }
        
        # Ajouter une valeur minimale pour éviter un graphique vide
        if sum(status_counts.values()) == 0:
            status_counts = {
                'Nouveau': 1,
                'En cours': 0,
                'Finalisé': 0,
                'En attente': 0
            }
        
        fig = go.Figure(data=[go.Pie(
            labels=list(status_counts.keys()),
            values=list(status_counts.values()),
            hole=.3,
            marker_colors=['#1976D2', '#F57C00', '#2E7D32', '#C62828']
        )])
        fig.update_layout(
            title="Répartition des statuts",
            height=300,
            margin=dict(l=20, r=20, t=30, b=20)
        )
        st.plotly_chart(fig, use_container_width=True)

# Configuration de la page
st.set_page_config(
    page_title="LogiLink - Marketplace Logistique Anonyme",
    page_icon="🚚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personnalisé
def custom_css():
    st.markdown("""
    <style>
        .stApp {
            background-color: #f8f9fa;
        }
        
        .card {
            padding: 1.5rem;
            border-radius: 10px;
            background-color: white;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            margin-bottom: 1rem;
            transition: transform 0.2s ease, box-shadow 0.2s ease;
        }
        
        .card:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        }
        
        .metric-container {
            background: white;
            padding: 1rem;
            border-radius: 8px;
            text-align: center;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        }
        
        .metric-value {
            font-size: 24px;
            font-weight: bold;
            color: #1E88E5;
            margin: 0.5rem 0;
        }
        
        .metric-label {
            color: #666;
            font-size: 14px;
        }
        
        .status-badge {
            padding: 4px 12px;
            border-radius: 15px;
            font-size: 12px;
            font-weight: 500;
            display: inline-block;
        }
        
        .status-new { 
            background: #E3F2FD; 
            color: #1976D2; 
        }
        
        .status-pending { 
            background: #FFF3E0; 
            color: #F57C00; 
        }
        
        .status-accepted { 
            background: #E8F5E9; 
            color: #2E7D32; 
        }
        
        .status-refused { 
            background: #FFEBEE; 
            color: #C62828; 
        }
        
        .hero {
            background: linear-gradient(135deg, #1E88E5, #1565C0);
            color: white;
            padding: 3rem;
            border-radius: 15px;
            text-align: center;
            margin-bottom: 2rem;
        }
        
        .form-container {
            background: white;
            padding: 2rem;
            border-radius: 10px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        
        .chat-container {
            height: 400px;
            overflow-y: auto;
            padding: 1rem;
            background: white;
            border-radius: 10px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        
        .chat-message {
            margin-bottom: 1rem;
            padding: 0.5rem 1rem;
            border-radius: 15px;
        }
        
        .chat-message.sent {
            background: #E3F2FD;
            margin-left: 20%;
            color: #1976D2;
        }
        
        .chat-message.received {
            background: #F5F5F5;
            margin-right: 20%;
            color: #333;
        }
        
        .notification-badge {
            background-color: #f44336;
            color: white;
            padding: 2px 8px;
            border-radius: 10px;
            font-size: 0.7rem;
            position: absolute;
            top: -5px;
            right: -5px;
        }
        
        /* Amélioration des formulaires */
        .stTextInput input, .stTextArea textarea {
            border-radius: 8px;
            border: 1px solid #ddd;
            padding: 0.5rem;
            transition: border-color 0.2s ease;
        }
        
        .stTextInput input:focus, .stTextArea textarea:focus {
            border-color: #1E88E5;
            box-shadow: 0 0 0 2px rgba(30,136,229,0.2);
        }
        
        .stButton button {
            border-radius: 20px;
            padding: 0.5rem 2rem;
            background-color: #1E88E5;
            border: none;
            color: white;
            font-weight: 500;
            transition: transform 0.2s ease;
        }
        
        .stButton button:hover {
            transform: translateY(-1px);
        }
        
        .stSelectbox select {
            border-radius: 8px;
            border: 1px solid #ddd;
        }
        
        /* Menu de navigation */
        .nav-link {
            border-radius: 8px;
            margin: 5px 0;
            padding: 0.5rem 1rem;
            transition: background-color 0.2s ease;
        }
        
        .nav-link:hover {
            background-color: #f0f2f6;
        }
        
        .nav-link.active {
            background-color: #1E88E5;
            color: white;
        }
        
        /* Timeline */
        .timeline {
            border-left: 2px solid #1E88E5;
            padding-left: 20px;
            margin-left: 10px;
        }
        
        .timeline-item {
            position: relative;
            margin-bottom: 1.5rem;
        }
        
        .timeline-item::before {
            content: '';
            position: absolute;
            left: -26px;
            top: 0;
            width: 12px;
            height: 12px;
            border-radius: 50%;
            background: #1E88E5;
        }
    </style>
    """, unsafe_allow_html=True)

# Fonction pour générer un ID anonyme
def generate_anonymous_id(real_id, salt="LogiLink"):
    return hashlib.sha256(f"{real_id}{salt}".encode()).hexdigest()[:8]

# Classes pour la gestion des données
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

# Initialisation de l'état de session
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
    if 'notifications' not in st.session_state:
        st.session_state['notifications'] = []

# Fonctions pour le tableau de bord
def show_metrics_dashboard(user_type):
    col1, col2, col3, col4 = st.columns(4)
    
    if user_type == "E-commerçant":
        metrics = [
            ("Besoins actifs", len([n for n in st.session_state['needs'] if n.status == "Nouveau"]), "📦"),
            ("Propositions reçues", len(st.session_state['proposals']), "📝"),
            ("En négociation", len([p for p in st.session_state['proposals'] if p.status == "En attente"]), "🤝"),
            ("Taux de réponse", f"{calculate_response_rate()}%", "📊")
        ]
    else:
        metrics = [
            ("Opportunités", len([n for n in st.session_state['needs'] if n.status == "Nouveau"]), "🎯"),
            ("Propositions envoyées", len([p for p in st.session_state['proposals'] if p.provider_id == st.session_state['user_id']]), "📤"),
            ("En attente", len([p for p in st.session_state['proposals'] if p.status == "En attente"]), "⏳"),
            ("Taux d'acceptation", f"{calculate_acceptance_rate()}%", "✅")
        ]
    
    for col, (label, value, icon) in zip([col1, col2, col3, col4], metrics):
        with col:
            st.markdown(f"""
            <div class="metric-container">
                <div style="font-size: 24px;">{icon}</div>
                <div class="metric-value">{value}</div>
                <div class="metric-label">{label}</div>
            </div>
            """, unsafe_allow_html=True)

def calculate_response_rate():
    active_needs = [n for n in st.session_state['needs'] if n.status != "Nouveau"]
    if not active_needs:
        return 0
    return int(len([n for n in active_needs if len(n.proposals) > 0]) / len(active_needs) * 100)

def calculate_acceptance_rate():
    my_proposals = [p for p in st.session_state['proposals'] if p.provider_id == st.session_state['user_id']]
    if not my_proposals:
        return 0
    return int(len([p for p in my_proposals if p.status == "Accepté"]) / len(my_proposals) * 100)

def show_activity_charts():
    col1, col2 = st.columns(2)
    
    with col1:
        # Graphique d'activité sur 7 jours
        dates = pd.date_range(end=datetime.now(), periods=7)
        data = pd.DataFrame({
            'Date': dates,
            'Besoins': [random.randint(1, 10) for _ in range(7)],
            'Propositions': [random.randint(5, 15) for _ in range(7)]
        })
        
        fig = px.line(data, x='Date', y=['Besoins', 'Propositions'],
                     title="Activité des 7 derniers jours")
        fig.update_layout(height=300, margin=dict(l=20, r=20, t=30, b=20))
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Graphique statuts
        status_counts = {
            'Nouveau': len([n for n in st.session_state['needs'] if n.status == "Nouveau"]),
            'En cours': len([n for n in st.session_state['needs'] if n.status == "En cours"]),
            'Finalisé': len([n for n in st.session_state['needs'] if n.status == "Finalisé"]),
            'En attente': len([p for p in st.session_state['proposals'] if p.status == "En attente"])
        }
        
        fig = go.Figure(data=[go.Pie(
            labels=list(status_counts.keys()),
            values=list(status_counts.values()),
            hole=.3,
            marker_colors=['#1976D2', '#F57C00', '#2E7D32', '#C62828']
        )])
        fig.update_layout(title="Répartition des statuts", height=300)
        st.plotly_chart(fig, use_container_width=True)

def create_new_need():
    with st.container():
        st.markdown("""
        <div class="card">
            <h2>📦 Nouveau besoin logistique</h2>
            <p>Les champs marqués d'un * sont obligatoires</p>
        </div>
        """, unsafe_allow_html=True)
        
        with st.form("new_need_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            
            with col1:
                title = st.text_input("Titre *", placeholder="Ex: Transport palettes Paris-Lyon")
                category = st.selectbox("Catégorie *", 
                                      ["Transport", "Stockage", "Préparation", "Manutention", "Autre"])
                volume = st.number_input("Volume estimé (m³) *", min_value=0.0)
                start_date = st.date_input("Date de début *")
            
            with col2:
                location = st.text_input("Zone géographique *", placeholder="Ex: Région Île-de-France")
                urgency = st.select_slider("Niveau d'urgence", 
                                         options=["Basse", "Moyenne", "Haute"])
                weight = st.number_input("Poids estimé (kg) *", min_value=0.0)
                end_date = st.date_input("Date de fin *")
            
            description = st.text_area("Description détaillée *", 
                                     placeholder="Décrivez votre besoin sans mentionner d'informations identifiantes",
                                     height=150)
            
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                submit = st.form_submit_button("📤 Publier anonymement", use_container_width=True)
            
            if submit:
                if all([title, volume, weight, location, description]):
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
                    st.success(f"✅ Besoin publié avec succès! ID de suivi: {need.anonymous_id}")
                else:
                    st.error("❌ Veuillez remplir tous les champs obligatoires")

def show_my_needs():
    if not st.session_state['needs']:
        st.info("🔍 Vous n'avez pas encore publié de besoins")
        return
    
    needs = [n for n in st.session_state['needs'] if n.user_id == st.session_state['user_id']]
    
    # Filtres
    status_filter = st.multiselect(
        "Filtrer par statut",
        ["Nouveau", "En cours", "Finalisé"],
        default=["Nouveau", "En cours"]
    )
    
    filtered_needs = [n for n in needs if n.status in status_filter]
    
    for need in filtered_needs:
        with st.container():
            st.markdown(f"""
            <div class="card">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <h3>📦 {need.title}</h3>
                    <span class="status-badge status-{need.status.lower()}">{need.status}</span>
                </div>
                <p style="color: #666;">ID: {need.anonymous_id}</p>
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; margin: 1rem 0;">
                    <div>
                        <p><strong>Volume:</strong> {need.volume} m³</p>
                        <p><strong>Poids:</strong> {need.weight} kg</p>
                        <p><strong>Localisation:</strong> {need.location}</p>
                    </div>
                    <div>
                        <p><strong>Début:</strong> {need.start_date}</p>
                        <p><strong>Fin:</strong> {need.end_date}</p>
                        <p><strong>Créé le:</strong> {need.created_at.strftime('%d/%m/%Y')}</p>
                    </div>
                </div>
                
                <div class="timeline">
                    <div class="timeline-item">
                        <p>✨ Besoin créé le {need.created_at.strftime('%d/%m/%Y à %H:%M')}</p>
                    </div>
            """, unsafe_allow_html=True)
            
            # Affichage des propositions
            proposals = [p for p in st.session_state['proposals'] if p.need_id == need.id]
            
            if proposals:
                st.markdown(f"### 📫 Propositions reçues ({len(proposals)})")
                for proposal in proposals:
                    with st.container():
                        st.markdown(f"""
                        <div style="background: #f8f9fa; padding: 1rem; border-radius: 8px; margin: 0.5rem 0;">
                            <div style="display: flex; justify-content: space-between; align-items: center;">
                                <span>Prestataire #{proposal.anonymous_provider_id}</span>
                                <span class="status-badge status-{proposal.status.lower()}">{proposal.status}</span>
                            </div>
                            <p><strong>Prix proposé:</strong> {proposal.price} €</p>
                            <p>{proposal.description}</p>
                            <p style="color: #666; font-size: 0.9rem;">Reçue le {proposal.created_at.strftime('%d/%m/%Y à %H:%M')}</p>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        if proposal.status == "En attente":
                            col1, col2 = st.columns(2)
                            with col1:
                                if st.button("✅ Accepter", key=f"accept_{proposal.id}"):
                                    proposal.status = "Accepté"
                                    need.status = "En cours"
                                    st.success("Proposition acceptée!")
                                    st.rerun()
                            with col2:
                                if st.button("❌ Refuser", key=f"refuse_{proposal.id}"):
                                    proposal.status = "Refusé"
                                    st.info("Proposition refusée")
                                    st.rerun()
            else:
                st.info("Aucune proposition reçue pour le moment")

def show_available_needs():
    if not st.session_state['needs']:
        st.info("🔍 Aucune opportunité disponible pour le moment")
        return
    
    available_needs = [n for n in st.session_state['needs'] if n.status == "Nouveau"]
    
    # Filtres
    col1, col2 = st.columns(2)
    with col1:
        location_filter = st.multiselect(
            "Filtrer par zone",
            list(set([n.location for n in available_needs]))
        )
    with col2:
        sort_by = st.selectbox(
            "Trier par",
            ["Date (plus récent)", "Date (plus ancien)", "Volume (croissant)", "Volume (décroissant)"]
        )
    
    # Appliquer les filtres
    filtered_needs = available_needs
    if location_filter:
        filtered_needs = [n for n in filtered_needs if n.location in location_filter]
    
    # Trier les besoins
    if sort_by == "Date (plus récent)":
        filtered_needs.sort(key=lambda x: x.created_at, reverse=True)
    elif sort_by == "Date (plus ancien)":
        filtered_needs.sort(key=lambda x: x.created_at)
    elif sort_by == "Volume (croissant)":
        filtered_needs.sort(key=lambda x: x.volume)
    elif sort_by == "Volume (décroissant)":
        filtered_needs.sort(key=lambda x: x.volume, reverse=True)
    
    for need in filtered_needs:
        with st.container():
            st.markdown(f"""
            <div class="card">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <h3>🎯 Opportunité #{need.anonymous_id}</h3>
                    <span class="status-badge status-new">Nouveau</span>
                </div>
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; margin: 1rem 0;">
                    <div>
                        <p><strong>Volume:</strong> {need.volume} m³</p>
                        <p><strong>Poids:</strong> {need.weight} kg</p>
                        <p><strong>Localisation:</strong> {need.location}</p>
                    </div>
                    <div>
                        <p><strong>Début:</strong> {need.start_date}</p>
                        <p><strong>Fin:</strong> {need.end_date}</p>
                        <p><strong>Publié le:</strong> {need.created_at.strftime('%d/%m/%Y')}</p>
                    </div>
                </div>
                <p><strong>Description:</strong> {need.description}</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Formulaire de proposition
            with st.form(key=f"proposal_form_{need.id}"):
                st.markdown("### 💼 Faire une proposition")
                col1, col2 = st.columns(2)
                with col1:
                    price = st.number_input("Prix proposé (€) *", min_value=0.0)
                    completion_time = st.number_input("Délai de réalisation (jours)", min_value=1)
                
                with col2:
                    availability = st.date_input("Date de disponibilité")
                    guarantee = st.selectbox("Garantie proposée", 
                                          ["Standard", "Premium", "Sur-mesure"])
                
                proposal_description = st.text_area("Description de votre proposition *",
                                                  placeholder="Détaillez votre offre sans mentionner d'informations identifiantes")
                
                submit_col1, submit_col2, submit_col3 = st.columns([1, 2, 1])
                with submit_col2:
                    if st.form_submit_button("📤 Envoyer la proposition", use_container_width=True):
                        if price > 0 and proposal_description:
                            proposal = LogisticsProposal(
                                need_id=need.id,
                                provider_id=st.session_state['user_id'],
                                price=price,
                                description=proposal_description
                            )
                            st.session_state['proposals'].append(proposal)
                            st.success("✅ Proposition envoyée avec succès!")
                            st.rerun()
                        else:
                            st.error("❌ Veuillez remplir tous les champs obligatoires")

def show_my_proposals():
    my_proposals = [p for p in st.session_state['proposals'] 
                   if p.provider_id == st.session_state['user_id']]
    
    if not my_proposals:
        st.info("📭 Vous n'avez pas encore fait de propositions")
        return
    
    # Filtres
    status_filter = st.multiselect(
        "Filtrer par statut",
        ["En attente", "Accepté", "Refusé"],
        default=["En attente", "Accepté"]
    )
    
    filtered_proposals = [p for p in my_proposals if p.status in status_filter]
    
    for proposal in filtered_proposals:
        need = next((n for n in st.session_state['needs'] if n.id == proposal.need_id), None)
        if need:
            st.markdown(f"""
            <div class="card">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <h3>💼 Proposition #{proposal.anonymous_id}</h3>
                    <span class="status-badge status-{proposal.status.lower()}">{proposal.status}</span>
                </div>
                <p>Pour le besoin: {need.title} (#{need.anonymous_id})</p>
                <div style="background: #f8f9fa; padding: 1rem; border-radius: 8px; margin: 1rem 0;">
                    <p><strong>Prix proposé:</strong> {proposal.price} €</p>
                    <p><strong>Description:</strong> {proposal.description}</p>
                    <p style="color: #666;">Envoyée le {proposal.created_at.strftime('%d/%m/%Y à %H:%M')}</p>
                </div>
            </div>
            """, unsafe_allow_html=True)

def show_messages():
    st.markdown("""
    <div class="card">
        <h2>💬 Messagerie sécurisée</h2>
        <p>Échangez de manière anonyme avec vos contacts</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 3])
    
    with col1:
        st.markdown("""
        <div class="card">
            <h3>Conversations</h3>
            <div style="color: #666; text-align: center; padding: 1rem;">
                Aucune conversation active
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="card" style="height: 500px; display: flex; flex-direction: column;">
            <div style="flex-grow: 1; padding: 1rem; text-align: center; color: #666;">
                <p style="margin-top: 200px;">Sélectionnez une conversation pour commencer</p>
            </div>
            <div style="padding: 1rem; border-top: 1px solid #eee;">
                <input type="text" placeholder="Écrivez votre message..." 
                       style="width: 100%; padding: 0.5rem; border-radius: 20px; border: 1px solid #ddd;">
            </div>
        </div>
        """, unsafe_allow_html=True)

def show_ecommercant_dashboard():
    selected = option_menu(
        menu_title=None,
        options=["Dashboard", "Nouveau besoin", "Mes besoins", "Messages"],
        icons=["house", "plus-circle", "list-check", "chat"],
        orientation="horizontal"
    )
    
    if selected == "Dashboard":
        show_metrics_dashboard("E-commerçant")
        show_activity_charts()
    elif selected == "Nouveau besoin":
        create_new_need()
    elif selected == "Mes besoins":
        show_my_needs()
    elif selected == "Messages":
        show_messages()

def show_logisticien_dashboard():
    selected = option_menu(
        menu_title=None,
        options=["Dashboard", "Opportunités", "Mes propositions", "Messages"],
        icons=["house", "search", "clipboard-check", "chat"],
        orientation="horizontal"
    )
    
    if selected == "Dashboard":
        show_metrics_dashboard("Logisticien")
        show_activity_charts()
    elif selected == "Opportunités":
        show_available_needs()
    elif selected == "Mes propositions":
        show_my_proposals()
    elif selected == "Messages":
        show_messages()

def main():
    custom_css()
    init_session_state()
    
    # Sidebar avec connexion
    with st.sidebar:
        if not st.session_state['login_status']:
            st.markdown("""
            <div style="text-align: center; padding: 1rem;">
                <h2>👋 Bienvenue sur LogiLink</h2>
                <p>La première marketplace logistique anonyme</p>
            </div>
            """, unsafe_allow_html=True)
            
            user_type = st.radio("Je suis un:", ["E-commerçant", "Logisticien"])
            with st.form("login_form"):
                email = st.text_input("Email")
                password = st.text_input("Mot de passe", type="password")
                submit = st.form_submit_button("Se connecter", use_container_width=True)
                
                if submit:
                    st.session_state['login_status'] = True
                    st.session_state['user_type'] = user_type
                    st.session_state['user_id'] = str(uuid.uuid4())
                    st.success("✅ Connexion réussie!")
                    st.rerun()
        else:
            st.markdown(f"""
            <div style="text-align: center; padding: 1rem;">
                <h3>👤 Mon profil</h3>
                <p>{st.session_state['user_type']}</p>
                <p style="color: #666;">ID: {generate_anonymous_id(st.session_state['user_id'])}</p>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button("🚪 Déconnexion", use_container_width=True):
                for key in st.session_state.keys():
                    del st.session_state[key]
                st.rerun()

    # Contenu principal
    if not st.session_state['login_status']:
        st.markdown("""
        <div class="hero">
            <h1>🚚 LogiLink Anonymous</h1>
            <p style="font-size: 1.2rem;">La première marketplace logistique 100% anonyme</p>
            <p>Échangez en toute confidentialité avec vos futurs partenaires logistiques</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Section fonctionnalités
        st.markdown("### Comment ça marche?")
        col1, col2, col3 = st.columns(3)
        features = [
            ("🔒 Publication anonyme", 
             "Publiez vos besoins logistiques en toute confidentialité"),
            ("🤝 Mise en relation", 
             "Échangez de manière sécurisée avec des prestataires vérifiés"),
            ("✅ Contrôle total", 
             "Gardez le contrôle sur vos informations sensibles")
        ]
        
        for col, (title, desc) in zip([col1, col2, col3], features):
            with col:
                st.markdown(f"""
                <div class="card">
                    <h3 style="text-align: center;">{title}</h3>
                    <p style="text-align: center;">{desc}</p>
                </div>
                """, unsafe_allow_html=True)
    else:
        if st.session_state['user_type'] == "E-commerçant":
            show_ecommercant_dashboard()
        else:
            show_logisticien_dashboard()

if __name__ == "__main__":
    main()
