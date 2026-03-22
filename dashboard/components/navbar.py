import streamlit as st


class Navbar:
    def __init__(self):
        self.title = "Dashboard"
        self.links = {
            "Home": "home",
            "Analytics": "analytics"
        }
        st.session_state.setdefault("page", "home")
        # self.current_page = st.session_state.get("page", "home")
        self.initialize()

    def initialize(self):
        """Initialize the navbar state"""
        self.render()
        
    def navigate(self, page, **kwargs):
        st.session_state["page"] = page
        for k, v in kwargs.items():
            st.session_state[k] = v
    
    def render(self):
        st.markdown("""
        <style>
        .navbar {
            padding: 1rem 0;
            border-bottom: 1px solid #ddd;
            margin-bottom: 2rem;
        }
        </style>
        """, unsafe_allow_html=True)

        col1, col2, col3 = st.columns([2,1,1])

        with col1:
            st.markdown(f"### {self.title}")

        with col2:
            if st.button("🏠 Home", use_container_width=True):
                self.navigate(self.links["Home"])

        with col3:
            if st.button("Analytics", use_container_width=True):
                self.navigate(self.links["Analytics"])
                
    

    
