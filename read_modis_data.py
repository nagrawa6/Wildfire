import pandas as pd
from pathlib import Path
import numpy as np
import ioexcel
import datetime


    
def read_fires_from_excel():
    _df = ioexcel.read_excel_data("Fires_input.xlsx")
    _df= _df[['Site', 'LATITUDE', 'LONGITUDE', 'FIRE_YEAR', 'DISCOVERY_DATE', 'DISCOVERY_DOY',
                    'FIRE_SIZE', 'FIRE_SIZE_CLASS' ]]
    _df['DISCOVERY_DOY']=_df.DISCOVERY_DOY.astype(str)
    _df['DISCOVERY_DOY'] = _df['DISCOVERY_DOY'].str.zfill(3)
    _df["Period"] = "A"+ _df["FIRE_YEAR"].astype(str)+ _df["DISCOVERY_DOY"]
    return _df

def read_bioatmosphere_data_from_excel():
    _df = ioexcel.read_excel_data("bioatmosphere_data.xlsx")
    _df= _df[['Date', 'Site', '250m_16_days_EVI', '250m_16_days_NDVI', 'Fpar_500m', 
          'Lai_500m', 'LST_Day_1km', 'LST_Night_1km']]#, #'scaled_250m_16_days_EVI'] ]
             #'ET_500m','LE_500m','PET_500m', 'PLE_500m', 
    _df.set_index('Site', inplace=True)
    _cols = ["250m_16_days_EVI", "250m_16_days_NDVI", "Fpar_500m", "Lai_500m", "LST_Day_1km", "LST_Night_1km"]
    Sites = _df.fillna(method='ffill')
    ##This step is must since we are collapsiing two consecutive dates into one removing even rows later
    Sites = Sites.sort_values(by=['Site','Date'])
    ###This method is being performed because EVI and NDVI are at intervals of 8 days while rest are at 16 days
    ### We collapse two consecutive rows into one
    #Compute the average of two consecutive rows by using shift method
    _sites_shifted = (Sites[_cols] + Sites[_cols].shift(-1))/2
    #Put the date back in the new dataframe
    _sites_shifted['Date'] = Sites['Date']
    ##Remove even rows since the odd row contains the average of the two rows.
    #_sites_shifted = _sites_shifted.iloc[::2]  
    _sites_shifted = _sites_shifted.loc[_sites_shifted.groupby('Site').cumcount().mod(2).eq(0)] 
    ####Calculate the anomalies of the data band compared to the average over 22 years of data.
    _sites_shifted[_cols] = _sites_shifted[_cols]-_sites_shifted[_cols].mean(axis = 0, skipna = True)
    return _sites_shifted

def convert_modis_to_calendar_dates(row):
    
    _datestring = row[1:5]+"-01-01"
    # format
    _format = '%Y-%m-%d'

    # convert from string format to datetime format
    _date1 = datetime.datetime.strptime(_datestring, _format)
    
    #Get the number of days away from 1st Jan which is stored in 5th through 8th column. It's 3 digit string e.g. '009'
    days_delta = int(row[5:8])
    #days_delta_int = [datetime.timedelta(int(numeric_string)-1) for numeric_string in days_delta_string]
    #print(days_delta_int)
    #Convert last three digit to numberic value and then timedelta so that they can be added to the first day of the year
    # -1 is subtracted to get the exact day which is number of days away from 1st Jan
    
    
    end_date = _date1 + datetime.timedelta(days=days_delta)
    
    # Converting the index as date
    return end_date

