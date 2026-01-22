"""
Sidebar components for dashboard
"""
import streamlit as st
from trading_engine.strategy_factory import StrategyFactory
from trading_engine.config import StrategyConfig


def render_health_check(data_loader):
    """Render health check and stats in sidebar"""
    health = data_loader.health_check()
    if health.get('status') == 'healthy':
        st.success("✅ Dev API Connected")
    else:
        st.error(f"❌ Dev API Error: {health.get('error', 'Unknown')}")
        st.stop()
    
    # Display stats
    stats = data_loader.get_stats()
    if stats:
        st.metric("Total Stocks", stats.get('total_stocks', 0))
        st.metric("Total Records", stats.get('total_records', 0))
        if stats.get('last_date'):
            st.info(f"Latest: {stats['last_date']}")


def render_controls(stocks):
    """Render sidebar controls and return selections"""
    st.sidebar.header("Controls")
    selected = st.sidebar.selectbox("Select stock", stocks, index=0)
    days = st.sidebar.slider("Days of history", 1, 7, 7)
    compare_mode = st.sidebar.checkbox("Compare multiple stocks")
    
    return selected, days, compare_mode


def render_interval_selector():
    """Render interval selector and return selection"""
    st.sidebar.markdown("---")
    st.sidebar.subheader("Chart Interval")
    interval_options = {
        "1 Minute": "1min",
        "5 Minutes": "5min",
        "15 Minutes": "15min",
        "30 Minutes": "30min",
        "1 Hour": "1H",
        "4 Hours": "4H",
        "8 Hours": "8H"
    }
    selected_interval_label = st.sidebar.selectbox(
        "Time Interval",
        options=list(interval_options.keys()),
        index=2  # Default to 15 minutes
    )
    return selected_interval_label, interval_options[selected_interval_label]


def render_strategy_registry():
    """Render strategy registry checkboxes and parameters - synced with marketplace"""
    st.sidebar.markdown("---")
    st.sidebar.header("Strategy Registry")
    
    # Initialize session state if not exists
    if 'registry_strategies' not in st.session_state:
        st.session_state.registry_strategies = set()
    if 'enabled_strategies' not in st.session_state:
        st.session_state.enabled_strategies = {}
    if 'strategy_params' not in st.session_state:
        st.session_state.strategy_params = {}
    
    # Get strategies
    StrategyFactory._registry = {}
    strategies = StrategyFactory.all()
    
    if not strategies:
        st.sidebar.warning("No strategies found")
        return st.session_state.enabled_strategies, st.session_state.strategy_params
    
    # Show registry count
    registry_count = len(st.session_state.registry_strategies)
    st.sidebar.caption(f"📋 {registry_count} strategies in registry")
    
    if registry_count == 0:
        st.sidebar.info("Add strategies from the Marketplace tab")
        return st.session_state.enabled_strategies, st.session_state.strategy_params
    
    # Strategy enablement - only show strategies that are in registry
    enabled_strategies = {}
    for name in st.session_state.registry_strategies:
        if name not in strategies:
            continue
            
        current_enabled = st.session_state.enabled_strategies.get(name, False)
        enabled = st.sidebar.checkbox(
            f"Enable {name}", 
            value=current_enabled,
            key=f"sidebar_strat_{name}",
            help="Enable this strategy for trading signals"
        )
        st.session_state.enabled_strategies[name] = enabled
        enabled_strategies[name] = enabled
    
    # Strategy parameters - editable only for enabled strategies
    st.sidebar.markdown("---")
    st.sidebar.header("Strategy Parameters")
    
    enabled_count = sum(1 for v in enabled_strategies.values() if v)
    if enabled_count > 0:
        st.sidebar.success(f"✅ {enabled_count} enabled")
    else:
        st.sidebar.info("Enable strategies to configure parameters")
    
    strategy_params = {}
    
    # Only show parameters for enabled strategies
    for name in st.session_state.registry_strategies:
        if name not in strategies:
            continue
        
        # Skip if not enabled
        if not enabled_strategies.get(name, False):
            continue
        
        try:
            strat_cls = strategies[name]
            strat = strat_cls()
            
            # Check if methods exist
            if not hasattr(strat, 'default_params') or not hasattr(strat, 'parameter_schema'):
                st.sidebar.warning(f"{name}: Missing parameter methods")
                continue
            
            defaults = strat.default_params()
            schema = strat.parameter_schema()
            
            # Get current params from session or use defaults
            current_params = st.session_state.strategy_params.get(name, defaults)
            
            # Show parameters in expander
            with st.sidebar.expander(f"⚙️ {name}", expanded=True):
                params = {}
                
                for param_name, default_value in defaults.items():
                    meta = schema.get(param_name, {"type": "number", "min": 0, "max": 100})
                    current_value = current_params.get(param_name, default_value)
                    
                    if meta["type"] == "number":
                        params[param_name] = st.number_input(
                            param_name.replace("_", " ").title(),
                            value=float(current_value) if current_value is not None else 0.0,
                            min_value=float(meta.get("min", 0)),
                            max_value=float(meta.get("max", 100)),
                            step=0.01 if isinstance(default_value, float) else 1.0,
                            key=f"sidebar_param_{name}_{param_name}",
                            help=f"Range: {meta.get('min', 0)} - {meta.get('max', 100)}"
                        )
                    else:
                        params[param_name] = st.text_input(
                            param_name.replace("_", " ").title(),
                            value=str(current_value) if current_value is not None else "",
                            key=f"sidebar_param_{name}_{param_name}"
                        )
                
                strategy_params[name] = params
                # Update session state with new values
                st.session_state.strategy_params[name] = params
                
        except Exception as e:
            st.sidebar.error(f"Error loading {name}: {str(e)}")
            continue
    
    return enabled_strategies, strategy_params


def render_footer():
    """Render sidebar footer"""
    st.sidebar.markdown("---")
    st.sidebar.caption("Data Source: Alpaca Markets")
    st.sidebar.caption("Dev API: http://localhost:8000")
