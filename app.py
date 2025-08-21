import streamlit as st
import pandas as pd
import numpy as np
import json
from pathlib import Path
import folium
from streamlit_folium import st_folium
import plotly.graph_objects as go
from scipy.optimize import linprog
import unicodedata
from shapely.geometry import shape
import os
import re

DATA_PATH = Path("data")  # Platform-agnostic

# ----- Nutrient Standardization -----
NUTRIENT_MAPPING = {
    'vitamina': 'Vitamin A',
    'vitamin a': 'Vitamin A',
    'vita': 'Vitamin A',
    'iron': 'Iron',
    'fer': 'Iron',
    'vitaminb12': 'Vitamin B12',
    'vitamin b12': 'Vitamin B12',
    'vitaminb6': 'Vitamin B6',
    'vitamin b6': 'Vitamin B6',
    # Add more mappings as needed
}

def standardize_nutrient_name(name):
    name = name.lower().strip()
    name = re.sub(r'\([^)]*\)', '', name)
    name = re.sub(r'\s+', ' ', name)
    return NUTRIENT_MAPPING.get(name, name.title())

def normalize_name(name):
    if pd.isnull(name):
        return ""
    name = name.lower().strip()
    name = ''.join(c for c in unicodedata.normalize('NFD', name) if unicodedata.category(c) != 'Mn')
    return name

def validate_adequacy_data(df):
    required_columns = ['District']
    if not all(col in df.columns for col in required_columns):
        raise ValueError("Adequacy data missing required columns")
    nutrient_cols = [col for col in df.columns if col != 'District']
    for col in nutrient_cols:
        if df[col].min() < 0 or df[col].max() > 200:
            st.warning(f"Questionable values in {col}")

# ----- UI Organization -----
def dashboard_section(title, explanation):
    st.markdown(f"### {title}")
    with st.expander(f"â„¹ï¸ What does this section represent?"):
        st.write(explanation)

# ----- Map and Colors -----
def get_color(val):
    if pd.isnull(val):
        return "#cccccc"
    try:
        val = float(val)
    except:
        return "#cccccc"
    # ColorBrewer colorblind safe
    if val >= 80: return "#0072B2"
    elif val >= 60: return "#56B4E9"
    elif val >= 40: return "#F0E442"
    else: return "#D55E00"

def add_color_legend():
    st.markdown("""
    <div style="display:flex;flex-direction:row;gap:1em;">
        <div><span style="background-color:#0072B2;width:20px;height:20px;display:inline-block;margin-right:8px;border-radius:4px;"></span> â‰¥ 80%</div>
        <div><span style="background-color:#56B4E9;width:20px;height:20px;display:inline-block;margin-right:8px;border-radius:4px;"></span> 60-79%</div>
        <div><span style="background-color:#F0E442;width:20px;height:20px;display:inline-block;margin-right:8px;border-radius:4px;"></span> 40-59%</div>
        <div><span style="background-color:#D55E00;width:20px;height:20px;display:inline-block;margin-right:8px;border-radius:4px;"></span> < 40%</div>
        <div><span style="background-color:#cccccc;width:20px;height:20px;display:inline-block;margin-right:8px;border-radius:4px;"></span> No data</div>
    </div>
    """, unsafe_allow_html=True)

def get_geojson_centroid(geojson_data):
    try:
        polys = []
        for f in geojson_data['features']:
            try:
                geom = shape(f['geometry'])
                polys.append(geom)
            except Exception:
                continue
        if not polys:
            return [0.0, 0.0]
        union = polys[0]
        for p in polys[1:]:
            union = union.union(p)
        centroid = union.centroid
        return [centroid.y, centroid.x]
    except Exception:
        # fallback
        c = geojson_data['features'][0]['geometry']['coordinates']
        try:
            if geojson_data['features'][0]['geometry']['type'] == "Polygon":
                lon, lat = c[0][0]
            elif geojson_data['features'][0]['geometry']['type'] == "MultiPolygon":
                lon, lat = c[0][0][0]
            else:
                lon, lat = c[0][0]
            return [lat, lon]
        except Exception:
            return [0.0,0.0]

def extract_district_name(feature):
    properties = feature.get('properties', {})
    for key in ["NAME_2", "NAME_1", "name", "district", "DISTRICT", "Name", "NAME"]:
        if key in properties:
            return normalize_name(properties[key])
    return None

