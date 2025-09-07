# 🌍 Malawi Food Policy Simulator

A comprehensive Streamlit dashboard for analyzing food consumption patterns and simulating policy interventions to improve nutritional outcomes in Malawi.

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Data Sources](#data-sources)
- [Installation](#installation)
- [Usage](#usage)
- [Project Structure](#project-structure)
- [Technical Details](#technical-details)
- [Contributing](#contributing)
- [License](#license)

## 🌍 Overview

The Malawi Food Policy Simulator is a data-driven web application designed to help policymakers, researchers, and nutritionists analyze food security and nutritional outcomes in Malawi. The dashboard provides interactive visualizations, policy simulation tools, and comprehensive data exploration capabilities.

### Key Objectives

- **Analyze** current food consumption patterns across Malawi districts
- **Visualize** nutrient adequacy and deficiency rates
- **Simulate** policy intervention impacts on nutritional outcomes
- **Compare** gender-based nutritional differences
- **Explore** comprehensive food composition data
- **Malawi Branding** with national flag integration throughout the interface

## ✨ Features

### 🏠 Overview Dashboard
- **Key Metrics**: Food items tracked, nutrients analyzed, districts covered
- **Interactive Tabs**:
  - **Consumption**: Top food consumption patterns
  - **Composition**: Nutritional content of food groups
  - **Highlights**: District vs nutrient heatmap

### 📊 Nutrition Analysis
- **By District**: Nutrient adequacy across Malawi districts
- **Deficiency Analysis**: Critical nutrient deficiency identification
- **Correlations**: Nutrient relationship analysis
- **Distributions**: Statistical analysis of nutrient adequacy
- **Gender Comparison**: Male vs female nutritional outcomes

### 🎯 Policy Simulation
- **Intervention Types**: Supplementation, Fortification, Diversification, Subsidy
- **Real-time Simulation**: Interactive parameter adjustment
- **Impact Visualization**: Before/after comparison charts
- **Scenario Comparison**: Low, Medium, High intensity scenarios
- **Pre-calculated Results**: Evidence-based intervention impacts

### 🔍 Data Explorer
- **Food Composition**: 207 food items with 12 nutrients
- **Consumption Patterns**: Malawi-specific consumption data
- **Nutrient Adequacy**: District-level nutritional status
- **Gender Data**: Male/female nutritional comparisons
- **Simulations**: Pre-calculated intervention impacts

## 📊 Data Sources

### Primary Datasets

1. **Food Composition** (`food_composition.csv`)
   - 207 food items with complete nutritional profiles
   - 12 nutrients: Energy, Protein, Vitamins A/C/B12, Minerals, etc.
   - Source: Malawi-specific food composition database

2. **Consumption Patterns** (`initial_cons.csv`)
   - Food supply quantities (kg/capita/year)
   - Malawi-specific consumption data
   - Source: FAO Food Balance Sheets

3. **Nutrient Adequacy** (`nutrient_adequacy.csv`)
   - District-level nutritional status (32 districts)
   - 12 nutrient adequacy percentages
   - Source: National nutrition surveys

4. **Gender Comparison** (`gender_comparison.csv`)
   - Male vs female nutritional outcomes
   - District-specific gender analysis
   - Source: Demographic and health surveys

5. **Simulations** (`simulations.csv`)
   - Pre-calculated intervention impacts
   - Evidence-based efficacy data
   - Source: Policy research and impact studies

## 🚀 Installation

### Prerequisites

- Python 3.8 or higher
- pip package manager

### Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd malawi-food-policy-simulator
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**
   ```bash
   streamlit run app.py
   ```

4. **Access the dashboard**
   - Open your browser to `http://localhost:8501`

### Dependencies

```
streamlit>=1.28.0
pandas>=2.0.0
numpy>=1.24.0
plotly>=5.15.0
pathlib
```

## 📖 Usage

### Navigation

The dashboard features a clean sidebar navigation with four main sections:

1. **Overview**: Dashboard summary and key metrics
2. **Nutrition Analysis**: Detailed nutritional analysis tools
3. **Policy Simulation**: Interactive policy impact simulation
4. **Data Explorer**: Raw data exploration and download

### Key Workflows

#### Analyzing Nutrition Patterns
1. Navigate to **Nutrition Analysis**
2. Select a nutrient from the dropdown
3. Choose visualization type (By District, Deficiency, etc.)
4. Explore correlations and distributions

#### Simulating Policy Interventions
1. Go to **Policy Simulation**
2. Select a district and intervention type
3. Adjust intensity parameters
4. Click "Run Simulation" to see projected impacts
5. Compare different scenarios

#### Exploring Data
1. Access **Data Explorer**
2. Choose dataset tab (Food Composition, Consumption, etc.)
3. View and filter data as needed
4. Export data for further analysis

## 📁 Project Structure

```
malawi-food-policy-simulator/
├── app.py                          # Main Streamlit application
├── README.md                       # This documentation
├── requirements.txt                # Python dependencies
├── su.jpg                         # Background image
├── data/
│   └── malawi/
│       ├── food_composition.csv    # Food nutritional data
│       ├── initial_cons.csv        # Consumption patterns
│       ├── nutrient_adequacy.csv   # District nutrition status
│       ├── gender_comparison.csv   # Gender-based analysis
│       └── simulations.csv         # Policy intervention data
└── docs/
    ├── API.md                      # Technical API documentation
    ├── DATA.md                     # Data documentation
    └── DEPLOYMENT.md               # Deployment guide
```

## 🔧 Technical Details

### Architecture

- **Frontend**: Streamlit web framework
- **Data Processing**: Pandas for data manipulation
- **Visualizations**: Plotly for interactive charts
- **Styling**: Custom CSS with responsive design
- **State Management**: Streamlit session state

### Key Components

#### Data Loading (`load_data()`)
- Cached data loading for performance
- Error handling for missing files
- Data validation and cleaning

#### Visualization Functions
- `create_nutrient_radar_chart()`: Radar charts for nutrient profiles
- `create_deficiency_heatmap()`: Heatmaps for deficiency analysis
- `create_interactive_scatter()`: Scatter plots for correlations
- `create_district_nutrient_heatmap()`: District-nutrient heatmaps

#### Policy Simulation
- `Intervention` class: Intervention modeling
- `simulate_intervention()`: Impact calculation
- Real-time parameter adjustment
- Scenario comparison tools

### Color Palette

The application uses a carefully designed color palette:

- **Primary Dark**: `#123024` (Dark green)
- **Primary Darker**: `#081c15` (Darker green)
- **Primary Light**: `#74c69d` (Light green)
- **Background Tint**: `#d8f3dc` (Very light green)

### Responsive Design

- Mobile-friendly interface
- Adaptive layouts for different screen sizes
- Touch-friendly controls
- Optimized for tablets and desktops

## 📈 Performance

### Optimization Features

- **Data Caching**: Streamlit `@st.cache_data` for fast loading
- **Lazy Loading**: Data loaded only when needed
- **Efficient Visualizations**: Plotly for smooth interactions
- **Memory Management**: Optimized data structures

### Browser Compatibility

- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## 🚀 Deployment

### Local Development
```bash
streamlit run app.py --server.port 8501
```

### Production Deployment

#### Streamlit Cloud
1. Push code to GitHub
2. Connect to Streamlit Cloud
3. Deploy with one click

#### Docker
```dockerfile
FROM python:3.9-slim
COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt
EXPOSE 8501
CMD ["streamlit", "run", "app.py"]
```

#### Heroku
```bash
# Add Procfile
echo "web: streamlit run app.py --server.port=$PORT --server.address=0.0.0.0" > Procfile

# Deploy
git push heroku main
```

## 🤝 Contributing

### Development Setup

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

### Code Style

- Follow PEP 8 guidelines
- Use type hints where appropriate
- Document functions and classes
- Write clear commit messages

### Testing

```bash
# Run linting
flake8 app.py

# Test data loading
python -c "import app; print('Data loaded successfully')"
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Data Sources**: FAO, Malawi Ministry of Health, National Statistics Office
- **Research**: Nutrition policy research community
- **Technology**: Streamlit, Plotly, Pandas communities
- **Design**: Inspired by modern data visualization best practices

## 📞 Support

For questions, issues, or contributions:

- **Issues**: [GitHub Issues](https://github.com/your-repo/issues)
- **Discussions**: [GitHub Discussions](https://github.com/your-repo/discussions)
- **Email**: [your-email@domain.com]

## 🔄 Version History

- **v1.0.0** (2024-01-XX): Initial release with core functionality
- **v1.1.0** (2024-01-XX): Added gender comparison analysis
- **v1.2.0** (2024-01-XX): Enhanced policy simulation features
- **v1.3.0** (2024-01-XX): Improved data quality and performance

---

**Made with ❤️ for Malawi's nutrition security**
