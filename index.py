from flask import Flask

# create server
app = Flask(__name__)


@app.route("/")
def home():
    return "This is home page"


# implement this app if it is not import from other file
if __name__ == "__main__":
    app.run(debug=True)
