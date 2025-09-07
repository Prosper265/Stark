# 📊 Data Documentation

This document provides detailed information about the datasets used in the Malawi Food Policy Simulator.

## 📁 Dataset Overview

| Dataset | File | Rows | Columns | Description |
|---------|------|------|---------|-------------|
| Food Composition | `food_composition.csv` | 207 | 14 | Nutritional content of foods |
| Consumption | `initial_cons.csv` | 170 | 15 | Food consumption patterns |
| Nutrient Adequacy | `nutrient_adequacy.csv` | 34 | 13 | District-level nutrition status |
| Gender Comparison | `gender_comparison.csv` | 405 | 4 | Male/female nutritional differences |
| Simulations | `simulations.csv` | 11 | 7 | Policy intervention impacts |

## 🍎 Food Composition Data

**File**: `data/malawi/food_composition.csv`

### Structure
- **Food_code**: Unique identifier (MZF0001-MZF0207)
- **Food_name**: Food item name with preparation details
- **Nutrients**: 12 nutritional components

### Nutrient Columns
| Column | Description | Unit | Range |
|--------|-------------|------|-------|
| E_kcal | Energy | kcal | 1-567 |
| Prot_g | Protein | g | 0.0-59.0 |
| RAE_μg | Vitamin A (Retinol Activity Equivalents) | μg | 0-4968 |
| VitC_mg | Vitamin C | mg | 0.0-43.3 |
| Thiamin_mg | Thiamin (Vitamin B1) | mg | 0.0-0.853 |
| Riboflavin_mg | Riboflavin (Vitamin B2) | mg | 0.0-4.19 |
| Nia_mg | Niacin (Vitamin B3) | mg | 0.0-17.52 |
| Fol_μg | Folate | μg | 0-633 |
| VitB12_μg | Vitamin B12 | μg | 0.0-83.13 |
| Ca_mg | Calcium | mg | 0-3000 |
| Fe_mg | Iron | mg | 0.0-17.0 |
| Zn_mg | Zinc | mg | 0.0-6.7 |

### Data Quality
- **Completeness**: 95%+ data completeness
- **Validation**: Cross-referenced with international food databases
- **Source**: Malawi Ministry of Health, FAO

## 🍽️ Consumption Data

**File**: `data/malawi/initial_cons.csv`

### Structure
- **Domain Code**: FBS (Food Balance Sheets)
- **Area**: Country (Malawi, Ghana)
- **Item**: Food item name
- **Value**: Consumption in kg/capita/year

### Key Food Categories
- **Cereals**: Maize, Rice, Wheat, Sorghum, Millet
- **Roots**: Cassava, Potatoes, Sweet Potatoes
- **Legumes**: Beans, Peas, Groundnuts
- **Fruits**: Mangoes, Bananas, Oranges
- **Vegetables**: Tomatoes, Onions, Other vegetables
- **Animal Products**: Meat, Fish, Milk, Eggs

### Malawi-Specific Data
- **Total Items**: 81 food items
- **Time Period**: 2022
- **Source**: FAO Food Balance Sheets

## 🏥 Nutrient Adequacy Data

**File**: `data/malawi/nutrient_adequacy.csv`

### Structure
- **District**: 32 Malawi districts
- **Nutrients**: 12 nutrient adequacy percentages

### Districts Covered
1. Balaka, 2. Blantyre, 3. Blantyre City, 4. Chikwawa
5. Chiradzulu, 6. Chitipa, 7. Dedza, 8. Dowa
9. Karonga, 10. Kasungu, 11. Likoma, 12. Lilongwe
13. Lilongwe City, 14. Machinga, 15. Mangochi, 16. Mchinji
17. Mulanje, 18. Mwanza, 19. Mzimba, 20. Mzuzu City
21. Neno, 22. Nkhata Bay, 23. Nkhotakota, 24. Nsanje
25. Ntcheu, 26. Ntchisi, 27. Phalombe, 28. Rumphi
29. Salima, 30. Thyolo, 31. Zomba, 32. Zomba City

### Nutrient Adequacy Metrics
- **Scale**: 0-100% (percentage of recommended daily intake)
- **Thresholds**: 
  - <80%: Deficient
  - 80-100%: Adequate
  - >100%: More than adequate

## 👥 Gender Comparison Data

**File**: `data/malawi/gender_comparison.csv`

### Structure
- **District**: 32 Malawi districts
- **Category**: Male, Female
- **Nutrients**: 12 nutrient adequacy values

### Key Insights
- **Sample Size**: 405 observations (32 districts × 12 nutrients × 2 genders)
- **Gender Differences**: Significant variations in nutrient adequacy
- **District Variations**: Wide range of nutritional outcomes

## 🎯 Simulation Data

**File**: `data/malawi/simulations.csv`

### Structure
- **country**: Ghana, Malawi
- **intervention**: Intervention type
- **year**: Implementation year
- **baseline_coverage**: Current coverage percentage
- **delta_coverage_pp**: Coverage increase (percentage points)
- **scenario_coverage**: Projected coverage
- **adequacy_uplift_points**: Expected improvement

### Intervention Types
1. **diarrhea_zinc**: Zinc supplementation for diarrhea treatment
2. **iodised_salt**: Salt iodization programs
3. **iron_supp**: Iron supplementation
4. **iron_tablets**: Iron tablet distribution
5. **vit_a**: Vitamin A supplementation

### Malawi Interventions
- **Coverage Range**: 11.5% - 89.8%
- **Improvement Range**: 1.5 - 9.0 adequacy points
- **Years**: 2015-2018

## 🔍 Data Processing

### Cleaning Steps
1. **Column Standardization**: Consistent naming conventions
2. **Missing Value Handling**: Appropriate imputation strategies
3. **Data Type Conversion**: Proper numeric formatting
4. **Outlier Detection**: Statistical validation

### Validation
- **Range Checks**: Nutrient values within expected ranges
- **Consistency Checks**: Cross-dataset validation
- **Quality Metrics**: Completeness and accuracy measures

## 📈 Data Usage

### In the Application
1. **Food Composition**: Powers nutritional analysis and food selection
2. **Consumption**: Drives consumption pattern visualizations
3. **Nutrient Adequacy**: Enables district-level analysis
4. **Gender Data**: Supports gender comparison features
5. **Simulations**: Provides evidence-based policy impacts

### Performance Considerations
- **Caching**: All datasets cached for fast loading
- **Filtering**: Efficient data filtering for large datasets
- **Memory**: Optimized data structures for web deployment

## 🔄 Data Updates

### Update Frequency
- **Food Composition**: Annual updates
- **Consumption**: Annual (FAO releases)
- **Nutrient Adequacy**: Every 2-3 years (survey cycles)
- **Gender Data**: Every 2-3 years (survey cycles)
- **Simulations**: As new evidence becomes available

### Version Control
- **Data Versions**: Tracked in git
- **Change Log**: Documented modifications
- **Backup**: Regular data backups

## 📞 Data Support

For questions about the data:

- **Technical Issues**: Check data validation logs
- **Missing Data**: Review data completeness reports
- **Updates**: Monitor data source releases
- **Quality**: Validate against original sources

---

**Last Updated**: January 2024
**Data Version**: 1.0
**Next Review**: March 2024
