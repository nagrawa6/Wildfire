import matplotlib.pyplot as plt
import numpy as np
import xarray as xr
import pandas as pd
import psutil
psutil.virtual_memory()
import geopandas as gpd   #Use pip install geopandas
import folium #conda install -c conda-forge folium
import sqlite3  
import ioexcel
from pathlib import Path

#USE conda install -c conda-forge pyshp
#import shapefile
#If not already installed - use conda install -c conda-forge sqlite

def get_top_fires(nfires):
    conn = sqlite3.connect('data/FPA_FOD_20221014.sqlite')
    #in lieu of dataframe manipulation in the next code block:
    df = pd.read_sql_query("""SELECT *
                       FROM Fires""", conn)
    
    #Get fires which were size >50K acres and occured after 2004 since MODIS data is available after 2000?
    _df_top_fires = df.query("FIRE_SIZE > 50000 & FIRE_YEAR> 2004").sort_values(by='FIRE_SIZE')
    _df_topn_fires = _df_top_fires.head(nfires)
    
    _df_topn = _df_topn_fires[['OBJECTID','LATITUDE', 'LONGITUDE', 'FIRE_YEAR', 'DISCOVERY_DATE', 'DISCOVERY_DOY',
                'FIRE_SIZE', 'STAT_CAUSE_CODE', 'STAT_CAUSE_DESCR' ]]
    
    
    ioexcel.write_to_excel_fires(_df_topn)
    return _df_topn


def plot_fires():
    #Get the connection object
    conn = sqlite3.connect('data/FPA_FOD_20221014.sqlite')
    wildfires = pd.read_sql_query('SELECT FIRE_YEAR, DISCOVERY_DATE, FIRE_SIZE, STAT_CAUSE_DESCR FROM Fires;', con=conn)
    fig, ax = plt.subplots(figsize=(12,6))
    ax.hist(wildfires['FIRE_YEAR'], rwidth=0.9, bins=24);
    ax.set_xlabel('Year')
    ax.set_ylabel('Amount of Fire Incidents')
    plt.title('Incidents by Years')
    
    distribution = wildfires['STAT_CAUSE_DESCR'].value_counts()
    plt.figure(figsize=(6,6))
    plt.title('Distribution by cause', y=-0.15)
    plt.pie(distribution, labels=list(distribution.index[:-2]) + ['', '']);
    plt.axis('equal');
    
    
    #Does the day of week matter?
    #https://developers.arcgis.com/python/samples/historical-wildfire-analysis/
    pd.options.mode.chained_assignment = None 

    wildfires['MONTH'] = pd.DatetimeIndex(wildfires['DISCOVERY_DATE']).month
    wildfires['DAY_OF_WEEK'] = pd.DatetimeIndex(wildfires['DISCOVERY_DATE']).dayofweek
    df_arson = wildfires[wildfires['STAT_CAUSE_DESCR']=='Arson']
    dfa = df_arson['DAY_OF_WEEK'].value_counts()
    df_lightning = wildfires[wildfires['STAT_CAUSE_DESCR']=='Lightning']
    dfl = df_lightning['DAY_OF_WEEK'].value_counts()

    ind = np.arange(7) 
    width = 0.35       

    fig, ax   = plt.subplots(figsize=(10,6))
    arson     = ax.bar(ind, dfa.sort_index(), width, color='coral')
    lightning = ax.bar(ind + width, dfl.sort_index(), width, color='teal')

    ax.set_title('Wildfires by day of week', y=-0.15)
    ax.set_xticklabels(('', 'Mon', 'Tues', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'))
    ax.legend((arson[0], lightning[0]), ('Arson', 'Lightning'), loc=2);
    
    ax = wildfires.plot.scatter(x='FIRE_YEAR', y='FIRE_SIZE')
    
###
#
#  Download the Polygon datafile from https://www.sciencebase.gov/catalog/item/5ee13de982ce3bd58d7be7e7
#  Wildfires_1878_2019_Polygon_Data.zip
#  Unzip to data directory. It contains Shape file, but also needs supporting file.
def plot_us_fires():
    shape = shapefile.Reader("data/US_Wildfires_1878_2019.shp")
    #first feature of the shapefile
    feature = shape.shapeRecords()[0]
    first = feature.shape.__geo_interface__  
    
    sf = shape #shapefile.Reader(sf_path, encoding = 'Shift-JIS')

    fields = [x[0] for x in sf.fields][1:]
    records = sf.records()
    shps = [s.points for s in sf.shapes()]

    sf_df = pd.DataFrame(columns = fields, data = records)
    fig, ax = plt.subplots(figsize=(12,6))
    ax.hist(sf_df['FireYear'], rwidth=0.9, bins=24);
    ax.set_xlabel('Year')
    ax.set_ylabel('Amount of Fire Incidents')
    plt.title('Incidents by Years')
    
    #https://developers.arcgis.com/python/samples/historical-wildfire-analysis/
    #What are the causes of wildfire?
    distribution = sf_df['FireCause'].value_counts()
    plt.figure(figsize=(6,6))
    plt.title('Distribution by cause', y=-0.15)
    plt.pie(distribution, labels=list(distribution.index[:-2]) + ['', '']);
    plt.axis('equal');


def get_bandname_from_file(_file):
    _fp=_file.find('_') 
    _lp = _file.find('.') 
    _site = _file[4:_file.find('_')]
    _band = _file[_fp+1:_lp]
    print("_site", _site, "_band:", _band)
    return _site, _band

def read_modisdata_file(_dir, _file, _band):
    _path = _dir + _file #"../Data/MOD13Q1/1-30/Site1_250m_16_days_EVI.csv"
            
    my_file = Path(_path)
    if my_file.is_file() is False:
        print("File not found:", _path)
        return None
    df  = pd.read_csv(_path, header=None, low_memory=False) #, dtype={cols[0:]:float})
    cols = [0, 1, 3, 4, 5]
    df.drop(df.columns[cols], axis=1, inplace=True)
    df.set_index(2, inplace=True)
    df.loc[:].replace('F', np.nan, inplace=True)
    _nulls = df.isnull().sum().sum()
    _size = df.size
    
    # Convert all columns to numeric so that it mean can be calculated
    cols = df.columns
    df[cols[0:]] = df[cols[0:]].apply(pd.to_numeric, errors='coerce')
    _ds = df.mean(axis=1)
    _ds.rename(_band, inplace=True)
    return _ds, _nulls, _size

def convert_dictionary_to_dataframe(_sites):
    _dfResult = pd.DataFrame()
    for _site in _sites.keys():
        print(_site)
        _bands = _sites.get(_site)
        #print(_bands)
        ser = pd.Series([],dtype=pd.Float64Dtype())
        _df = pd.DataFrame()
        for _band in _bands.keys():

            _ds = _bands.get(_band)
            _df= pd.concat([_df, _ds], axis=1)

        _df['Site']=_site
        _dfResult=pd.concat([_dfResult, _df], axis=0)
    return _dfResult
