# Predicting Large Wildfires in the United States

## Overview

Wildfires pose severe health and ecological consequences. In 2021 alone, 58,968 wildfires burned 7.1 million acres across the United States. Large wildfires (> 300 acres) in the United States account for more than 95% of the burned area in a given year. Predicting large wildfires is imperative, however, current wildfire predictive models are localized and computationally expensive. This research aims to accurately predict large wildfire occurrences across the United States based on easily available environmental data and using a scalable model.

## Data Sources

- USDA data for 2060 wildfire occurrences over 20 years, representing 35 million acres burned.
- NASA MODIS remote sensing data consisting of 1.3 billion satellite observations.
- Copernicus ERA5 reanalysis data.

## Methodology

1. **Feature Selection**: Six key environmental variables were identified, and annual averages over three years leading up to each wildfire occurrence were computed. Addititionally, five key atmospheric variables were identified and were sampled from four pressure levels.

2. **Model Selection**: The resulting dataset of environmental variables was tested on six different machine learning classification models (Logistic Regression, Decision Tree, Random Forest, XGBoost, KNN, and SVM) to determine their accuracy in predicting large wildfires.

3. **Model Performance**: The XGBoost Classification model performed the best in predicting large wildfires, with an accuracy of 90.44%.

4. **Environmental Justice Analysis**: An analysis was performed to identify disadvantaged communities that are also vulnerable to large wildfire occurrences, contributing towards the Environmental Justice (Justice40 Initiative).

## Results

- The XGBoost Classification model achieved a remarkable accuracy of 90.44% in predicting large wildfires.
- This model can be used by wildfire safety organizations to predict large wildfire occurrences with high accuracy and employ protective safeguards to prioritize resource allocation for socioeconomically disadvantaged communities.