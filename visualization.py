import pandas as pd
import holoviews as hv

from datetime import datetime, timedelta
from holoviews import opts
hv.extension('bokeh')

url = 'https://covid19.isciii.es/resources/serie_historica_acumulados.csv'


def get_data(csv_url):
    df = pd.read_csv(csv_url, engine='python', skipfooter=1)
    return df


def preprocess(df):
    df.rename(columns={'CCAA Codigo ISO': 'Comunidad Autónoma'}, inplace=True)
    df.columns = map(str.rstrip, df.columns)

    df.Fecha = pd.to_datetime(df.Fecha, format='%d/%m/%Y')
    df.Fecha = df.loc[:, 'Fecha'].dt.strftime('%d-%m')

    return df


# plot
def get_global(complete_df):
    # preprocessing
    df = complete_df[['Comunidad Autónoma', 'Fecha', 'Casos']]

    # plot
    key_dimensions = ['Fecha']
    value_dimensions = ['Casos', 'Comunidad Autónoma']
    macro = hv.Table(df, key_dimensions, value_dimensions)
    fig = macro.to.bars(key_dimensions, 'Casos', 'Comunidad Autónoma', label='global')
    fig.opts(
        opts.Bars(aspect=16 / 9, xrotation=90, ylabel='', xlabel='Fecha',
                  responsive=True, fontsize=dict(xticks='8pt'),
                  tools=['hover'], title='Casos totales', shared_axes=False),
    )

    return fig


# plot
def get_ccaa(complete_df):
    # preprocessing
    df = complete_df.drop(columns=['Casos'])
    #     df.dropna(axis=0, thresh=1, subset=df.columns[-3:], inplace=True)

    df = pd.melt(df, id_vars=df.columns[:2], var_name='Estado', value_name='Número')

    # plot
    key_dimensions = ['Fecha', 'Estado']
    value_dimensions = ['Número', 'Comunidad Autónoma']

    macro = hv.Table(df, key_dimensions, value_dimensions)

    color_cycle = hv.Cycle(['#ffb940', '#d96859', '#000000'])
    fig = macro.to.bars(['Fecha', 'Estado'], 'Número', 'Comunidad Autónoma', label='ccaa')
    fig.opts(
        opts.Bars(color=color_cycle, show_legend=True, stacked=True, aspect=16 / 9,
                  ylabel='', xlabel='Fecha', responsive=True, tools=['hover'],
                  legend_position='top_left', xrotation=90, title='Desglose'),
    )
    return fig


def get_dashboard(csv_url):
    # obtaining data
    df = get_data(csv_url)
    # preprocessing
    df = preprocess(df)
    # all cases
    fig_global = get_global(df)
    # hospitalized, ICU and deceased
    fig_ccaa = get_ccaa(df)

    layout = hv.Layout(fig_global + fig_ccaa)

    renderer = hv.renderer('bokeh')
    renderer.save(layout, 'docs/index.html')


def generate_html(csv_url):
    get_dashboard(url)


if __name__ == '__main__':
    generate_html(url)
