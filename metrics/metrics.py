from flask import Response


def render_value(value):
    if value is True:
        return 1
    elif value is False:
        return 0
    else:
        return value


def render_metrics(metrics):
    output = ""
    for k, v in metrics.items():
        if v is not None:
            output += "{k} {v}\n".format(k=k, v=render_value(v))
    return Response(output, mimetype='text/plain')


def label_metrics(metrics, labels):
    label_items = ",".join('{k}="{v}"'.format(k=k, v=v) for k, v in labels.items())
    label = "{" + label_items + "}"

    labelled = {}
    for k, v in metrics.items():
        labelled[k + label] = v
    return labelled