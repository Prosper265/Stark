import streamlit as st
import pandas as pd
import numpy as np
import json
from pathlib import Path
import plotly.express as px
import plotly.graph_objects as go
import re
import unicodedata

# Set page config
st.set_page_config(page_title="Malawi Food Policy Simulator", layout="wide", page_icon="🌍")

# Get the data directory path
DATA_PATH = Path("data/malawi")

# ----- Data Loading -----
@st.cache_data
def load_data():
    try:
        # Load food composition data
        food_comp = pd.read_csv(DATA_PATH / "food_composition.csv")
        
        # Load consumption data
        consumption = pd.read_csv(DATA_PATH / "initial_cons.csv")
        
        # Load additional Malawi-specific data
        adequacy_df = pd.read_csv(DATA_PATH / "nutrient_adequacy.csv")
        gender_df = pd.read_csv(DATA_PATH / "gender_comparison.csv")
        simulations_df = pd.read_csv(DATA_PATH / "simulations.csv")
        
        return food_comp, consumption, adequacy_df, gender_df, simulations_df
    except FileNotFoundError as e:
        st.error(f"Data file not found: {e}")
        st.info("Please make sure all CSV files are in the data/malawi/ directory")
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

food_comp, consumption, adequacy_df, gender_df, simulations_df = load_data()

# Check if data loaded successfully
if food_comp.empty or consumption.empty:
    st.stop()

# ----- Data Preprocessing -----
def preprocess_data(food_comp, consumption):
    # Clean food composition data
    food_comp.columns = [col.strip() for col in food_comp.columns]
    
    # Extract nutrient information from food composition
    nutrients = [col for col in food_comp.columns if col not in ['Food_code', 'Food_name']]
    
    # Process consumption data - filter for Malawi only
    malawi_consumption = consumption[consumption['Area'] == 'Malawi'].copy()
    malawi_consumption['Item'] = malawi_consumption['Item'].str.title()
    
    return food_comp, malawi_consumption, nutrients

food_comp, malawi_consumption, nutrients = preprocess_data(food_comp, consumption)

# ----- Nutrient Standardization -----
def standardize_nutrient_name(name):
    if pd.isnull(name): return ""
    name = name.lower().strip()
    name = re.sub(r'\([^)]*\)', '', name)
    name = re.sub(r'\s+', ' ', name)
    return name.title()

# Standardize column names in adequacy data
if not adequacy_df.empty:
    adequacy_df.columns = [standardize_nutrient_name(col) for col in adequacy_df.columns]

# ----- UI Organization -----
def dashboard_section(title, explanation):
    st.markdown(f"### {title}")
    with st.expander(f"ℹ️ {title} Details"):
        st.write(explanation)

# ----- Visualization Functions -----
def create_nutrient_radar_chart(sel_nutrients, radar_vals, district):
    fig = go.Figure(data=go.Scatterpolar(r=radar_vals, theta=sel_nutrients, fill='toself', name=district, 
                                        line_color="#1f77b4", fillcolor="rgba(31,119,180,0.2)"))
    fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 100])), 
                     showlegend=True, template="plotly_white", 
                     title=f"Nutrient Profile: {district}", height=400)
    return fig

def create_deficiency_heatmap(adequacy_df):
    nutrient_cols = [col for col in adequacy_df.columns if col != 'District']
    deficiency_data = [{'Nutrient': n, 'Deficiency Rate (%)': (len(adequacy_df[adequacy_df[n] < 80]) / len(adequacy_df)) * 100, 
                       'Severity': 'Critical' if rate > 50 else 'High' if rate > 30 else 'Moderate'} 
                      for n, rate in [(n, (len(adequacy_df[adequacy_df[n] < 80]) / len(adequacy_df)) * 100) for n in nutrient_cols]]
    deficiency_df = pd.DataFrame(deficiency_data).sort_values('Deficiency Rate (%)', ascending=False)
    fig = px.bar(deficiency_df, x='Nutrient', y='Deficiency Rate (%)', color='Severity', 
                 color_discrete_map={'Critical': '#B22222', 'High': '#FF8C00', 'Moderate': '#FFD700'}, 
                 title="Nutrient Deficiency Rates Across Malawi Districts")
    fig.update_layout(template="plotly_white", height=400)
    return fig

