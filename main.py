from flask import Flask, redirect, make_response
from routes.load import loading_blueprint
from routes.dataset import dataset_blueprint
from routes.analysis import analysis_blueprint

import settings

settings.init()

app = Flask(__name__)

app.register_blueprint(loading_blueprint, url_prefix="/load")
app.register_blueprint(dataset_blueprint, url_prefix="/dataset")
app.register_blueprint(analysis_blueprint, url_prefix="/analysis")


@app.route("/", methods=["GET"])
def index():
    return redirect("/load")


@app.route("/drop", methods=["GET"])
def drop():
    settings.dataset = None
    return redirect("/load")


@app.route("/save", methods=["GET"])
def save():
    response = make_response(settings.dataset.to_csv())
    response.headers["Content-Disposition"] = "attachment; filename=export.csv"
    response.headers["Content-Type"] = "text/csv"
    return response


if __name__ == "__main__":
    app.run(debug=True)