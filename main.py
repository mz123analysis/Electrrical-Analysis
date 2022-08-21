import pandas as pd
import requests
import seaborn as sb
import matplotlib.pyplot as plt
from scipy import stats

sb.set_theme(style='whitegrid')

api_key = "L3ikibOADDxwNC5GkAyg8gQ1rfjiNpOgJyHPnBsc"

def api_get(seriesID):
    r = requests.get('http://api.eia.gov/series/data?api_key=' + api_key +
                     '&series_id=' + seriesID)
    j = r.json()

    df = pd.DataFrame(j.get('series_data')[0].get('data'))
    df[0] = pd.to_datetime(df[0], format='%Y%m', errors='coerce') # Change the date given to a date format for viz
    df = df.dropna() #Removes rows with NA
    df = df.drop_duplicates() #Remove rows that are duplicated

    return df

if __name__ == '__main__':

    # Getting the amount of Electricity sold or used for residental homes
    r = requests.get('http://api.eia.gov/series/data?api_key=' + api_key +
                     '&series_id=ELEC.SALES.NY-ALL.M')
    j = r.json()

    df = pd.DataFrame(j.get('series_data')[0].get('data'))
    df.columns = ['Date', 'Sales (Million kWh)']
    df.set_index('Date', inplace=True)

    # Getting Pricing of electrical data for residental homes
    r = requests.get('http://api.eia.gov/series/data?api_key=' + api_key +
                     '&series_id=ELEC.PRICE.NY-ALL.M')
    j2 = r.json()
    df1 = pd.DataFrame(j2.get('series_data')[0].get('data'))
    df1.columns = ['Date', 'Price in cents']
    df1.set_index('Date', inplace=True)

    # Combining the two dataframes. Since they are the same date format, I can just concat sideways.
    price_sold = pd.concat([df, df1], axis=1)
    price_sold = price_sold.reset_index()

    price_sold['Date'] = pd.to_datetime(price_sold['Date'], format='%Y%m', errors='coerce')
    print(price_sold.corr())
    # Getting prices of natural gas since it is one of the largest way NYC produces electricity
    r = requests.get('http://api.eia.gov/series/data?api_key=' + api_key +
                     '&series_id=ELEC.COST.NG-NY-98.M')
    j = r.json()

    NY_gas_price = pd.DataFrame(j.get('series_data')[0].get('data'))
    NY_gas_price.columns = ['Date', 'Price of Gas ($ per mcf)']

    # Getting what sources are used in electrical generation
    r = requests.get('http://api.eia.gov/series/data?api_key=' + api_key +
                     '&series_id=ELEC.CONS_EG.NG-NY-99.M')
    j = r.json()

    consumption_gas = pd.DataFrame(j.get('series_data')[0].get('data'))
    consumption_gas.columns = ['Date', 'Consumptions (thousand Mcf)']

    r = requests.get('http://api.eia.gov/series/data?api_key=' + api_key +
                     '&series_id=ELEC.CONS_EG.PC-NY-99.M')
    j = r.json()
    consumption_pc = pd.DataFrame(j.get('series_data')[0].get('data'))
    consumption_pc.columns = ['Date', 'Consumption (thousand tons)']

    r = requests.get('http://api.eia.gov/series/data?api_key=' + api_key +
                     '&series_id=ELEC.CONS_EG.COW-NY-99.M')
    j = r.json()
    consumption_coal = pd.DataFrame(j.get('series_data')[0].get('data'))
    consumption_coal.columns = ['Date', 'Consumption (thousand tons)']

    r = requests.get('http://api.eia.gov/series/data?api_key=' + api_key +
                     '&series_id=ELEC.CONS_EG.PEL-NY-99.M')
    j = r.json()
    consumption_pl = pd.DataFrame(j.get('series_data')[0].get('data'))
    consumption_pl.columns = ['Date', 'thousand barrels']

    consumption_pl['Date'] = pd.to_datetime(consumption_pl['Date'], format='%Y%m', errors='coerce')
    consumption_coal['Date'] = pd.to_datetime(consumption_coal['Date'], format='%Y%m', errors='coerce')
    consumption_gas['Date'] = pd.to_datetime(consumption_gas['Date'], format='%Y%m', errors='coerce')
    consumption_pc['Date'] = pd.to_datetime(consumption_pc['Date'], format='%Y%m', errors='coerce')
    NY_gas_price['Date'] = pd.to_datetime(NY_gas_price['Date'], format='%Y%m', errors='coerce')
    
    # Cleaning and Visualization of our data
    # First visualization: Prices of Electricity over the years
    print(price_sold.isnull().sum())
    print(price_sold.duplicated().sum())
    # No null or duplicated values in our data
    sb.set_theme(style='whitegrid')

    sb.lineplot(x='Date', y='Price in cents',
                data=price_sold)
    plt.show()

    # Second Visualization: Electricity Usage in Households throughout the year
    sb.lineplot(x="Date", y="Sales (Million kWh)",
                   data=price_sold)
    plt.show()

    # Seeing if there is a relationship between Price and Amount of Sales
    sb.scatterplot(x='Price in cents', y="Sales (Million kWh)",
                    data=price_sold)
    plt.show()
    
    # First the amount of consumption of fossil fuel
    sb.lineplot(x="Date", y="thousand barrels",
                data=consumption_pl)
    plt.show()

    sb.lineplot(x="Date", y="Consumption (thousand tons)",
                data=consumption_coal)
    plt.show()

    sb.lineplot(x="Date", y="Consumption (thousand tons)",
                data=consumption_pc)
    plt.show()

    sb.lineplot(x="Date", y="Consumptions (thousand Mcf)",
                data=consumption_gas)
    plt.show()
    
    sb.lineplot(x='Date', y='Price of Gas ($ per mcf)',
                data=NY_gas_price)
    plt.show()

    sb.scatterplot(y=price_sold["Price in cents"], x=NY_gas_price["Price of Gas ($ per mcf)"])
    plt.show()
    
    # Question 5- Are similar trends happening in other states (Cali and Louisiana

    cali_price = api_get('ELEC.PRICE.CA-ALL.M')
    cali_sales = api_get('ELEC.SALES.CA-RES.M')
    cali_NG_usage = api_get('ELEC.RECEIPTS.NG-CA-98.M') # Usage of NG
    cali_coal_usage = api_get('ELEC.RECEIPTS.COW-CA-98.M') #Usage of Coal (NONE)
    cali_PL_usage = api_get('ELEC.RECEIPTS.PEL-CA-98.M') # Usage of PL (NONE)
    cali_PC_usage = api_get('ELEC.RECEIPTS.PC-CA-99.M') #Usage of Petroleum Coke (NONE)
    cali_NG_price = api_get('ELEC.COST.NG-CA-98.M') # Since 2008

    cali_price.columns = ['Date', 'Price (cents)']
    cali_sales.columns = ['Date', 'Sales (Million kWh)']
    cali_NG_usage.columns = ['Date', 'Consumption (Thousand Mcf)']
    cali_NG_price.columns = ['Date', 'Price ($ per Mcf)']

    
    sb.lineplot(x='Date', y='Price (cents)',
                data=cali_price)
    plt.show()
    sb.lineplot(x='Date', y='Sales (Million kWh)',
                data=cali_sales)
    plt.show()

    print(stats.pearsonr(cali_price['Price (cents)'], cali_sales['Sales (Million kWh)']))
    sb.scatterplot(x=cali_price['Price (cents)'], y=cali_sales['Sales (Million kWh)'])
    plt.show()

    sb.lineplot(x='Date', y='Consumption (Thousand Mcf)',
                data=cali_NG_usage)
    plt.show()
    
    sb.lineplot(x='Date', y='Price ($ per Mcf)',
                data=cali_NG_price)
    plt.show()

    sb.scatterplot(x=cali_NG_usage['Consumption (Thousand Mcf)'], y=cali_NG_price['Price ($ per Mcf)'])
    plt.show()

    #Louisiana data
    loui_price = api_get('ELEC.PRICE.LA-ALL.M')
    loui_sales = api_get('ELEC.SALES.LA-ALL.M')
    loui_NG_usage = api_get('ELEC.RECEIPTS.NG-LA-99.M') #Usage of NG
    loui_coal_usage = api_get('ELEC.RECEIPTS.COW-LA-99.M ') #Usage of Coal
    loui_PL_usage = api_get('ELEC.RECEIPTS.PEL-LA-99.M') # Usage of PL (NONE)
    loui_PC_usage = api_get('ELEC.RECEIPTS.PC-LA-99.M') # Usage of PC
    loui_NG_price = api_get('ELEC.COST.NG-LA-99.M') # Since 2008
    loui_coal_price = api_get('ELEC.COST.COW-LA-1.M') # Since 2008
    loui_PC_price = api_get('ELEC.COST.PC-LA-98.M')
    
    loui_price.columns = ['Date', 'Price (cents)']
    loui_sales.columns = ['Date', 'Sales (Million kWh)']
    loui_NG_price.columns = ['Date', 'Price ($ per Mcf)']
    loui_coal_usage.columns = ['Date', 'thousand tons']
    loui_NG_usage.columns = ['Date', 'Consumption (Thousand Mcf)']
    loui_PC_usage.columns = ['Date', 'thousand tons']
    loui_coal_price.columns = ['Date', '$ per ton']
    loui_PC_price.columns = ['Date', '$ per ton' ]

    sb.lineplot(x='Date',y='Price (cents)', data=loui_price)
    plt.show()

    sb.lineplot(x='Date', y='Sales (Million kWh)', data=loui_sales)
    plt.show()

    print(stats.pearsonr(loui_price['Price (cents)'], loui_sales['Sales (Million kWh)']))
    sb.scatterplot(x=loui_price['Price (cents)'], y=loui_sales['Sales (Million kWh)'])
    plt.show()

    sb.lineplot(x='Date', y='Consumption (Thousand Mcf)',
                data=loui_NG_usage)
    plt.show()
    sb.lineplot(x='Date', y='Price ($ per Mcf)',
                data=loui_NG_price)
    plt.show()

    sb.lineplot(x='Date', y='thousand tons',
                data=loui_coal_usage)
    plt.show()

    sb.lineplot(x='Date', y='$ per ton',
                data=loui_coal_price)
    plt.show()
    sb.lineplot(x='Date', y='thousand tons',
                data=loui_PC_usage)
    plt.show()

    sb.lineplot(x='Date', y='$ per ton',
                data=loui_PC_price)
    plt.show()