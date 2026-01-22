"""
Strategy Marketplace component - displays strategies like a plugin store
"""
import streamlit as st
from trading_engine.strategy_factory import StrategyFactory


def render_strategy_marketplace():
    """Render strategy marketplace with card-based layout"""
    st.title("🏪 Strategy Marketplace")
    st.caption("Browse and add trading strategies to your registry")
    
    # Initialize session state for registry (not enabled status)
    if 'registry_strategies' not in st.session_state:
        st.session_state.registry_strategies = set()
    if 'strategy_params' not in st.session_state:
        st.session_state.strategy_params = {}
    
    # Get strategies (force reload registry)
    StrategyFactory._registry = {}
    strategies = StrategyFactory.all()
    
    st.write(f"DEBUG: Found {len(strategies)} strategies")  # Debug line
    
    if not strategies:
        st.warning("No strategies found in the marketplace")
        return {}, {}
    
    # Filters
    col1, col2, col3 = st.columns([2, 2, 2])
    with col1:
        # Get unique categories
        categories = set()
        for strat_cls in strategies.values():
            try:
                strat = strat_cls()
                categories.add(strat.metadata().get("category", "Uncategorized"))
            except:
                pass
        
        category_filter = st.selectbox(
            "Category",
            ["All"] + sorted(list(categories))
        )
    with col2:
        risk_filter = st.selectbox(
            "Risk Level",
            ["All", "Low", "Medium", "Medium-High", "High"]
        )
    with col3:
        search = st.text_input("🔍 Search", placeholder="Search strategies...")
    
    st.markdown("---")
    
    # Strategy cards
    strategy_params = {}
    
    # Display in grid layout (2 columns)
    for idx, (name, strat_cls) in enumerate(strategies.items()):
        if idx % 2 == 0:
            cols = st.columns(2)
        
        col = cols[idx % 2]
        
        with col:
            try:
                strat = strat_cls()
                meta = strat.metadata()
                
                # Apply filters
                if category_filter != "All" and meta.get("category") != category_filter:
                    continue
                if risk_filter != "All" and meta.get("risk_level") != risk_filter:
                    continue
                if search and search.lower() not in name.lower() and search.lower() not in meta.get("description", "").lower():
                    continue
                
                # Check if already in registry
                is_in_registry = name in st.session_state.registry_strategies
                
                # Strategy card
                with st.container():
                    st.markdown(f"""
                    <div style="border: 1px solid #ddd; border-radius: 10px; padding: 20px; margin-bottom: 20px; background: linear-gradient(135deg, #667eea22 0%, #764ba222 100%);">
                        <div style="display: flex; align-items: center; margin-bottom: 10px;">
                            <span style="font-size: 2.5em; margin-right: 15px;">{meta.get('icon', '📊')}</span>
                            <div>
                                <h3 style="margin: 0; color: #d9e9ff;">{name} {'✅' if is_in_registry else ''}</h3>
                                <span style="background: #667eea; color: white; padding: 2px 8px; border-radius: 12px; font-size: 0.75em; font-weight: 600;">{meta.get('category', 'Uncategorized')}</span>
                                {' <span style="background: #10b981; color: white; padding: 2px 8px; border-radius: 12px; font-size: 0.75em; font-weight: 600; margin-left: 8px;">IN REGISTRY</span>' if is_in_registry else ''}
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Description
                    st.write(meta.get("description", "No description available"))
                    
                    # Metadata row
                    info_col1, info_col2, info_col3 = st.columns(3)
                    with info_col1:
                        risk_color = {
                            "Low": "🟢",
                            "Medium": "🟡",
                            "Medium-High": "🟠",
                            "High": "🔴"
                        }.get(meta.get("risk_level", "Medium"), "⚪")
                        st.caption(f"{risk_color} {meta.get('risk_level', 'Medium')}")
                    with info_col2:
                        st.caption(f"v{meta.get('version', '1.0.0')}")
                    with info_col3:
                        st.caption(f"👤 {meta.get('author', 'Unknown')}")
                    
                    # Tags
                    if meta.get("tags"):
                        tags_html = " ".join([
                            f'<span style="background: #3b5297; padding: 2px 8px; border-radius: 8px; font-size: 0.75em; margin-right: 4px;">#{tag}</span>'
                            for tag in meta.get("tags", [])
                        ])
                        st.markdown(tags_html, unsafe_allow_html=True)
                    
                    st.markdown("<br>", unsafe_allow_html=True)
                    
                    # Add/Remove from registry button
                    if is_in_registry:
                        if st.button(f"🗑️ Remove from Registry", key=f"marketplace_remove_{name}", type="secondary"):
                            st.session_state.registry_strategies.discard(name)
                            if name in st.session_state.strategy_params:
                                del st.session_state.strategy_params[name]
                            st.rerun()
                    else:
                        if st.button(f"➕ Add to Registry", key=f"marketplace_add_{name}", type="primary"):
                            st.session_state.registry_strategies.add(name)
                            st.session_state.strategy_params[name] = strat.default_params()
                            st.success(f"Added {name} to registry!")
                            st.rerun()
                    
                    st.markdown("---")
                    
            except Exception as e:
                st.error(f"Error loading strategy {name}: {str(e)}")
    
    # Summary
    registry_count = len(st.session_state.registry_strategies)
    if registry_count > 0:
        st.info(f"📋 {registry_count} {'strategy' if registry_count == 1 else 'strategies'} in registry")
    
    return strategy_params
