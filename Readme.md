# Predicting Large Wildfires in the United States

## Overview
Wildfires pose severe health and ecological consequences. In 2021 alone, 58,968 wildfires burned 2.9 million hectares across the United States. Large wildfires (> 125 hectares) in the United States account for more than 95% of the burned area in a given year. Predicting large wildfires is imperative, however, current wildfire predictive models are localized and computationally expensive. This research aims to accurately predict large wildfire occurrences across the United States based on easily available environmental data and using a scalable model.

## Data Sources
1. USDA data for 2060 wildfire occurrences over 20 years, representing 35 million acres burned.
2. NASA MODIS remote sensing data consisting of 1.3 billion satellite observations.
3. Fifth generation ECMWF atmospheric reanalysis (ERA5) data
4. Environmental Justice Data classifying 1956 counties across the United States as environmentally disadvantaged or not

## Methodology
### Feature Selection: 
Six key environmental variables from NASA MODIS were used:
1. Normalized Difference Vegetation Index (NDVI)
2. Enhanced Vegetation Index (EVI)
3. Leaf Area Index (LAI)
4. Fraction of Photosynthetically Active Radiation (FPAR)
5. Land Surface Temperature during the Day (LST Day)
6. Land Surface Temperature during the Night (LST Night)
	
Five atmospheric variables from ERA5 at four pressure levels (300, 500, 700, and 850 hPa) were used:
1. u component of wind
2. v component of wind
3. relative humidity
4. temperature
5. geopotential

Environmental and atmospheric are both drivers of wildfire activity. However, the impact of environmental variables on wildfire spread build up over the long-term while instantaneous atmospheric variables influence wildfire behavior in the short-term.

Therefore, for each wildfire occurrence, MODIS data up to three years prior to the wildfire start date was processed and three annual averages leading up to the wildfire occurrence were computed, as opposed to monthly averages, in order to eliminate seasonal variations within each environmental variable. The 20 instantaneous ERA5 atmospheric reanalysis data at the wildfire start date was obtained. This leads to a total of 38 variables.

### Model Selection: 
The resulting dataset of 38 variables was tested on six different machine learning classification models (Logistic Regression, Decision Tree, Random Forest, XGBoost, KNN, and SVM) to determine their accuracy in predicting large wildfires. The results from the modeling process were evaluated for (i) model accuracy analysis, (ii) model validation, and (iii) identification of important variables among the 18 variables used in this research.

### Model Accuracy Analysis: 
For each of the three models, the accuracy score was determined by how many classifications the model correctly predicted out of the total number of predictions through 10 k-fold cross validation

### Model Validation: 
For each of the six models, two model validation tests were performed.
#### Confusion Matrix: 
For each of the six models, a validation test was performed by comparing the actual wildfire classification to the model’s predicted wildfire classification through its confusion matrix which validates that the data inputted to the model was balanced. 
#### ROC Curve: 
A second validation test was performed by comparing the model’s true positive rate to its false positive rate by analyzing each model’s Receiver Operating Characteristic curve (ROC curve). The true positive rate is the proportion of occurrences that the model correctly predicted as large wildfires out of all large wildfire occurrences. The false positive rate is the proportion of occurrences that the model incorrectly predicted as large wildfires out of all not large wildfire occurrences. The Area Under the Curve (AUC) is a widely used measure of validating a model’s performance. 

### Identification of important variables: 
Variable importance is key to understanding which factors are most significant in large wildfire classification. In order to determine the variables which have the most predictive abilities, permutation variable importance analysis was performed. The permutation variable importance is defined to be the decrease in a model score when a single variable value is randomly shuffled. This procedure breaks the relationship between the variable and the target, thus the drop in the model score is indicative of how much the model depends on the variable. This technique benefits from being model agnostic and can be calculated many times with different permutations of the variables.

### Model Performance: 
The XGBoost Classification model performed the best in predicting large wildfires, with an accuracy of 90.44%.

### Environmental Justice Analysis: 
Recently, the Federal Government established the Justice40 Initiative. Through this initiative, 40% of the benefits of Federal assistance will go to disadvantaged communities so that these overburdened communities can get the vital resources they need. The Justice40 Initiative takes into account several indicators which have been collected from a wide variety of sources, including the U.S. Census Bureau, Environmental Protection Agency, Centers for Disease Control and Prevention, Department of Transportation, Department of Energy, Federal Emer-gency Management Agency, and Department of Housing and Urban Development. These indicators are then used to determine whether a community is disadvantaged.One of the  programs that the Justice40 Initiative covers is “Reducing Wildfire Risk to Tribes, Underserved, and Socially Vulnerable Communities.” With limited budget and resources available, it is imperative to optimize resource al-location judiciously and equitably. To that extent, we performed a spatial analysis de-picting where disadvantaged communities and wildfire predicted by the XGBoost Classification model overlap across the United States. This spatial analysis highlights vulnerable disadvantaged geographical areas which are also impacted by large wildfires (Oklahoma and Northern California), and such should be treated with high priority for federal assistance. This is a key step towards environ-mental justice.

### Training
The input data was split into 10 subsets of data (also known as folds). The models were repeatedly trained on all but one of the folds, and was tested on the one subset that was not used for training. Therefore, the shuffled dataframe was repeatedly split into 90% (9/10 folds) train and 10% (1/10 folds) test ratio and the model’s generalized accuracy score was an average of the 10 trials. The training set was used to fit the machine learning models to predict large wildfires. The testing set was unknown to the model during the training period and used to determine a generalized overall model accuracy.

## Steps:
Software: Python version 3.9.13 on Jupyter Notebooks.

### Data:
1. The consolidated USDA, NASA MODIS, and ERA5 data is stored in the following: wildfire_classes2.csv

### Model Training and Tuning: 
Taking the input data file wildfire_classes2.csv, run the six models (using the Jupyter Notebooks files below) for model accuracy, model validation (confusion matrix and ROC curve), and importance of variables:

1. Logistic Regression: Logistic Regression.ipynb
2. Decision Tree: Decision Tree Classification.ipynb
3. Random Forest: Random Forest Classification.ipynb
4. XGBoost: XGBoost Classification.ipynb
5. KNN: KNN Classification.ipynb
6. SVM: SVM Classification.ipynb

### Environmental Justice Analysis: 
To perform the data analysis run the following: Environmental Justice.ipynb

## Results
The XGBoost Classification model achieved a remarkable accuracy of 90.44% in predicting large wildfires.
The environmental variable LST Night from 1 year before average and the atmospheric variable geopotential at 850 hPa were determined to be the most significant for the XGBoost Classification model.
This model can be used by wildfire safety organizations to predict large wildfire occurrences with high accuracy and employ protective safeguards to prioritize resource allocation for socioeconomically disadvantaged communities.