@st.cache_data
def compute_district_colors(adequacy_df, nutrient_col, geojson_data):
    colors = {}
    for feature in geojson_data['features']:
        district_name = extract_district_name(feature)
        row = adequacy_df[adequacy_df['District'].apply(normalize_name) == district_name]
        if not row.empty and nutrient_col in row.columns:
            value = row.iloc[0][nutrient_col]
            colors[district_name] = get_color(value)
        else:
            colors[district_name] = "#cccccc"
    return colors

def make_map(geojson_data, adequacy_df, nutrient_col, map_center, zoom_start):
    m = folium.Map(location=map_center, zoom_start=zoom_start, tiles='cartodbpositron', width="100%")
    colors = compute_district_colors(adequacy_df, nutrient_col, geojson_data)
    for feature in geojson_data['features']:
        district_name = extract_district_name(feature)
        color = colors.get(district_name, "#cccccc")
        value = None
        row = adequacy_df[adequacy_df['District'].apply(normalize_name) == district_name]
        if not row.empty and nutrient_col in row.columns:
            value = row.iloc[0][nutrient_col]
            tooltip_text = f"{district_name.title()}: {value:.1f}%"
        else:
            tooltip_text = f"{district_name.title()}: No data"
        folium.GeoJson(
            feature,
            style_function=lambda x, color=color: {"fillColor": color, "color": "black", "weight": 1, "fillOpacity": 0.7},
            highlight_function=lambda x: {"weight": 3, "color": "#666"},
            tooltip=folium.Tooltip(tooltip_text),
        ).add_to(m)
    return m

# ----- Data Loading -----
@st.cache_data(ttl=3600, show_spinner="Loading region data...")
def load_region_data(region_info):
    adequacy_df = pd.DataFrame()
    foodcomp_df = pd.DataFrame()
    population_df = pd.DataFrame()
    geojson_data = None
    # Adequacy
    try:
        if region_info.get("adequacy"):
            adequacy_df = pd.read_csv(region_info["adequacy"])
            validate_adequacy_data(adequacy_df)
    except Exception as e:
        st.error(f"Error loading adequacy data: {str(e)}")
    # Food composition
    try:
        if region_info.get("foodcomp"):
            foodcomp_df = pd.read_csv(region_info["foodcomp"])
            if 'Food' not in foodcomp_df.columns:
                raise ValueError("Food composition missing required column 'Food'")
    except Exception as e:
        st.error(f"Error loading food composition data: {str(e)}")
    # Population
    try:
        if region_info.get("population"):
            population_df = pd.read_csv(region_info["population"])
            if 'District' not in population_df.columns:
                raise ValueError("Population data missing required column 'District'")
    except Exception as e:
        st.error(f"Error loading population data: {str(e)}")
    # GeoJSON
    try:
        if region_info.get("geojson"):
            with open(region_info["geojson"], 'r') as f:
                geojson_data = json.load(f)
    except Exception as e:
        st.error(f"Error loading geojson: {str(e)}")
    return adequacy_df, foodcomp_df, population_df, geojson_data

@st.cache_data
def detect_regions():
    region_dirs = [d for d in DATA_PATH.iterdir() if d.is_dir()]
    regions = {}
    for d in region_dirs:
        flag = d / "flag.png"
        bg = d / "background.jpg"
        adequacy = d / "nutrient_adequacy.csv"
        population = d / "population_data.csv"
        foodcomp = d / "food_composition.csv"
        geojson = d / "districts.geojson"
        regions[d.name] = {
            "name": d.name.title(),
            "flag_path": str(flag) if flag.exists() else "",
            "bg_path": str(bg) if bg.exists() else "",
            "adequacy": adequacy if adequacy.exists() else None,
            "population": population if population.exists() else None,
            "foodcomp": foodcomp if foodcomp.exists() else None,
            "geojson": geojson if geojson.exists() else None
        }
    return regions

def load_flag_bg(flag_path, bg_path):
    if bg_path:
        st.markdown(f"""
        <style>
            body {{
                background-image: url('{bg_path}');
                background-size: cover;
                background-attachment: scroll;
                background-repeat: no-repeat;
                background-position: center;
            }}
            .main-header {{
                font-size:3rem;
                color:#222;
                background:rgba(255,255,255,0.85);
                text-align:center;
                margin-bottom:1rem;
                border-radius:12px;
                padding:1em;
            }}
        </style>
        """, unsafe_allow_html=True)
    if flag_path:
        st.image(flag_path, output_format='PNG', width=64, caption="Region flag")

