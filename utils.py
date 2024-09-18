
import plotly.graph_objects as go
import pandas as pd
import numpy as np

def calculate_time_weights(df, weight_range=(0.5, 1.0), method='linear'):
    """
    Calculate time-based weights for a DataFrame based on its index.
    
    Parameters:
    df (pd.DataFrame): The DataFrame with a time-based index.
    weight_range (tuple): The range of weights (min_weight, max_weight).
    method (str): The type of weighting ('linear' or 'exponential').
    
    Returns:
    pd.Series: A Series of weights.
    """
    
    # Ensure the index is sorted by time
    df = df.sort_index()
    
    # Calculate the time differences from the most recent observation
    time_deltas = (df.index.max() - df.index).days  # Time delta in days

    # Normalize the time differences to the range [0, 1]
    normalized_time = time_deltas / time_deltas.max()

    # Apply the chosen weighting method
    if method == 'linear':
        # Linear interpolation between weight_range
        weights = weight_range[0] + (weight_range[1] - weight_range[0]) * (1 - normalized_time)
    elif method == 'exponential':
        # Exponential decay based on normalized time
        weights = weight_range[0] + (weight_range[1] - weight_range[0]) * np.exp(-normalized_time)
    else:
        raise ValueError("Invalid method. Choose 'linear' or 'exponential'.")
    
    return pd.Series(weights, index=df.index)


def plot_candlesticks( df, tar_date, ticker):
    df = df.loc[tar_date]
    fig = go.Figure(data=[go.Candlestick(x=df.index, open=df['open'], high=df['high'], low=df['low'], close=df['close'])])
    fig.update_layout( title=ticker, xaxis_title='Date', yaxis_title='Price', xaxis_rangeslider_visible=False) # Hide the range slider )
    fig.show()


def calc_open_close_change(df, colname):

    target_col = colname + '_ON_CHANGE'
    open_col = colname + '_OPEN'
    prev_close_col = colname + '_PREV_CLOSE'
    # Get daily open and close prices
    daily_data = df.resample('B').agg({'open': 'first', 'close': 'last'}).dropna()

    daily_data[open_col] = daily_data['open']
    daily_data[prev_close_col] = daily_data['close'].shift(1)

    # Calculate change from previous close to next day open
    #daily_data[colname] = (daily_data['open'] - daily_data['close'].shift(1))/daily_data['close'].shift(1)
    daily_data[target_col] = (daily_data['open'] - daily_data['close'].shift(1))/daily_data['open']
    #daily_data[colname] = (daily_data['open'].shift(-1) - daily_data['close'])/daily_data['close']
    
    return daily_data[[target_col, open_col, prev_close_col]]

# Calculate Percent Change from Market Open to Time t
def calc_percent_change_from_open(df, colname):


    target_col = colname + '_CHANGE_FROM_OPEN'
    close_col = colname + '_CURRENT_CLOSE'
    open_col = colname + '_CURRENT_DAY_OPEN'

    # Group by day and calculate the percent change from open to each minute within the trading day
    df[open_col] = df['open'].groupby(df.index.date).transform('first')
    df[close_col] = df['close']
    
    # Calculate percent change from open for each minute
    df[target_col] = (df[close_col] - df[open_col]) / df[open_col] 
    
    return df[[target_col, open_col, close_col]]


