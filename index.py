from flask import Flask, render_template, request, g, redirect
import sqlite3
import requests
import math

# create server
app = Flask(__name__)

DATABASE = "./datafile.db"


def get_db():
    # check if g got a attribute "sql_db"
    if not hasattr(g, "sql_db"):
        # if not set g.sql_db attribute from sqlite3
        g.sql_db = sqlite3.connect(DATABASE)
    return g.sql_db

# excute after ever http request


@app.teardown_appcontext
def close_connection(exception):
    print("正在結束sql connection...")
    if hasattr(g, "sql_db"):
        # if got database attribute then disconnected
        g.sql_db.close()


# get exchange rate from API
r = requests.get("https://tw.rter.info/capi.php")
exchange_rate = r.json()["USDTWD"]["Exrate"]


@app.route("/")
def home():
    # data from cash table
    conn = get_db()
    cursor = conn.cursor()
    result_cash = cursor.execute("select * from cash").fetchall()
    # calculate and convert total to twd
    twd = 0
    usd = 0
    for data in result_cash:
        twd += data[1]
        usd += data[2]
    total = math.floor(twd+usd*exchange_rate)
    # save data as a object
    data_cash = {"twd": twd, "usd": usd, "rate": exchange_rate,
                 "total": total, "result": result_cash}
    # render the html file from templates folder
    # send data to html
    return render_template("index.html", data_cash=data_cash)


@app.route("/cash")
def cash_form():
    return render_template("cash.html")


@app.route("/cash", methods=["POST"])
def submit_cash():
    # get values from heml form
    twd = 0
    usd = 0
    if request.values["taiwanese-dollars"] != "":
        twd = request.values["taiwanese-dollars"]
    if request.values["us-dollars"] != "":
        usd = request.values["us-dollars"]
    note = request.values["note"]
    date = request.values["date"]

    # update data to database
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "insert into cash(taiwanese_dollars,us_dollars,note,date_info) values(?,?,?,?)", (twd, usd, note, date))
    conn.commit()
    # take the user back to homepage
    return redirect("/")


@app.route("/stock")
def stock_form():
    return render_template("stock.html")


@app.route("/stock", methods=["post"])
def submit_stock():
    num = 0
    price = 0
    fee = 0
    tax = 0
    stock_id = request.values["stock-id"]
    num = request.values["stock-num"]
    price = request.values["stock-price"]
    fee = request.values["processing-fee"]
    tax = request.values["tax"]
    date = request.values["date"]

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("insert into stock(stock_id,stock_num,stock_price,processing_fee,tax,date_info) values(?,?,?,?,?,?)",
                   (stock_id, num, price, fee, tax, date))
    conn.commit()
    return redirect("/")


# implement this app if it is not import from other file
if __name__ == "__main__":
    app.run(port=8080, debug=True)