# ----- Performance: Precompute District Data -----
@st.cache_data
def precompute_district_data(adequacy_df):
    district_data = {}
    for _, row in adequacy_df.iterrows():
        district = row['District']
        nutrient_map = {standardize_nutrient_name(col): row[col] for col in adequacy_df.columns if col != 'District'}
        district_data[normalize_name(district)] = nutrient_map
    return district_data

# ----- Chart Consistency -----
PLOTLY_TEMPLATE = "plotly_white"

# ----- Metrics/Weighted Averages -----
NUTRIENT_WEIGHTS = {
    'Vitamin A': 2,
    'Iron': 1.5,
    # Add more weights
}

def weighted_average(nutrients, vals):
    weights = [NUTRIENT_WEIGHTS.get(n, 1) for n in nutrients]
    return np.average(vals, weights=weights)

def advanced_metrics_display(sel_nutrients, radar_vals):
    if len(radar_vals) == 0:
        st.warning("No nutrient data available for this district and selection.")
        return
    avg_adequacy = weighted_average(sel_nutrients, radar_vals)
    min_idx = np.argmin(radar_vals) if len(radar_vals) > 0 else None
    max_idx = np.argmax(radar_vals) if len(radar_vals) > 0 else None
    min_nutrient = sel_nutrients[min_idx] if min_idx is not None else "N/A"
    min_value = radar_vals[min_idx] if min_idx is not None else "N/A"
    max_nutrient = sel_nutrients[max_idx] if max_idx is not None else "N/A"
    max_value = radar_vals[max_idx] if max_idx is not None else "N/A"
    col1, col2, col3 = st.columns(3)
    col1.metric("Weighted Adequacy", f"{avg_adequacy:.1f}%" if avg_adequacy else "N/A")
    col2.metric("Most Deficient", f"{min_nutrient}: {min_value:.1f}%" if min_nutrient != "N/A" else "N/A")
    col3.metric("Most Adequate", f"{max_nutrient}: {max_value:.1f}%" if max_nutrient != "N/A" else "N/A")
    st.progress(min(max(avg_adequacy/100, 0.0), 1.0))

def advanced_radar_chart(sel_nutrients, radar_vals, district):
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=radar_vals,
        theta=sel_nutrients,
        fill='toself',
        name=district,
        line_color="#0072B2"
    ))
    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
        showlegend=True,
        title=f"Nutrient Adequacy Profile for {district}",
        template=PLOTLY_TEMPLATE
    )
    st.plotly_chart(fig, use_container_width=True)

def advanced_intervention_display(sel_nutrients, gaps, projected):
    st.markdown("**Projected Adequacy After Interventions:**")
    impact_fig = go.Figure()
    impact_fig.add_trace(go.Bar(
        x=sel_nutrients,
        y=gaps.values,
        name="Current",
        marker_color="#D55E00"
    ))
    impact_fig.add_trace(go.Bar(
        x=sel_nutrients,
        y=projected.values,
        name="Projected",
        marker_color="#0072B2"
    ))
    impact_fig.update_layout(
        barmode="group",
        yaxis_title="Adequacy (%)",
        title="Current vs Projected Nutrient Adequacy",
        template=PLOTLY_TEMPLATE
    )
    st.plotly_chart(impact_fig, use_container_width=True)
    diffs = projected.values - gaps.values
    if len(diffs) > 0:
        delta_idx = np.argmax(diffs)
        st.info(f"Biggest improvement: **{sel_nutrients[delta_idx]}** (+{diffs[delta_idx]:.1f}%)", icon="ðŸ”")

def advanced_food_table(solution, foodcomp_df, sel_nutrients):
    if solution:
        st.markdown("##### Recommended Foods/Crops to Promote (with Nutrient Breakdown):")
        foods = list(solution.keys())
        subdf = foodcomp_df[foodcomp_df['Food'].isin(foods)]
        subdf = subdf.copy()
        subdf["Recommended Qty"] = [solution[f] for f in subdf['Food']]
        display_cols = ['Food', 'Recommended Qty'] + [n for n in sel_nutrients if n in subdf.columns]
        st.dataframe(subdf[display_cols], use_container_width=True)
    else:
        st.warning("No intervention solution found. Gaps may be too large or data insufficient.")