def read_modis_data_from_csv():
    import pandas as pd
    #colnames=['Date', 'Site', '250m_16_days_EVI', '250m_16_days_NDVI', 'Fpar_500m', 
    #      'Lai_500m', 'ET_500m','LE_500m','PET_500m', 'PLE_500m', 'LST_Day_1km', 'LST_Night_1km', 'scaled_250m_16_days_EVI'] 

    #Sites = pd.read_csv("bioatmosphere_data.csv", names=colnames, index_col=1, header=0)
    Sites = read_bioatmosphere_data_from_excel()
    #Drop the column which are not used
    #columns_to_drop = ['ET_500m', 'LE_500m', 'PET_500m', 'PLE_500m', 'scaled_250m_16_days_EVI'] #, 'Unknown']
    #Sites.drop(columns_to_drop, axis=1, inplace=True)
    Sites = Sites[Sites['250m_16_days_EVI'].notna()]
    print("Sites:", Sites.shape, Sites.index.unique())
    ## Load the fires into dataframe. We need the date when the fire occured.
    _df = read_fires_from_excel()
    
    Sites_fireOccurenceData = pd.DataFrame()
    for i in Sites.index.unique():
        ##Though index and 'Site' are two different columns, their values are same. This can be collapsed to single column
        _df_site1 = _df.loc[_df['Site']==i]

        _fire_occurence = _df_site1['Period']
        Site1 = Sites.loc[i]
        
        #_fire_occurence.values[0]] contains the date when the fire occured.
        print(Site1['Date'])
        print(_fire_occurence)
              
        Site1_b4fire  = Site1.loc[Site1['Date'] <_fire_occurence.values[0]]
        #Site1_b4fire= Site1_b4fire.tail(12)
        #Site1_b4fire_flatten = Site1_b4fire.tail(12).reset_index(drop=True)
        #Site1_b4fire_flatten = Site1_b4fire.drop(['Date'], axis=1)
        
        Sites_fireOccurenceData = pd.concat([Sites_fireOccurenceData, Site1_b4fire], axis=0)
        #print(i, _fire_occurence)
    
    Sites_fireOccurenceData['Date']=Sites_fireOccurenceData['Date'].apply(convert_modis_to_calendar_dates)

    #Get only the Fire data that we need
    _dfFIRE = _df[['Site', 'LATITUDE', 'LONGITUDE', 'FIRE_SIZE', 'FIRE_SIZE_CLASS', 'DISCOVERY_DATE']]
    _dfFIRE.set_index('Site', inplace=True)

    return _dfFIRE, Sites_fireOccurenceData

def get_3years_b4FireData(_dfSite):
    _siteNum = _dfSite.index.unique()[0]
    
    ##Each site has three rows for 3 years before the fire occured.
    idx_values = ['24-36M before', '12-24M before', '0-12M before']
    _dates = [0,0,0,0]
    #Get the last date and then move 3 years before.
    end_date =  _dfSite["Date"].iloc[-1] #datetime.datetime.strptime(_datestring, _format)
    _dates[3]=end_date
    for i in range (3,0,-1):
        _dates[i-1]= _dates[i] - datetime.timedelta(days=365) 
    _year = pd.DataFrame(columns =_dfSite.columns.values) #, index= idx_values)
    #Get the data for 3 years and take the mean. default is mean for each column
    for i in range(3):
        #print(_dates[i])
        mask = (_dfSite['Date'] > _dates[i]) & (_dfSite['Date'] <= _dates[i+1])
        df_filtered = _dfSite.loc[mask]
        _dfyeartemp = df_filtered.mean(axis=0, skipna = True)
        _year = _year.append(_dfyeartemp, ignore_index=True)
        
    _year=_year.drop(['Date'], axis=1)
    #_year['Site'] = _siteNum
    print("_year.columns:", _year.columns)
    return _year

#This function gets 36 month data before the fire happened.It is collapsed into yearly information 
# e.g.  Year_3 Before occured  Year_2 Before fire occured....Year_1 Before fire occured NDVI EVI, 
def collapse_modis_data(_dfSite):
    print("index:", _dfSite.index.unique()[0])
    _siteNum = _dfSite.index.unique()[0]
    
    _year = get_3years_b4FireData(_dfSite)
    print("_year.columns:", _year.columns)
    
    _arr = _year.to_numpy().flatten()
    columns = ['250m_16_days_EVI', '50m_16_days_NDVI', 'Fpar_500m', 'Lai_500m',
               'LST_Day_1km', 'LST_Night_1km']  #'ET_500m', 'LE_500m', 'PET_500m', 'PLE_500m',
    ##Now flatten this yearly data for 3 years. So effectively will have 3 X Number of parameters in a single row
    # Flattened rows are stored into numpy array which is then converted to DataFrame.
    flattened_columns = []
    #flattened_columns.append(_siteNum)
    for j in range(3):
        for i in range(len(columns)):
            #print(columns[i])
            ##Prefix each yearly data to _<number of the year> so that each column is named differently.
            flattened_columns.append(columns[i] + '-'+str(j))
    _dfSite_flattened = pd.DataFrame(columns=flattened_columns)
    #Create a flattened row for each site and append to _dfSite_flattened DataFrame.
    _dfSite_flattened = _dfSite_flattened.append(pd.DataFrame( [_arr],
                   columns=flattened_columns),
                   ignore_index = True)
    _dfSite_flattened['Site'] = _siteNum
    return _dfSite_flattened