def gen_data(input_file, time_weight):

    blackout_dts = '2022-05-17,2022-05-24,2022-06-17,2022-06-29,2022-08-26,2022-09-08,2022-09-23,2022-09-27,2022-09-28,2022-11-30,2023-01-10,2023-02-07,2023-05-19,2023-06-28,2023-06-29,2023-08-25,2023-09-28,2023-10-02,2023-10-19,2023-10-25,2023-11-08,2023-11-09,2023-12-01,2024-02-05,2024-03-22,2024-03-29,2024-04-03,2024-04-16,2024-05-14,2024-05-19,2022-06-10,2022-07-13,2022-08-10,2022-09-13,2022-10-13,2022-11-10,2022-12-13,2023-01-12,2023-02-14,2023-03-14,2023-04-12,2023-05-10,2023-06-13,2023-07-12,2023-08-10,2023-09-13,2023-10-12,2023-11-14,2023-12-12,2024-01-11,2024-02-13,2024-03-12,2024-04-10,2024-05-15,2024-06-12,2024-07-11,2024-08-14,2024-09-11,2024-10-10,2024-11-13,2024-12-11,2022-05-25,2022-07-06,2022-08-17,2022-10-12,2022-11-23,2023-01-04,2023-02-22,2023-04-12,2023-05-24,2023-07-05,2023-08-16,2023-10-11,2023-11-21,2024-01-03,2024-02-21,2024-04-10,2024-05-22,2024-07-03,2024-08-21,2024-10-09,2024-11-27,2022-06-15,2022-07-27,2022-09-21,2022-11-02,2022-12-14,2023-02-01,2023-03-22,2023-05-03,2023-06-14,2023-07-26,2023-09-20,2023-11-01,2023-12-13,2024-01-31,2024-03-20,2024-05-01,2024-06-12,2024-07-31,2024-09-18,2024-11-06,2024-12-18'
    blackout_dts = blackout_dts.split(',')

    # Read in the target data from Option Omega download
    #input_file = "C:\\Users\\miche\\Downloads\\trade-log-1030-4.csv.csv"


    def combine_date_time(date, time):
        return pd.to_datetime(date + ' ' + time)

    target_dat = pd.read_csv(
        input_file,
        parse_dates={'OpenDatetime': ['Date Opened', 'Time Opened'],
                    'CloseDatetime': ['Date Closed', 'Time Closed'],},  # Combine 'date' and 'time' into 'datetime'
        date_parser=combine_date_time  # Custom parser to handle the combination
    ).set_index('OpenDatetime')

    target_dat.index = target_dat.index - pd.DateOffset(hours=1)


    # calculate the time weighting

    target_dat['time_wt'] = calculate_time_weights(target_dat, 
                                                   weight_range=time_weight['range'], 
                                                   method=time_weight['method'])


    # Read in the VIX and SPX per minute data
    VIX_DATA = pd.read_pickle('C:/Users/miche/OptionsAnalysis/data/vix_minute_data.pkl')
    SPX_DATA = pd.read_pickle('C:/Users/miche/OptionsAnalysis/data/spx_minute_data.pkl')

    # Ensure the 'date' column is in datetime format
    VIX_DATA['date'] = pd.to_datetime(VIX_DATA['date'])
    SPX_DATA['date'] = pd.to_datetime(SPX_DATA['date'])

    # Set the date column as index
    VIX_DATA.set_index('date', inplace=True)
    SPX_DATA.set_index('date', inplace=True)

    VIX_DATA.index = VIX_DATA.index.tz_localize(None)
    SPX_DATA.index = SPX_DATA.index.tz_localize(None)

    # Define market open and close times
    vix_market_open_time = '08:31:00'
    spx_market_open_time = '08:30:00'
    market_close_time = '15:15:00'

    # Filter data to include only market open to close times
    VIX_DATA = VIX_DATA.between_time(vix_market_open_time, market_close_time)
    SPX_DATA = SPX_DATA.between_time(spx_market_open_time, market_close_time)





    VIX_OVERNIGHT_CHANGE = calc_open_close_change(VIX_DATA, 'VIX')
    VIX_OVERNIGHT_CHANGE.set_index( VIX_OVERNIGHT_CHANGE.index.date, inplace=True)

    SPX_OVERNIGHT_CHANGE = calc_open_close_change(SPX_DATA, 'SPX')
    SPX_OVERNIGHT_CHANGE.set_index( SPX_OVERNIGHT_CHANGE.index.date, inplace=True)

    # Apply the function to calculate percent change since open for VIX and SPX
    VIX_CHANGE = calc_percent_change_from_open(VIX_DATA,'VIX')
    VIX_CHANGE.index = VIX_CHANGE.index.tz_localize(None)

    SPX_CHANGE = calc_percent_change_from_open(SPX_DATA, 'SPX')
    SPX_CHANGE.index = SPX_CHANGE.index.tz_localize(None)

    # Now combine the variables with the target_dat dataset

    target_dat['open_date'] = target_dat.index.date

    target_dat = pd.merge(
        target_dat,
        VIX_OVERNIGHT_CHANGE,
        left_on='open_date',  # Merge on the 'date' column from minute_data
        right_index=True,  # Merge on the index (date) of VIX_OVERNIGHT_CHANGE
        how='left'  # Use 'left' join to keep all rows from minute_data
    )

    target_dat = pd.merge(
        target_dat,
        SPX_OVERNIGHT_CHANGE,
        left_on='open_date',  # Merge on the 'date' column from minute_data
        right_index=True,  # Merge on the index (date) of VIX_OVERNIGHT_CHANGE
        how='left'  # Use 'left' join to keep all rows from minute_data
    )

    target_dat = pd.merge(
        target_dat,
        VIX_CHANGE,
        left_index = True,
        right_index=True, 
        how='inner'  
    )

    target_dat = pd.merge(
        target_dat,
        SPX_CHANGE,
        left_index = True,
        right_index=True, 
        how='inner'  
    )


    # remove the blackout dates from the dataset
    date_list = pd.to_datetime(blackout_dts)
    target_dat.index = pd.to_datetime(target_dat.index.date)
    target_dat = target_dat.loc[~target_dat.index.isin(date_list)]

    return target_dat


