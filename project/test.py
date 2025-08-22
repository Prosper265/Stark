import streamlit as st
import requests
import pandas as pd
import json
import folium
from streamlit_folium import st_folium
from io import BytesIO
import zipfile
from fuzzywuzzy import process
import numpy as np

# Function to fetch data
@st.cache_data
def fetch_adequacy(country):
    api_urls = {
        'Benin': 'https://fs-cor.org/api/benin/fetchAdequacyByNutrientAndDepartment.php?table=benin_income_data',
        'Ghana': 'https://fs-cor.org/api/ghana/fetchAdequacyByNutrientAndDistrict.php',
        'Uganda': 'https://fs-cor.org/api/uganda/fetchAdequacyByNutrientAndDistrict.php',
        'Senegal': 'https://fs-cor.org/api/senegal/fetchAdequacyByNutrientAndDepartment.php?table=senegal_income_data',
        'Malawi': 'https://fs-cor.org/api/malawi/fetchAdequacyByNutrientAndDistrict.php'
    }
    try:
        response = requests.get(api_urls[country], timeout=10)
        response.raise_for_status()
        if response.text.strip():
            return response.json()
    except Exception as e:
        st.error(f"Failed to fetch adequacy data for {country}: {e}")
        return None
@st.cache_data
def fetch_vulnerability(country):
    url = f'https://fs-cor.org/api/fetchVulnerability.php?country={country.lower()}&parameter=cv_index'
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        if response.text.strip():
            return response.json()
    except Exception as e:
        st.error(f"Failed to fetch vulnerability data for {country}: {e}")
        return None
@st.cache_data
def fetch_geojson(country):
    geo_urls = {
        'Benin': 'https://geodata.ucdavis.edu/gadm/gadm4.1/json/gadm41_BEN_1.json',
        'Ghana': 'https://geodata.ucdavis.edu/gadm/gadm4.1/json/gadm41_GHA_1.json',
        'Uganda': 'https://geodata.ucdavis.edu/gadm/gadm4.1/json/gadm41_UGA_1.json',
        'Senegal': 'https://geodata.ucdavis.edu/gadm/gadm4.1/json/gadm41_SEN_1.json',
        'Malawi': 'https://fs-cor.org/assets/data/Malawi/level1.geo.json'
    }
    try:
        response = requests.get(geo_urls[country], timeout=10)
        response.raise_for_status()
        if response.text.strip():
            return response.json()
    except Exception as e:
        st.error(f"Failed to fetch geojson data for {country}: {e}")
        return None
@st.cache_data
def fetch_top5(country):
    url = f'https://fs-cor.org/api/getAllData.php?table={country.lower()}_top5'
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        if response.text.strip():
            return response.json()
    except Exception as e:
        st.error(f"Failed to fetch top5 data for {country}: {e}")
        return None
        response = requests.get(fbs_url, timeout=30)
        response.raise_for_status()
        with zipfile.ZipFile(BytesIO(response.content)) as z:
            with z.open('FoodBalanceSheets_E_All_Data_(Normalized).csv') as f:
                df = pd.read_csv(f, encoding='latin-1')
        return df
    except Exception as e:
        st.error(f"Error loading FBS data: {str(e)}")
        return pd.DataFrame()

@st.cache_data
def load_composition_data():
    comp_url = 'https://www.fao.org/fileadmin/user_upload/faoweb/2020/WAFCT_2019.xlsx'
    try:
        response = requests.get(comp_url, timeout=30)
        response.raise_for_status()
        df = pd.read_excel(BytesIO(response.content), sheet_name='COMPILATION_TABLE', skiprows=2)
        return df
    except Exception as e:
        st.error(f"Error loading composition data: {str(e)}")
        return pd.DataFrame()
        return response.json()
    except:
        return None  # Fallback if not available

