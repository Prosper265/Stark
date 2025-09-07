# 🔧 API Documentation

This document provides technical details about the Malawi Food Policy Simulator's code structure, functions, and implementation.

## 📁 Project Structure

```
malawi-food-policy-simulator/
├── app.py                    # Main application file
├── requirements.txt          # Python dependencies
├── README.md                # Project overview
├── su.jpg                   # Background image
├── data/malawi/             # Data directory
│   ├── food_composition.csv
│   ├── initial_cons.csv
│   ├── nutrient_adequacy.csv
│   ├── gender_comparison.csv
│   └── simulations.csv
└── docs/                    # Documentation
    ├── API.md
    ├── DATA.md
    └── DEPLOYMENT.md
```

## 🏗️ Architecture Overview

### Core Components

1. **Data Layer**: Data loading, preprocessing, and caching
2. **Visualization Layer**: Chart creation and interactive elements
3. **UI Layer**: Streamlit interface and user interactions
4. **Simulation Layer**: Policy intervention modeling

### Design Patterns

- **MVC Pattern**: Separation of data, logic, and presentation
- **Caching Strategy**: Streamlit `@st.cache_data` for performance
- **Component Architecture**: Modular function design
- **State Management**: Streamlit session state

## 📊 Data Layer

### Data Loading Functions

#### `load_data()`
```python
@st.cache_data
def load_data():
    """Load and cache all datasets"""
    # Returns: food_comp, consumption, adequacy_df, gender_df, simulations_df
```

**Purpose**: Centralized data loading with caching
**Returns**: Tuple of 5 DataFrames
**Caching**: Streamlit cache for performance

#### `preprocess_data(food_comp, consumption)`
```python
def preprocess_data(food_comp, consumption):
    """Clean and standardize data"""
    # Returns: food_comp, malawi_consumption, nutrients
```

**Purpose**: Data cleaning and standardization
**Parameters**:
- `food_comp`: Food composition DataFrame
- `consumption`: Consumption patterns DataFrame
**Returns**: Processed DataFrames and nutrient list

### Data Processing Functions

#### `standardize_nutrient_name(name)`
```python
def standardize_nutrient_name(name):
    """Standardize nutrient column names"""
    # Returns: Cleaned nutrient name
```

**Purpose**: Clean nutrient names for consistency
**Parameters**: `name` (str) - Raw nutrient name
**Returns**: Standardized nutrient name

## 🎨 Visualization Layer

### Chart Creation Functions

#### `create_nutrient_radar_chart(sel_nutrients, radar_vals, district)`
```python
def create_nutrient_radar_chart(sel_nutrients, radar_vals, district):
    """Create radar chart for nutrient profile"""
    # Returns: Plotly Figure object
```

**Purpose**: Radar chart for nutrient profiles
**Parameters**:
- `sel_nutrients`: List of nutrient names
- `radar_vals`: Nutrient values
- `district`: District name
**Returns**: Plotly Figure

#### `create_deficiency_heatmap(adequacy_df)`
```python
def create_deficiency_heatmap(adequacy_df):
    """Create deficiency rate heatmap"""
    # Returns: Plotly Figure object
```

**Purpose**: Visualize nutrient deficiency rates
**Parameters**: `adequacy_df` - Nutrient adequacy DataFrame
**Returns**: Plotly Figure

#### `create_interactive_scatter(adequacy_df, x_nutrient, y_nutrient)`
```python
def create_interactive_scatter(adequacy_df, x_nutrient, y_nutrient):
    """Create interactive scatter plot"""
    # Returns: Plotly Figure object
```

**Purpose**: Correlation analysis between nutrients
**Parameters**:
- `adequacy_df`: Nutrient adequacy DataFrame
- `x_nutrient`: X-axis nutrient
- `y_nutrient`: Y-axis nutrient
**Returns**: Plotly Figure

#### `create_district_nutrient_heatmap(adequacy_df)`
```python
def create_district_nutrient_heatmap(adequacy_df):
    """Create district-nutrient heatmap"""
    # Returns: Plotly Figure object
```

**Purpose**: District vs nutrient adequacy visualization
**Parameters**: `adequacy_df` - Nutrient adequacy DataFrame
**Returns**: Plotly Figure

### UI Components

#### `render_metric_card(title, value, background_color, text_color)`
```python
def render_metric_card(title, value, background_color, text_color):
    """Render custom metric card"""
    # Returns: HTML string
```

**Purpose**: Custom metric card styling
**Parameters**:
- `title`: Card title
- `value`: Card value
- `background_color`: Background color
- `text_color`: Text color
**Returns**: HTML string for rendering

## 🎯 Simulation Layer

### Policy Simulation Classes

#### `Intervention` Class
```python
class Intervention:
    def __init__(self, name, nutrient, efficacy, coverage):
        self.name = name
        self.nutrient = nutrient
        self.efficacy = efficacy
        self.coverage = coverage
```

