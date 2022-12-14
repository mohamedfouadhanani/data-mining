from flask import Blueprint, redirect, render_template, request
from dm.analysis import attribute_type, find_outliers
from dm.pretreatment import equal_intervals_discretization, fill_mean, fill_median, fill_minimum, fill_mode, fill_unknown, min_max_normalization, quantile_discretization, remove_outliers_equal_intervals_discretization, remove_outliers_quantile_discretization, z_score_normalization
import settings

pretreatment_blueprint = Blueprint("pretreatment", __name__)


@pretreatment_blueprint.route("/<string:attribute>/delete", methods=["GET"])
def delete_attribute(attribute):
    if settings.dataset is None:
        return redirect("/load/")

    if attribute not in settings.dataset.columns:
        return redirect("/dataset/")

    settings.dataset.drop(attribute, axis=1, inplace=True)

    return redirect("/dataset/")


@pretreatment_blueprint.route("/<string:attribute>/outliers/delete", methods=["GET"])
def delete_outliers(attribute):
    if settings.dataset is None:
        return redirect("/load/")

    if attribute not in settings.dataset.columns:
        return redirect("/dataset/")

    if "continue" in attribute_type(settings.dataset, attribute):
        outliers_indicies = find_outliers(settings.dataset[attribute])
        settings.dataset.drop(settings.dataset.index[outliers_indicies], inplace=True)

    return redirect(request.referrer)


@pretreatment_blueprint.route("/<string:attribute>/normalization", methods=["POST"])
def normalize(attribute):
    normalization_method = request.form["normalization"]

    if normalization_method == "minmax":
        # acquire minimum & maximum
        minimum = float(request.form["minimum"])
        maximum = float(request.form["maximum"])

        # minmax normalization
        settings.dataset[attribute] = min_max_normalization(
            settings.dataset[attribute], minimum=minimum, maximum=maximum)

        return redirect(request.referrer)

    # apply zscore normalization
    settings.dataset[attribute] = z_score_normalization(settings.dataset[attribute])

    return redirect(request.referrer)


@pretreatment_blueprint.route("/duplicates/delete", methods=["GET"])
def delete_duplicates():
    settings.dataset.drop_duplicates(inplace=True)
    return redirect(request.referrer)


@pretreatment_blueprint.route("/<string:attribute>/missing", methods=["POST"])
def replace_missing_values(attribute):
    if settings.dataset is None:
        return redirect("/load/")

    if attribute not in settings.dataset.columns:
        return redirect("/dataset/")

    method = request.form["missing_values_replacement"]

    method_functions = {
        "mean": fill_mean,
        "median": fill_median,
        "mode": fill_mode,
        "minimum": fill_minimum,
        "unknown": fill_unknown
    }

    try:
        method_functions[method](settings.dataset, attribute)
    except:
        pass

    return redirect(request.referrer)


@pretreatment_blueprint.route("/<string:attribute>/discretize", methods=["POST"])
def discretize(attribute):
    if settings.dataset is None:
        return redirect("/load/")

    if attribute not in settings.dataset.columns:
        return redirect("/dataset/")

    method = request.form["discretization"]
    k = int(request.form["k"])

    discretization_functions = {
        "equal-frequency": quantile_discretization,
        "equal-width": equal_intervals_discretization
    }

    try:
        discretization_functions[method](dataset=settings.dataset, attribute=attribute, k=k)
    except:
        pass

    return redirect(request.referrer)


@pretreatment_blueprint.route("/<string:attribute>/outliers/replace", methods=["POST"])
def discretize_outliers(attribute):

    method = request.form["discretization"]
    k = int(request.form["k"])

    print(f"removing outliers by discretisizing them using the method {method} and k equal to {k}")

    discretization_functions = {
        "equal-frequency": remove_outliers_quantile_discretization,
        "equal-width": remove_outliers_equal_intervals_discretization
    }

    try:
        discretization_functions[method](dataset=settings.dataset, attribute=attribute, k=k)
    except:
        pass

    return redirect(request.referrer)
