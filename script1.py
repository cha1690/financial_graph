
from flask import Flask, render_template, request

# app = Flask(__name__)
app = Flask('financial_graph')

@app.route("/plot", methods=['POST'])
def plot():
    import datetime
    import yfinance as yf
    from bokeh.plotting import figure
    from bokeh.embed import components
    from bokeh.resources import CDN

    if request.method == 'POST':
        tickr = request.form["Tickr_symbol"]

    tickrNew = str(tickr.upper()) + '.NS'

    start_date = datetime.datetime(2020, 1, 1)
    end_date = datetime.datetime(2020, 2, 26)

    df = yf.download('tickrNew', start_date, end_date)

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
           hours_12, df.Height[df.Status == "Increase"], fill_color = "#CCFFFF", line_color="black")

    p.rect(df.index[df.Status == "Decrease"], df.Middle[df.Status == "Decrease"],
           hours_12, df.Height[df.Status == "Decrease"], fill_color="#FF3333", line_color="black")

    script1, div1 = components(p)
    cdn_js = CDN.js_files[0]
    # cdn_css = CDN.css_files[0]
    return render_template("plot.html",
                           script1=script1,
                           div1=div1,
                           cdn_js=cdn_js)

@app.route('/')
def home():
    return render_template("home.html")


@app.route('/about')
def about():
    return render_template("about.html")


@app.route('/stock_list')
def stock_list():
    import pandas
    try:
        df = pandas.read_csv('static/stock_list.csv')
        return render_template("stock_list.html", text=df.to_html())
    except Exception as e:
        return render_template("stock_list.html", text=str(e))

@app.route('/login')
def login():
    return render_template("login.html")


if __name__ == "__main__":
    app.run(debug=True)