**Purpose**: Model policy interventions
**Attributes**:
- `name`: Intervention name
- `nutrient`: Target nutrient
- `efficacy`: Intervention effectiveness
- `coverage`: Population coverage

### Simulation Functions

#### `simulate_intervention(adequacy_df, intervention, district)`
```python
def simulate_intervention(adequacy_df, intervention, district):
    """Simulate intervention impact"""
    # Returns: Modified DataFrame
```

**Purpose**: Calculate intervention impacts
**Parameters**:
- `adequacy_df`: Baseline adequacy data
- `intervention`: Intervention object
- `district`: Target district
**Returns**: Modified adequacy DataFrame

#### `create_intervention_comparison(adequacy_df, interventions, district)`
```python
def create_intervention_comparison(adequacy_df, interventions, district):
    """Create intervention comparison chart"""
    # Returns: Plotly Figure object
```

**Purpose**: Compare multiple interventions
**Parameters**:
- `adequacy_df`: Baseline data
- `interventions`: List of interventions
- `district`: Target district
**Returns**: Plotly Figure

## 🎨 UI Layer

### Main Application Function

#### `main()`
```python
def main():
    """Main application function"""
    # Handles navigation and page routing
```

**Purpose**: Application entry point and navigation
**Features**:
- Sidebar navigation
- Page routing
- Session state management
- UI rendering

### Page Functions

#### Overview Page
- Key metrics display
- Interactive tabs
- Consumption visualizations
- Composition analysis

#### Nutrition Analysis Page
- District-based analysis
- Deficiency identification
- Correlation analysis
- Distribution analysis
- Gender comparison

#### Policy Simulation Page
- Intervention selection
- Parameter adjustment
- Real-time simulation
- Impact visualization
- Scenario comparison

#### Data Explorer Page
- Dataset selection
- Data filtering
- Export capabilities
- Raw data display

## ⚙️ Configuration

### Color Palette
```python
PALETTE = {
    "primary_dark": "#123024",
    "primary_darker": "#081c15", 
    "primary_light": "#74c69d",
    "background_tint": "#d8f3dc",
}
```

### Theme Detection
```python
def get_plotly_template():
    """Get appropriate Plotly template"""
    return "plotly_dark" if IS_DARK else "plotly_white"
```

### CSS Styling
- Custom CSS for UI components
- Responsive design
- Theme-aware styling
- Color consistency

## 🔧 Technical Implementation

### Performance Optimizations

#### Caching Strategy
```python
@st.cache_data
def load_data():
    """Cached data loading"""
```

#### Memory Management
- Efficient DataFrame operations
- Lazy loading where possible
- Optimized data structures

#### Error Handling
```python
try:
    # Data loading
except FileNotFoundError as e:
    st.error(f"Data file not found: {e}")
```

### State Management

#### Session State
```python
if "page" not in st.session_state:
    st.session_state.page = PAGES[0]
```

#### Component State
- Form state persistence
- Navigation state
- User preferences

### Data Validation

#### Input Validation
- User input sanitization
- Range checking
- Type validation

#### Data Integrity
- Missing value handling
- Outlier detection
- Consistency checks

## 🧪 Testing

### Unit Tests
```python
def test_data_loading():
    """Test data loading functionality"""
    # Test implementation
```

### Integration Tests
```python
def test_visualization_rendering():
    """Test chart rendering"""
    # Test implementation
```

### Performance Tests
```python
def test_loading_performance():
    """Test application performance"""
    # Test implementation
```

## 🚀 Deployment

### Environment Variables
```bash
STREAMLIT_SERVER_PORT=8501
STREAMLIT_SERVER_ADDRESS=0.0.0.0
```

### Docker Configuration
```dockerfile
FROM python:3.9-slim
COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt
EXPOSE 8501
CMD ["streamlit", "run", "app.py"]
```

### Production Settings
- Gunicorn for production
- Nginx for reverse proxy
- SSL/TLS configuration
- Monitoring and logging

## 📝 Code Style

### Python Standards
- PEP 8 compliance
- Type hints where appropriate
- Docstring documentation
- Clear variable naming

### Function Documentation
```python
def function_name(param1: type, param2: type) -> return_type:
    """
    Brief description of function.
    
    Args:
        param1: Description of parameter
        param2: Description of parameter
        
    Returns:
        Description of return value
        
    Raises:
        ExceptionType: Description of when raised
    """
```

## 🔄 Maintenance

### Regular Updates
- Dependency updates
- Security patches
- Performance improvements
- Feature enhancements

### Monitoring
- Application performance
- Error tracking
- User analytics
- Resource usage

---

**Last Updated**: January 2024
**Version**: 1.0
**Maintainer**: Development Team
