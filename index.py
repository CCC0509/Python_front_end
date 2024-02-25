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

# get info from API
s = requests.get(
    "https://openapi.twse.com.tw/v1/exchangeReport/STOCK_DAY_AVG_ALL")
s_info = s.json()


@app.route("/")
def home():
    # print(type(s_info[0]["Code"]))
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
    cash_total = math.floor(twd+usd*exchange_rate)
    # save data as a object
    data_cash = {"twd": twd, "usd": usd, "rate": exchange_rate,
                 "total": cash_total, "result": result_cash}
    # data from stock table
    result_stock = cursor.execute("select * from stock").fetchall()
    # list all stock_id which is no duplicate
    stock_list = []
    for data in result_stock:
        if data[1] not in stock_list:
            stock_list.append(data[1])
    # get each stock info
    stock_info = []
    # all stock price
    stock_price = 0
    for stock in stock_list:
        result = cursor.execute(
            "select * from stock where stock_id=?", (stock,)).fetchall()
        # get price which match stock_id
        for i in s_info:
            if i["Code"] == stock:
                current_price = float(i["ClosingPrice"])
        num = 0
        stock_buy_total = 0
        for data in result:
            num += data[2]
            stock_buy_total += data[2]*data[3]+data[4]+data[5]
        stock_total = math.floor(current_price*num)
        average_cost = round(stock_buy_total/num, 2)
        roi = math.floor(((stock_total-stock_buy_total)/stock_buy_total)*100)
        stock_price += stock_total
        # store stock info we need in to stock_info
        stock_info.append({"stock_id": stock, "num": num, "price": current_price, "total_price": stock_total,
                          "cost": stock_buy_total, "average_cost": average_cost, "roi": roi})
    # calculate the percentage of each stock from all stock
    for stock in stock_info:
        stock["value_percentage"] = round(
            (stock["total_price"]/stock_price)*100, 2)
    # render the html file from templates folder
    # send data to html
    return render_template("index.html", data_cash=data_cash, stock_info=stock_info)


@app.route("/cash")
def cash_form():
    return render_template("cash.html")


@app.route("/cash", methods=["POST"])
def submit_cash():
    # get values from html form
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


# delete data from datatype which choosen from html
@app.route("/delete_cash", methods=["post"])
def delete_table():
    del_id = request.values["id"]
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("delete from cash where transaction_id =?", (del_id))
    conn.commit()
    return redirect("/")


@app.route("/stock")
def stock_form():
    return render_template("stock.html")


@app.route("/stock", methods=["post"])
def submit_stock():
    fee = 0
    tax = 0
    stock_id = request.values["stock-id"]
    num = request.values["stock-num"]
    price = request.values["stock-price"]
    if request.values["processing-fee"] != "":
        fee = request.values["processing-fee"]
    if request.values["tax"] != "":
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
