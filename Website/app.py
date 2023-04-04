from flask import Flask, render_template, request
import yfinance as yf
import pandas as pd
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
from datetime import datetime
import time
import io
import base64
from flask import Flask

app = Flask(__name__)
app.debug = True
app = Flask(__name__)

def generate_graph(ticker_symbol):
    df = pd.DataFrame(columns=["datetime", "close_price"])

    start_time = datetime.now()

    fig, ax = plt.subplots()
    line, = ax.plot([], [])
    ax.set_xlabel("Time")
    ax.set_ylabel("Close Price ($)")
    ax.set_title("Stock Info for " + yf.Ticker(ticker_symbol).info["longName"])
    fig.show()

    while True:
        stock_info = yf.Ticker(ticker_symbol).history(period="1d", interval="1m")

        current_time = datetime.now().strftime("%I:%M:%S %p")
        close_price = stock_info.tail(1)["Close"].iloc[0]

        df = pd.concat([df, pd.DataFrame({"datetime": [current_time], "close_price": [close_price]})], ignore_index=True)

        df["datetime"] = pd.to_datetime(df["datetime"])
        line.set_xdata(df["datetime"])
        line.set_ydata(df["close_price"])
        ax.relim()
        ax.autoscale_view()
        ax.xaxis.set_major_formatter(matplotlib.dates.DateFormatter('%I:%M:%S %p'))
        fig.canvas.draw()
        fig.canvas.flush_events()

        time.sleep(1)

        if (datetime.now() - start_time).seconds >= 3600:
            break

    # Save the figure to a buffer and encode it as a base64 string
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    graph = base64.b64encode(buffer.getvalue()).decode()
    plt.close()

    return graph


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        ticker_symbol = request.form['ticker_symbol']
        graph = generate_graph(ticker_symbol)
        stock_info = yf.Ticker(ticker_symbol).info
        return render_template('index.html', graph=graph, stock_info=stock_info)
    return render_template('index.html')


if __name__ == '__main__':
    app.run(debug=True)
