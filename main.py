import pandas as pd
import numpy as np
import math
from flask import Flask, request, jsonify

def process_data(df):
    daily_simple_returns = df.pct_change(1)
    annual_returns = daily_simple_returns.mean()*252
    annual_risks = daily_simple_returns.std()*math.sqrt(252)
    sorted_annual_returns = annual_returns.sort_values(ascending = False)

    df2 = pd.DataFrame()
    df2['Expected Annual Returns'] = annual_returns
    df2['Expected Annual Risks'] = annual_risks
    df2['Company Symbol'] = df2.index
    df2['Ratio'] = df2['Expected Annual Returns']/df2['Expected Annual Risks']
    df2.sort_values(by="Ratio", axis = 0, ascending = False)

    remove_list = []
    for ticker in df2['Company Symbol'].values:
        no_better_asset = df2.loc[(df2['Expected Annual Returns']>df2['Expected Annual Returns'][ticker])&(df2['Expected Annual Risks']<df2['Expected Annual Risks'][ticker])].empty
        if no_better_asset == False:
            remove_list.append(ticker)

    findf = df2.drop(remove_list)
    return findf

def process_result(findf):
    output_ticker = list(findf['Company Symbol'])
    output_returns = list(findf['Expected Annual Returns']*100)

    assets = findf.index
    num_assets = len(assets)

    n = 1.0/float(num_assets)
    weights = [n]*num_assets
    weights = np.array(weights)

    output_port_ar = round(np.sum(weights*output_returns)*100, 2)
    return {"data":dict(zip(output_ticker, output_returns)), "portfolio_return":output_port_ar}

app = Flask(__name__)

@app.route('/stocks', methods=['GET'])
def recommend():

    url = "https://drive.google.com/file/d/1Moy7gFri9FPmDspWyK2rJWU4n7AJP18R/view"
    url='https://drive.google.com/uc?id=' + url.split('/')[-2]
    df = pd.read_csv(url)
    df.drop( "Unnamed: 0", axis=1, inplace = True)
    df.set_index(pd.DatetimeIndex(df.Date.values), inplace = True)
    df.drop("Date", axis = 1, inplace=True)

    yr = int(request.args.get('year'))
    if yr == 1:
        df = df['2023-05-22':'2024-05-22']
    elif yr == 3:
        df = df['2021-05-22':'2024-05-22']
    else:
        df = df
    
    findf = process_data(df)
    return jsonify(process_result(findf=findf))

if '__main__' == __name__:
    app.run(host = "0.0.0.0", port = 5000)
