from flask import Flask, render_template, request
import pandas as pd
import pandas_highcharts.core
import sqlite3

app = Flask(__name__)

@app.route('/graph')
def graph_Example(chartID = 'chart_ID', chart_type = 'line', chart_height = 500):
#    df = pd.read_csv('csv/BCHAIN-TRVOU-BitcoinUSDExchangeTradeVolume.csv', index_col='Date', parse_dates=True)
#    df = pd.read_csv('csv/test.csv', index_col='Date', parse_dates=False)
    
    df = pd.read_csv('messages_4d3f6a.csv', index_col='timestamp', parse_dates=True)
    dataSet = pandas_highcharts.core.serialize(df, render_to='my-chart', output_type='json', title='SaveYourFridge', chart={'zoomType': 'x'})
    return render_template('graph.html', chart=dataSet)


#    cnx = sqlite3.connect("syf.db")
#    df = pd.read_sql_query("SELECT timestamp as Date, temperature as Value from messages_4d3f6a",cnx)
##    dataSet = pandas_highcharts.core.serialize(df, render_to='my-chart', output_type='json', title='SaveYourFridge', xAxis={'title': 'Test X-Achse'})
#    dataSet = pandas_highcharts.core.serialize(df, render_to='my-chart', output_type='json', title='SaveYourFridge')
#    return render_template('graph.html', chart=dataSet)


@app.route('/')
def main():
	return "Server up and running..."

app.run(debug=True)