@st.cache_data
def load_fbs_data():
    fbs_url = 'https://fenixservices.fao.org/faostat/static/bulkdownloads/FoodBalanceSheets_E_All_Data_(Normalized).zip'
    response = requests.get(fbs_url)
    with zipfile.ZipFile(BytesIO(response.content)) as z:
        # You probably want to extract or read files from the zip here
        # For example:
        # with z.open('FoodBalanceSheets_E_All_Data_(Normalized).csv') as f:
        #     df = pd.read_csv(f, encoding='latin-1')
        pass  # Remove this line and add your zip processing logic

    # Fetch data
    adequacy_data = fetch_adequacy(selected_country)
    vuln_data = fetch_vulnerability(selected_country)
    geo_data = fetch_geojson(selected_country)
    top5 = fetch_top5(selected_country)
fbs_df = load_fbs_data()
comp_df = load_composition_data()

# Check if we have data before processing
if not adequacy_data:
    st.error(f"Unable to load adequacy data for {selected_country}. Please try again later.")
    st.stop()
    # This code is outside of a function and should not use 'return'
    response = requests.get(comp_url)
    df = pd.read_excel(BytesIO(response.content), sheet_name='COMPILATION_TABLE', skiprows=2)
    # Mapping of nutrient names to column names in the composition table
    nutrient_columns = {
        'Zinc': 'ZINC (mg)',
        'Vitamin A': 'VITA_RE (µg)'
    }

    # RDA values (simplified, adult male)
    rda = {
        'Iron': 8,  # mg/day
    'Zinc': 11,  # mg/day
    'Vitamin A': 900  # ug/day
}

# Main app
st.title('Nutrient Gap & Intervention Simulator')

countries = ['Benin', 'Ghana', 'Senegal', 'Uganda', 'Malawi']
selected_country = st.selectbox('Select Country', countries)

# Fetch data
adequacy_data = fetch_adequacy(selected_country)
vuln_data = fetch_vulnerability(selected_country)
geo_data = fetch_geojson(selected_country)
top5 = fetch_top5(selected_country)
fbs_df = load_fbs_data()
comp_df = load_composition_data()

# Process adequacy to DF
adeq_df = pd.DataFrame(adequacy_data)
adeq_df = adeq_df.pivot(index='department' if 'department' in adeq_df.columns else 'district', columns='nutrient', values='adequacy')

# Overall adequacy score
adeq_df['overall'] = adeq_df.mean(axis=1)

# Vulnerability DF
vuln_df = pd.DataFrame(vuln_data)
vuln_df = vuln_df.set_index('region')  # Assume 'region' key

# Join
merged_df = adeq_df.join(vuln_df)

# Map
m = folium.Map(location=[9.5, 2.25] if selected_country == 'Benin' else [0, 0], zoom_start=6)

folium.Choropleth(
    geo_data=geo_data,
    data=merged_df,
    columns=[merged_df.index.name, 'overall'],
    key_on='feature.properties.NAME_1',
    fill_color='YlOrRd',
    fill_opacity=0.7,
    line_opacity=0.2,
    legend_name='Overall Nutrient Adequacy (%)'
).add_to(m)

st_folium(m, width=700, height=500)

# Top 5 crops
if top5:
    top5_df = pd.DataFrame(top5)
    st.bar_chart(top5_df.set_index('crop')['consumption'])
else:
    st.write('Top 5 data not available, using FBS fallback')
    country_fbs = fbs_df[(fbs_df['Area'] == selected_country) & (fbs_df['Element'] == 'Food supply quantity (kg/capita/yr)') & (fbs_df['Year'] == fbs_df['Year'].max())]
    top5_fbs = country_fbs.sort_values('Value', ascending=False).head(5)
    st.bar_chart(top5_fbs.set_index('Item')['Value'])

# Summary
most_deficient = adeq_df.mean().idxmin()
most_vuln = merged_df['cv_index'].idxmax()
st.write(f'Most deficient nutrient: {most_deficient}')
st.write(f'Most vulnerable region: {most_vuln}')