# ----- Optimization -----
def diet_optimizer(nutrient_gaps, foodcomp_df, max_food_quantity=500, nutrient_max=None, food_prefs=None):
    nutrients = nutrient_gaps.index.tolist()
    foods = foodcomp_df['Food'].tolist() if not foodcomp_df.empty else []
    nutrients_in_foodcomp = [n for n in nutrients if n in foodcomp_df.columns]
    if not nutrients_in_foodcomp or len(foods) == 0:
        return {}, nutrient_gaps
    A = foodcomp_df[nutrients_in_foodcomp].values.T
    b = 100 - nutrient_gaps[nutrients_in_foodcomp].values
    c = np.ones(len(foods))
    bounds = [(0, max_food_quantity)] * len(foods)
    # Food preferences/allergies
    if food_prefs:
        for i, f in enumerate(foods):
            if f in food_prefs.get("exclude", []):
                bounds[i] = (0, 0)
            if f in food_prefs.get("max_qty", {}):
                bounds[i] = (0, food_prefs["max_qty"][f])
    # Nutrient upper bounds
    A_ub = -A
    b_ub = -b
    if nutrient_max:
        for idx, nutrient in enumerate(nutrients_in_foodcomp):
            max_val = nutrient_max.get(nutrient, 1000)
            A_ub = np.vstack([A_ub, A[idx]])
            b_ub = np.append(b_ub, max_val)
    try:
        res = linprog(c, A_ub=A_ub, b_ub=b_ub, bounds=bounds, method='highs')
    except Exception as e:
        st.warning(f"Optimization failed: {e}")
        solution = {}
        projected = nutrient_gaps
        return solution, projected
    solution = {}
    if res.success:
        for i, qty in enumerate(res.x):
            if qty > 0.01:
                solution[foods[i]] = qty
        projected = nutrient_gaps.copy()
        for idx, nutrient in enumerate(nutrients_in_foodcomp):
            projected[nutrient] = min(100, projected[nutrient] + np.dot(A[idx], res.x))
    else:
        st.warning("Optimization problem infeasible. Please adjust constraints.")
        projected = nutrient_gaps
    return solution, projected

# ----- Population Impact Analysis -----
def population_impact_analysis(solution, population_df, district):
    if not solution or population_df.empty:
        return
    
    # Find population for the district
    district_pop = population_df[population_df['District'].apply(normalize_name) == normalize_name(district)]
    if district_pop.empty:
        st.info("No population data available for impact analysis.")
        return
        
    total_pop = district_pop.iloc[0]['Population']
    st.metric("Population Impact", f"{total_pop:,} people", 
              help="Estimated population that could benefit from these interventions")

# ----- Main Map and Drilldown -----
def advanced_map_and_drilldown(rinfo, adequacy_df, nutrients, sel_nutrient, population_df, foodcomp_df, geojson_data):
    map_center = get_geojson_centroid(geojson_data)
    dashboard_section("District-level Map", "Shows adequacy for the selected nutrient across all districts.")
    add_color_legend()
    with st.spinner("Loading map..."):
        m = make_map(geojson_data, adequacy_df, sel_nutrient, map_center, zoom_start=7)
        map_data = st_folium(m, use_container_width=True, height=500)
    clicked_district = map_data.get("last_active_drawing", None)
    if clicked_district:
        properties = clicked_district["properties"]
        district_name = None
        for key in ["NAME_2", "NAME_1", "name", "district", "DISTRICT", "Name", "NAME"]:
            if key in properties:
                district_name = normalize_name(properties[key])
                break
        if district_name:
            dashboard_section(f"Analysis for {district_name.title()}", "Shows radar chart, metrics, and intervention for the selected district.")
            district_row = adequacy_df[adequacy_df['District'].apply(normalize_name) == district_name]
            if not district_row.empty:
                row = district_row.iloc[0]
                nutrient_map = {standardize_nutrient_name(n): row[n] for n in adequacy_df.columns if n != 'District'}
                radar_vals = [nutrient_map[n] for n in nutrients if n in nutrient_map]
                advanced_radar_chart(nutrients, radar_vals, district_name.title())
                advanced_metrics_display(nutrients, radar_vals)
                
                # Population impact
                population_impact_analysis({}, population_df, district_name)
                
                # Interventions
                gaps = pd.Series([nutrient_map[n] for n in nutrients if n in nutrient_map], index=nutrients)
                with st.spinner("Optimizing diet recommendations..."):
                    solution, projected = diet_optimizer(gaps, foodcomp_df)
                advanced_food_table(solution, foodcomp_df, nutrients)
                advanced_intervention_display(nutrients, gaps, projected)
            else:
                st.warning("No adequacy data for this district.")
    else:
        st.info("Click a district to see detailed analysis.")

