
from flask import Flask, render_template, request
# from cachetools import cached, TTLCache

# app = Flask(__name__)
app = Flask('financial_graph')
# cache = TTLCache(maxsize=100, ttl=60)

@app.route("/plot", methods=['POST'])
def plot():
    import datetime
    import yfinance as yf
    from bokeh.plotting import figure
    from bokeh.embed import components
    from bokeh.resources import CDN
    from dateutil.parser import parse

    if request.method == 'POST':
        tickr = request.form["Tickr_symbol"]
        start_date = request.form["start_date"]
        end_date = request.form["end_date"]

    tickrNew = (str(tickr.upper()) + '.NS')
    start_date_formatted = parse(start_date).date()
    end_date_formatted = parse(end_date).date()

    df = yf.download(tickrNew, start_date_formatted, end_date_formatted)
    def inc_dec(c, o):
        if c > o:
            value = "Increase"
        elif c < o:
            value = "Decrease"
        else:
            value = "Equal"
        return value

    df["Status"] = [inc_dec(c, o) for c, o in zip(df.Close, df.Open)]
    df["Middle"] = (df.Open + df.Close) / 2
    df["Height"] = abs(df.Close - df.Open)

    p = figure(x_axis_type='datetime', width=1000, height=300)
    p.title.text = "Candlestick Chart"
    p.grid.grid_line_alpha = 0.3
    hours_12 = 12*60*60*1000

    p.segment(df.index, df.High, df.index, df.Low, color="Black")

    p.rect(df.index[df.Status == "Increase"], df.Middle[df.Status == "Increase"],
           hours_12, df.Height[df.Status == "Increase"], fill_color="#CCFFFF", line_color="black")

    p.rect(df.index[df.Status == "Decrease"], df.Middle[df.Status == "Decrease"],
           hours_12, df.Height[df.Status == "Decrease"], fill_color="#FF3333", line_color="black")

    script1, div1 = components(p)
    cdn_js = CDN.js_files[0]

    return render_template("plot.html",
                           script1=script1,div1=div1,
                           cdn_js=cdn_js,tickrNew1=tickrNew,
                           start_date_formatted=start_date_formatted, end_date_formatted=end_date_formatted)

@app.route('/login')
def login():
    return render_template("login.html")


@app.route('/')
def home():
    return render_template("home.html")


@app.route('/about')
def about():
    return render_template("about.html")


# @cached(cache)
@app.route('/stock_list', methods=['GET', 'POST'])
def stock_list():
    import pandas
    import re

    df = pandas.read_csv('static/stock_list.csv')

    if request.method == 'POST':
        search_arg = request.form["search"]
        search_string = str(search_arg)
        if len(search_string) != 0:
            # companies=[]
            # tickrs=[]
            # listings=[]
            # for ind in df.index:
            #     if (search_string in (df['Company'][ind]).casefold()) or (search_string in (df['Symbol'][ind]).casefold()):
            #         # companies.append(df['Company'][ind])
            #         # tickrs.append(df['Symbol'][ind])
            #         # listings.append(df['First Listing Date'][ind])

            # filtered_df = df[df['Company'] == search_string] or df[df['Symbol'] == search_string]

            # filtered_df = df[((df.Company == search_string) == True) | ((df.Symbol == search_string) == True)]

            filtered_df = df[df['Company'] == search_string]

            print(filtered_df)
            return render_template("stock_list.html", len=len(filtered_df.count(axis=0, level=None, numeric_only=False)), df=filtered_df)
        else:
            return render_template("stock_list.html", len=1601, df=df)

    if request.method == 'GET':
        return render_template("stock_list.html", len=1601, df=df)
if __name__ == "__main__":
    app.run(debug=True)
