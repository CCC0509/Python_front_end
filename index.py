from flask import Flask, render_template

# create server
app = Flask(__name__)


@app.route("/")
def home():
    # render the html file from templates folder
    return render_template("index.html")


@app.route("/cash")
def cash_form():
    return render_template("cash.html")


@app.route("/stock")
def stock_form():
    return render_template("stock.html")


# implement this app if it is not import from other file
if __name__ == "__main__":
    app.run(debug=True)