# ----- Main App -----
def main():
    st.set_page_config(page_title="Regional Nutrient Dashboard", layout="wide", page_icon="ðŸŒ")
    regions = detect_regions()
    if not regions:
        st.error("No region data found. Please check your data folder structure.")
        return

    with st.sidebar:
        st.markdown("## ðŸŒ Select Region")
        region_keys = list(regions.keys())
        region_names = [regions[k]["name"] for k in region_keys]
        selected_idx = st.selectbox("Region", range(len(region_keys)), format_func=lambda i: region_names[i])
        selected_region = region_keys[selected_idx]
        rinfo = regions[selected_region]

        adequacy_df, foodcomp_df, population_df, geojson_data = load_region_data(rinfo)
        nutrients_raw = [col for col in adequacy_df.columns if col != 'District']
        nutrients = [standardize_nutrient_name(n) for n in nutrients_raw]
        sel_nutrient = st.selectbox("Map Nutrient Overlay", nutrients, index=0)
        show_map = st.checkbox("Show Interactive District Map", value=True)
        show_table = st.checkbox("Show Detailed Table", value=False)
        show_plain = st.checkbox("Show Single-District Analysis", value=True)
        st.write("**Download data:**")
        if not adequacy_df.empty:
            if st.download_button("Nutrient Adequacy CSV", adequacy_df.to_csv(index=False), f"{selected_region}_adequacy.csv"):
                st.success("Download started!")
        if not foodcomp_df.empty:
            if st.download_button("Food Composition CSV", foodcomp_df.to_csv(index=False), f"{selected_region}_foodcomp.csv"):
                st.success("Download started!")
        if not population_df.empty:
            if st.download_button("Population Data CSV", population_df.to_csv(index=False), f"{selected_region}_population.csv"):
                st.success("Download started!")

    load_flag_bg(rinfo["flag_path"], rinfo["bg_path"])

    st.markdown(f"<div class='main-header'>{regions[selected_region]['name']} Nutrient Analysis Dashboard</div>", unsafe_allow_html=True)

    if show_map and geojson_data:
        advanced_map_and_drilldown(rinfo, adequacy_df, nutrients, sel_nutrient, population_df, foodcomp_df, geojson_data)

    if show_plain:
        dist_list = sorted(adequacy_df['District'].unique()) if not adequacy_df.empty else []
        if dist_list:
            sel_district = st.selectbox("Analyze Single District", dist_list)
            norm_sel = normalize_name(sel_district)
            dashboard_section(f"Analysis for {sel_district}", "Shows radar chart, metrics, and intervention for the selected district.")
            district_row = adequacy_df[adequacy_df['District'].apply(normalize_name) == norm_sel]
            if not district_row.empty:
                row = district_row.iloc[0]
                nutrient_map = {standardize_nutrient_name(n): row[n] for n in nutrients_raw}
                radar_vals = [nutrient_map[n] for n in nutrients if n in nutrient_map]
                advanced_radar_chart(nutrients, radar_vals, sel_district)
                advanced_metrics_display(nutrients, radar_vals)
                
                # Population impact
                population_impact_analysis({}, population_df, sel_district)
                
                # Interventions
                gaps = pd.Series([nutrient_map[n] for n in nutrients if n in nutrient_map], index=nutrients)
                with st.spinner("Optimizing diet recommendations..."):
                    solution, projected = diet_optimizer(gaps, foodcomp_df)
                advanced_food_table(solution, foodcomp_df, nutrients)
                advanced_intervention_display(nutrients, gaps, projected)
            else:
                st.warning("No adequacy data for this district.")

    if show_table:
        if not adequacy_df.empty:
            dashboard_section("Full District Data Table", "Shows all raw adequacy data for every district.")
            st.dataframe(adequacy_df, use_container_width=True)
        if not foodcomp_df.empty:
            dashboard_section("Full Food Composition Table", "Shows nutrient breakdown for available foods/crops.")
            st.dataframe(foodcomp_df, use_container_width=True)
        if not population_df.empty:
            dashboard_section("Population Data Table", "Shows population figures for all districts.")
            st.dataframe(population_df, use_container_width=True)

    st.markdown("---")
    st.markdown("""
        <div style='text-align:center; font-size:1.1em;'>
            <b>Nutrient Analysis Dashboard</b> â€¢ Powered by Advanced Optimization Models<br>
        </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
