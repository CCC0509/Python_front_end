from flask import Flask, render_template

# create server
app = Flask(__name__)


@app.route("/")
def home():
    # render the html file from templates folder
    return render_template("index.html")


# implement this app if it is not import from other file
if __name__ == "__main__":
    app.run(debug=True)