def create_interactive_scatter(adequacy_df, x_nutrient, y_nutrient):
    fig = px.scatter(adequacy_df, x=x_nutrient, y=y_nutrient, hover_name='District', 
                     title=f"{x_nutrient} vs {y_nutrient} Adequacy in Malawi Districts", 
                     color_discrete_sequence=['#1f77b4'])
    fig.update_layout(template="plotly_white", height=500)
    return fig

# ----- Intervention Simulation -----
class Intervention:
    def __init__(self, name, nutrient, efficacy, coverage):
        self.name = name
        self.nutrient = nutrient
        self.efficacy = efficacy
        self.coverage = coverage

def simulate_intervention(adequacy_df, intervention, district=None):
    df = adequacy_df.copy() if not district else adequacy_df[adequacy_df['District'] == district].copy()
    if intervention.nutrient in df.columns:
        current = df[intervention.nutrient]
        improvement = intervention.efficacy * intervention.coverage
        df[intervention.nutrient] = np.minimum(100, current + improvement)
    return df

def create_intervention_comparison(adequacy_df, interventions, district):
    baseline = adequacy_df[adequacy_df['District'] == district].melt(id_vars='District', var_name='Nutrient', value_name='Adequacy').assign(Scenario='Baseline')
    intervention_data = []
    for intervention in interventions:
        sim_data = simulate_intervention(adequacy_df, intervention, district).melt(id_vars='District', var_name='Nutrient', value_name='Adequacy').assign(Scenario=intervention.name)
        intervention_data.append(sim_data)
    plot_data = pd.concat([baseline] + intervention_data)
    fig = px.bar(plot_data, x='Nutrient', y='Adequacy', color='Scenario', barmode='group', 
                 title=f"Intervention Impacts: {district}")
    fig.update_layout(template="plotly_white", height=500)
    return fig

