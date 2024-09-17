from ib_insync import *
import pandas as pd
import time
from datetime import datetime, timedelta

# Connect to IB Gateway/TWS
ib = IB()
ib.connect('127.0.0.1', 7496, clientId=12)  # Ensure TWS/IB Gateway is running and port matches

# Define SPX and VIX contracts
spx_contract = Index(symbol='SPX', exchange='CBOE', currency='USD')
vix_contract = Index(symbol='VIX', exchange='CBOE', currency='USD')

# Qualify the contracts to ensure they are recognized by IBKR
qualified_contracts = ib.qualifyContracts(spx_contract, vix_contract)

# Initialize empty DataFrames to store the data
all_vix_data = pd.DataFrame()
all_spx_data = pd.DataFrame()

# Define the date range from May 2022 to the present
start_date = datetime(2022, 5, 1)
end_date = datetime.now()

# Loop through each week from start_date to end_date
current_date = start_date

while current_date < end_date:
    # Calculate the next week's end date
    next_date = current_date + timedelta(weeks=1)

    # Convert to the required IB date format
    endDateTime = current_date.strftime('%Y%m%d %H:%M:%S')

    try:
        # Request VIX data for the current week
        vix_data = ib.reqHistoricalData(
            vix_contract,
            endDateTime=endDateTime,
            durationStr='1 W',  # One week
            barSizeSetting='1 min',  # Minute granularity
            whatToShow='TRADES',
            useRTH=False  # Use all trading hours
        )
        time.sleep(2)  # Sleep to prevent rate limits

        # Request SPX data for the current week
        spx_data = ib.reqHistoricalData(
            spx_contract,
            endDateTime=endDateTime,
            durationStr='1 W',  # One week
            barSizeSetting='1 min',  # Minute granularity
            whatToShow='TRADES',
            useRTH=False  # Use all trading hours
        )

        # Convert to DataFrame and concatenate to the main DataFrame
        if vix_data:
            vix_df = util.df(vix_data)
            all_vix_data = pd.concat([all_vix_data, vix_df], ignore_index=True)

        if spx_data:
            spx_df = util.df(spx_data)
            all_spx_data = pd.concat([all_spx_data, spx_df], ignore_index=True)

        print(f"Data fetched for week starting {current_date.strftime('%Y-%m-%d')}")

    except Exception as e:
        print(f"Error fetching data for week starting {current_date.strftime('%Y-%m-%d')}: {e}")

    # Move to the next week
    current_date = next_date

# Save the combined DataFrame to a pickle file
all_vix_data.to_pickle('vix_minute_data.pkl')
all_spx_data.to_pickle('spx_minute_data.pkl')

print("Data fetching complete and saved to 'vix_minute_data.pkl' and 'spx_minute_data.pkl'.")

# Disconnect from IB
ib.disconnect()
