from scipy.optimize import differential_evolution, NonlinearConstraint
import numpy as np

# Define the objective function
def objective(x, df, min_trades, min_trades_boost, win_rate_boost):

    # Filter data based on the decision variables
    filtered_data = df[
        (df['VIX_ON_CHANGE'] >= x[0]) & (df['VIX_ON_CHANGE'] <= x[1]) &
        (df['SPX_ON_CHANGE'] >= x[2]) & (df['SPX_ON_CHANGE'] <= x[3]) &
        (df['VIX_CURRENT_CLOSE'] >= x[4]) & (df['VIX_CURRENT_CLOSE'] <= x[5]) &
        (df['SPX_CHANGE_FROM_OPEN'] >= x[6]) & (df['SPX_CHANGE_FROM_OPEN'] <= x[7]) 
        #(df['VIX_CHANGE_FROM_OPEN'] >= x[8]) & (df['VIX_CHANGE_FROM_OPEN'] <= x[9]) 
    ]
    
    # Objectives
    num_trades = len(filtered_data)  # Maximize number of trades
    total_profit = ( filtered_data['P/L'] * filtered_data['time_wt']).sum()  # Maximize total profit
    win_rate = 10000*( ( filtered_data['P/L'] > 0.0) * filtered_data['time_wt']).mean() if num_trades > 0 else 0  # Maximize win rate

    # Combined objective function (to minimize)
    # Include a penalty for too small ranges
    # penalty = 1000 * (1 / (VIX_overnight_max - VIX_overnight_min + 1e-6) +  1/(SPX_overnight_max - SPX_overnight_min + 1e-6))


    # Penalty for not meeting the minimum number of trades
    if num_trades < min_trades:
        min_trades_penalty = min_trades_boost * (min_trades - num_trades)  # Large penalty
    else:
        min_trades_penalty = 0  # No penalty if the constraint is met
    
    # Define weights for each objective
    # w2, w3 =  0.1, 0.8  # Adjust weights according to preference
    
    # Combined objective function (to minimize)
    return -( total_profit + win_rate_boost * win_rate) + min_trades_penalty


def perform_optimization(target_dat, min_trades,  min_trades_boost, win_rate_boost):

    bounds = [
        (target_dat.VIX_ON_CHANGE.min(), target_dat.VIX_ON_CHANGE.max() - 0.01 ), 
        (target_dat.VIX_ON_CHANGE.min() + 0.01, target_dat.VIX_ON_CHANGE.max()), 
        (target_dat.SPX_ON_CHANGE.min(), target_dat.SPX_ON_CHANGE.max() -0.01),  
        (target_dat.SPX_ON_CHANGE.min() + 0.01 , target_dat.SPX_ON_CHANGE.max()),  


        (target_dat.VIX_CURRENT_CLOSE.min(), target_dat.VIX_CURRENT_CLOSE.max()-1), 
        (target_dat.VIX_CURRENT_CLOSE.min()+1, target_dat.VIX_CURRENT_CLOSE.max()),  

        (target_dat.SPX_CHANGE_FROM_OPEN.min(), target_dat.SPX_CHANGE_FROM_OPEN.max() -0.01),  
        (target_dat.SPX_CHANGE_FROM_OPEN.min() + 0.01 , target_dat.SPX_CHANGE_FROM_OPEN.max()) 

        #(target_dat.VIX_CHANGE_FROM_OPEN.min(), target_dat.VIX_CHANGE_FROM_OPEN.max() -0.01), 
        #(target_dat.VIX_CHANGE_FROM_OPEN.min() + 0.01 , target_dat.VIX_CHANGE_FROM_OPEN.max()),  
    ]

    # Define constraints to ensure min is less than max for each range using NonlinearConstraint
    constraints = [
        NonlinearConstraint(lambda x: x[1] - x[0], 0, np.inf),  # VIX_overnight_max > VIX_overnight_min
        NonlinearConstraint(lambda x: x[3] - x[2], 0, np.inf),  # SPX_overnight_max > SPX_overnight_min
        NonlinearConstraint(lambda x: x[5] - x[4], 0, np.inf),   # VIX_prior_max > VIX_prior_min
        NonlinearConstraint(lambda x: x[7] - x[6], 0, np.inf),   # SPX_change_max > SPX_change_min
        #NonlinearConstraint(lambda x: x[9] - x[8], 0, np.inf),   # VIX_change_max > VIX_change_min
    ]

    # Define initial guess (midpoints of bounds)
    x0 = [-0.05, 0.05, -0.01, 0.01, 15, 20, -0.01, 0.01] #, -0.01, 0.01]

    # Perform the optimization using differential evolution
    result = differential_evolution(
        objective,
        bounds,
        args=(target_dat ,min_trades, min_trades_boost, win_rate_boost),
        strategy='best1bin',  # Strategy for differential evolution
        maxiter=1000,  # Maximum iterations
        popsize=17,  # Population size
        tol=1e-6,  # Tolerance for convergence
        mutation=(0.5, 1.44),  # Mutation factor
        recombination=0.9,  # Recombination constant
        seed=42,  # Seed for reproducibility
        disp=False,  # Display convergence messages
        constraints=constraints,
        polish = True
    )

    # Check if optimization was successful
    if result.success:
        # Get the optimal decision variables
        
        res_string =  f"VIX OVERNIGHT % CHANGE MIN: {np.round( result.x[0] * 100 ,2)}%\n"
        res_string = res_string + f"VIX OVERNIGHT % CHANGE MAX: {np.round( result.x[1] * 100 ,2)}%\n"
        res_string = res_string + f"SPX GAP MIN: {np.round( result.x[2] * 100 ,2)}%\n"
        res_string = res_string + f"SPX GAP MAX: {np.round( result.x[3] * 100 ,2)}%\n"
        res_string = res_string + f"VIX MIN: {np.round( result.x[4],2)}\n"
        res_string = res_string + f"VIX MAX: {np.round( result.x[5],2)}\n"

        res_string = res_string + f"SPX CHANGE MIN: {np.round( result.x[6]*100,2)}%\n"
        res_string = res_string + f"SPX CHANGE MAX: {np.round( result.x[7]*100,2)}%\n"
        # res_string = res_string + f"VIX CHANGE MIN: {np.round( result.x[8]*100,2)}%\n"
        # res_string = res_string + f"VIX CHANGE MAX: {np.round( result.x[9]*100,2)}%\n"

        print("\n\n***********************************************")
        print(    "************   OPTIMIAL VALUES  ***************")
        print("***********************************************\n")

        print(res_string)

    else:
        print("Optimization failed:", result.message)

    return result