# ----- Main App -----
def main():
    st.sidebar.title("Malawi Food Policy Simulator")
    page = st.sidebar.radio("Navigate to:", 
                           ["Overview", "Nutrition Analysis", "Policy Simulation", "Data Explorer"])
    
    # Main content
    if page == "Overview":
        st.title("🌍 Malawi Food Security & Nutrition Dashboard")
        
        st.markdown("""
        This dashboard helps policymakers analyze food consumption patterns in Malawi and simulate interventions 
        to improve nutritional outcomes. Use the navigation panel to explore different aspects of food security.
        """)
        
        # Key metrics
        col1, col2, col3 = st.columns(3)
        
        with col1:
            total_foods = len(malawi_consumption['Item'].unique()) if not malawi_consumption.empty else 0
            st.metric("Food Items Tracked", total_foods)
        
        with col2:
            nutrients_count = len(nutrients) if not food_comp.empty else 0
            st.metric("Nutrients Analyzed", nutrients_count)
        
        with col3:
            if not adequacy_df.empty:
                districts_count = len(adequacy_df['District'].unique())
                st.metric("Districts Analyzed", districts_count)
            else:
                st.metric("Districts Analyzed", 0)
        
        # Top food consumption in Malawi
        st.subheader("Top Food Consumption in Malawi")
        
        if not malawi_consumption.empty:
            top_foods = malawi_consumption.nlargest(10, 'Value')
            fig = px.bar(top_foods, x='Item', y='Value', 
                         title="Top 10 Food Items in Malawi (kg/capita/year)")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("No consumption data available for Malawi")
        
        # Nutrient availability by food group
        st.subheader("Nutritional Composition of Food Groups")
        if not food_comp.empty:
            food_groups = st.multiselect("Select Food Groups", 
                                        food_comp['Food_name'].unique(),
                                        default=food_comp['Food_name'].unique()[:3])
            
            if food_groups:
                selected_foods = food_comp[food_comp['Food_name'].isin(food_groups)]
                nutrient_select = st.selectbox("Select Nutrient", nutrients)
                
                fig = px.bar(selected_foods, x='Food_name', y=nutrient_select,
                             title=f"{nutrient_select} Content in Selected Foods")
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("No food composition data available")

    elif page == "Nutrition Analysis":
        st.title("📊 Malawi Nutrition Analysis")
        
        if not adequacy_df.empty:
            # Nutrient adequacy by district
            st.subheader("Nutrient Adequacy by District")
            
            # Select nutrient to visualize
            nutrient_cols = [col for col in adequacy_df.columns if col != 'District']
            selected_nutrient = st.selectbox("Select Nutrient", nutrient_cols)
            
            if selected_nutrient in adequacy_df.columns:
                fig = px.bar(adequacy_df, x='District', y=selected_nutrient,
                             title=f"{selected_nutrient} Adequacy by District in Malawi")
                fig.update_layout(xaxis_tickangle=-45)
                st.plotly_chart(fig, use_container_width=True)
            
            # Deficiency heatmap
            st.subheader("Nutrient Deficiency Overview in Malawi")
            fig = create_deficiency_heatmap(adequacy_df)
            st.plotly_chart(fig, use_container_width=True)
            
            # Interactive scatter plot
            st.subheader("Nutrient Correlation Analysis")
            col1, col2 = st.columns(2)
            
            with col1:
                x_nutrient = st.selectbox("X-Axis Nutrient", nutrient_cols, key="x_nutrient")
            
            with col2:
                y_nutrient = st.selectbox("Y-Axis Nutrient", nutrient_cols, key="y_nutrient")
            
            fig = create_interactive_scatter(adequacy_df, x_nutrient, y_nutrient)
            st.plotly_chart(fig, use_container_width=True)
            
        else:
            st.warning("No nutrient adequacy data available")
        
        # Gender comparison if available
        if not gender_df.empty:
            st.subheader("Gender-based Nutrient Adequacy")
            
            # Select district and nutrient for gender comparison
            districts = gender_df['District'].unique()
            selected_district = st.selectbox("Select District", districts)
            
            # Get available nutrients from gender data
            gender_nutrients = [col for col in gender_df.columns if col not in ['District', 'Category']]
            
            if gender_nutrients:
                selected_gender_nutrient = st.selectbox("Select Nutrient for Gender Comparison", gender_nutrients)
                
                # Filter data for selected district and nutrient
                district_gender_data = gender_df[gender_df['District'] == selected_district]
                
                if not district_gender_data.empty:
                    # Create bar chart
                    fig = px.bar(district_gender_data, x='Category', y=selected_gender_nutrient, 
                                 color='Category', title=f"{selected_gender_nutrient} by Gender in {selected_district}")
                    st.plotly_chart(fig, use_container_width=True)

    elif page == "Policy Simulation":
        st.title("🎯 Malawi Policy Intervention Simulator")
        
        st.markdown("""
        Simulate the impact of different policy interventions on nutritional outcomes in Malawi.
        Select a district and intervention type to see potential effects.
        """)
        
        if not adequacy_df.empty:
            # Select district
            districts = adequacy_df['District'].unique()
            district = st.selectbox("Select District for Intervention", districts)
            
            # Intervention types
            intervention_type = st.radio(
                "Select Intervention Type",
                ["Supplementation", "Fortification", "Diversification", "Subsidy"]
            )
            
            # Intervention parameters
            st.subheader("Intervention Parameters")
            
            col1, col2 = st.columns(2)
            
            with col1:
                nutrient_cols = [col for col in adequacy_df.columns if col != 'District']
                target_nutrient = st.selectbox("Target Nutrient", nutrient_cols)
                
            with col2:
                intensity = st.slider("Intervention Intensity", 1, 100, 10)
            
            # Simulate intervention effect
            if st.button("Run Simulation"):
                st.subheader("Simulation Results")
                
                # Get baseline data
                baseline_value = adequacy_df[adequacy_df['District'] == district][target_nutrient].values[0]
                
                # Calculate intervention effect based on type
                if intervention_type == "Supplementation":
                    effect = baseline_value * (intensity / 100)
                elif intervention_type == "Fortification":
                    effect = baseline_value * (intensity / 150)
                elif intervention_type == "Diversification":
                    effect = baseline_value * (intensity / 120)
                else:  # Subsidy
                    effect = baseline_value * (intensity / 80)
                
                projected_value = min(100, baseline_value + effect)
                
                # Display results
                col1, col2, col3 = st.columns(3)
                
                col1.metric("Current Adequacy", f"{baseline_value:.1f}%")
                col2.metric("Projected Adequacy", f"{projected_value:.1f}%")
                col3.metric("Improvement", f"+{effect:.1f}%", f"+{(effect/baseline_value*100):.1f}%" if baseline_value > 0 else "N/A")
                
                # Visualize results
                fig = go.Figure()
                fig.add_trace(go.Bar(
                    x=['Current', 'Projected'],
                    y=[baseline_value, projected_value],
                    marker_color=['blue', 'green']
                ))
                fig.update_layout(
                    title=f"Impact of {intervention_type} on {target_nutrient} in {district}",
                    yaxis_title=f"{target_nutrient} Adequacy (%)",
                    yaxis_range=[0, 100]
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                # Show pre-calculated simulation results if available
                if not simulations_df.empty:
                    st.subheader("Pre-calculated Intervention Impacts")
                    country_simulations = simulations_df[simulations_df['country'].str.lower() == 'malawi']
                    
                    if not country_simulations.empty:
                        fig = px.bar(country_simulations, x='intervention', y='adequacy_uplift_points', 
                                     color='intervention', title=f"Pre-calculated Intervention Impacts for Malawi")
                        st.plotly_chart(fig, use_container_width=True)
                    if not district_simulations.empty:
                        fig = px.bar(district_simulations, x='intervention', y='impact', 
                                     color='intervention', title=f"Pre-calculated Intervention Impacts for {district}")
                        st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("No nutrient adequacy data available for simulation")

    elif page == "Data Explorer":
        st.title("🔍 Malawi Data Explorer")
        
        st.markdown("Explore the underlying data used in this dashboard.")
        
        dataset = st.radio("Select Dataset", ["Food Composition", "Consumption Patterns", "Nutrient Adequacy", "Gender Comparison", "Simulations"])
        
        if dataset == "Food Composition":
            st.subheader("Food Composition Data")
            if not food_comp.empty:
                st.dataframe(food_comp, use_container_width=True)
            else:
                st.warning("No food composition data available")
                
        elif dataset == "Consumption Patterns":
            st.subheader("Consumption Patterns Data")
            if not malawi_consumption.empty:
                st.dataframe(malawi_consumption, use_container_width=True)
            else:
                st.warning("No consumption data available")
                
        elif dataset == "Nutrient Adequacy":
            st.subheader("Nutrient Adequacy Data")
            if not adequacy_df.empty:
                st.dataframe(adequacy_df, use_container_width=True)
            else:
                st.warning("No nutrient adequacy data available")
                
        elif dataset == "Gender Comparison":
            st.subheader("Gender Comparison Data")
            if not gender_df.empty:
                st.dataframe(gender_df, use_container_width=True)
            else:
                st.warning("No gender comparison data available")
                
        else:  # Simulations
            st.subheader("Simulations Data")
            if not simulations_df.empty:
                st.dataframe(simulations_df, use_container_width=True)
            else:
                st.warning("No simulations data available")

    # Footer
    st.markdown("---")
    st.markdown(
        """
        <div style='text-align: center'>
            <p>Malawi Food Policy Simulator | For informed decision-making in nutrition security</p>
        </div>
        """,
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()