import db
import statistics

import plotly
import plotly.graph_objs as go


"""
Get the standard deviation for the specific field of the analysed projects
"""
def get_standard_deviation(field):
    db.connect_db();

    values = db.get_values(field);

    stddev = statistics.pstdev(values);
    return stddev

"""
Create one set of histograms
"""
def create_all_histograms():
    make_histogram('dep_depth', 'Beroendedjup', 0, 25, 1, 1)
    make_histogram('dep_depth_dev', 'Beroendedjup', 0, 25, 1, 1)
    make_histogram('direct_dep', 'Direkta Beroenden', 0, 50, 2, 2)
    make_histogram('direct_dep_dev', 'Direkta Beroenden', 0, 50, 2, 2)
    make_histogram('indirect_dep', 'Indirekta Beroenden', 0, 2000, 50, 100)
    make_histogram('indirect_dep_dev', 'Indirekta Beroenden', 0, 2000, 50, 100)

"""
Create a histogram for the given field using plotly
"""
def make_histogram(field, xlabel, min_value, max_value, step_size, step_size_tick):
    db.connect_db();
    values = db.get_values(field);

    data = [go.Histogram(
        x=values,
        marker=dict(
            color='#a8a8a8',
            line = dict(
                width=2,
                color='#000000'
            )
        ),
        xbins=dict(
            start=min_value,
            end=max_value,
            size=step_size
        )
    )]

    layout = go.Layout(
        xaxis=dict(
            title=xlabel,
            tick0=0,
            dtick=step_size_tick,
            tickfont=dict(
                size=20
            ),
            titlefont=dict(
                size=20
            )
        ),
        yaxis=dict(
            title='Projekt',
            tickfont=dict(
                size=20
            ),
            titlefont=dict(
                size=20
            )
        )
    )

    fig = go.Figure(data=data, layout=layout)
    plotly.offline.plot(fig, filename=('histogram ' + field))