# Nutrient Gap View
selected_region = st.selectbox('Select Region', adeq_df.index)
st.write('Adequacy (%)')
st.radar_chart(adeq_df.loc[selected_region])

st.write(f'Vulnerability Index: {merged_df.loc[selected_region, "cv_index"]}')

# Intervention Simulator
st.header('Intervention Simulator')

# Baseline from FBS
country_fbs = fbs_df[(fbs_df['Area'] == selected_country) & (fbs_df['Element'] == 'Food supply quantity (kg/capita/yr)') & (fbs_df['Year'] == fbs_df['Year'].max())]

# Match items to comp
def match_food(item):
    match = process.extractOne(item.lower(), comp_df['FOOD ITEM (English name)'].str.lower())
    if match[1] > 80:
        return comp_df[comp_df['FOOD ITEM (English name)'].str.lower() == match[0]].iloc[0]
    return None

nutrient_intakes = {}
for _, row in country_fbs.iterrows():
    comp_row = match_food(row['Item'])
    if comp_row is not None:
        g_day = (row['Value'] / 365) * 1000
        for nut, col in nutrient_cols.items():
            intake = (g_day / 100) * comp_row[col]
            if nut not in nutrient_intakes:
                nutrient_intakes[nut] = 0
            nutrient_intakes[nut] += intake

# User inputs
intervention_type = st.selectbox('Intervention Type', ['Promote Crop X', 'Supplementation'])
target_nut = st.selectbox('Target Nutrient', list(nutrient_cols.keys()))
intensity = st.slider('Intensity (%)', 0, 50, 10)

crop_from = st.selectbox('Replace Crop', country_fbs['Item'].unique())
crop_to = st.selectbox('With Crop', country_fbs['Item'].unique())

# Simulate
base_intake = nutrient_intakes[target_nut]

comp_from = match_food(crop_from)
comp_to = match_food(crop_to)
if comp_from is not None and comp_to is not None:
    cons_from = country_fbs[country_fbs['Item'] == crop_from]['Value'].values[0]
    cons_to = country_fbs[country_fbs['Item'] == crop_to]['Value'].values[0]
    replace_amt = (intensity / 100) * cons_from
    new_from = cons_from - replace_amt
    new_to = cons_to + replace_amt
    
    g_day_from = (new_from / 365) * 1000
    g_day_to = (new_to / 365) * 1000
    
    delta_intake = - (g_day_from / 100) * comp_from[nutrient_cols[target_nut]] + (g_day_to / 100) * comp_to[nutrient_cols[target_nut]]
    new_intake = base_intake + delta_intake  # Approximate, since base includes all
    
    st.write(f'Baseline {target_nut} Intake: {base_intake:.2f} per day')
    st.write(f'New {target_nut} Intake: {new_intake:.2f} per day')
    st.write(f'Change: {(new_intake - base_intake) / base_intake * 100:.2f}%')
    
    # Adequacy change (vs RDA)
    base_adeq = (base_intake / rda[target_nut]) * 100
    new_adeq = (new_intake / rda[target_nut]) * 100
    st.write(f'Adequacy Change: {new_adeq - base_adeq:.2f}% points')

# For ML: Simple linear regression to predict adequacy based on vulnerability and consumption
import statsmodels.api as sm

# Prepare data: Use merged_df and some consumption
# Dummy ML for consistency: Predict overall adequacy from cv_index
X = merged_df['cv_index'].values.reshape(-1, 1)
y = merged_df['overall']
model = sm.OLS(y, sm.add_constant(X)).fit()
st.write('ML Model Summary for Predicting Adequacy from Vulnerability')
st.write(model.summary())

# Predict for a hypothetical
hyp_vuln = st.slider('Hypothetical Vulnerability', 0.0, 1.0, 0.3)
pred = model.predict([1, hyp_vuln])[0]
st.write(f'Predicted Adequacy: {pred:.2f}%')