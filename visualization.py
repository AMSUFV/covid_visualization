import pandas as pd
import holoviews as hv

from datetime import datetime, timedelta
from holoviews import opts
hv.extension('bokeh')

url = 'https://covid19.isciii.es/resources/serie_historica_acumulados.csv'
window = 20


def get_data(csv_url):
    df = pd.read_csv(csv_url, engine='python', skipfooter=1)
    return df


def preprocess(df):
    df.rename(columns={'CCAA Codigo ISO': 'Comunidad Autónoma'}, inplace=True)

    df.Fecha = pd.to_datetime(df.Fecha, format='%d/%m/%Y')

    # df = df[df.Fecha > datetime.today() - timedelta(days=window)]
    df.drop(columns=['Casos '], inplace=True)
    df.dropna(axis=0, thresh=1, subset=df.columns[-3:], inplace=True)

    df = pd.melt(df, id_vars=df.columns[:2], var_name='Estado', value_name='Número')

    df.Fecha = df.loc[:, 'Fecha'].dt.strftime('%d-%m')
    key_dimensions = ['Fecha', 'Estado']
    value_dimensions = ['Número', 'Comunidad Autónoma']

    return df, key_dimensions, value_dimensions


def get_dashboard(df, key_dimensions, value_dimensions):
    macro = hv.Table(df, key_dimensions, value_dimensions)

    color_cycle = hv.Cycle(['#ffb940', '#d96859', '#000000'])
    fig = macro.to.bars(['Fecha', 'Estado'], 'Número', 'Comunidad Autónoma')
    fig.opts(
        opts.Bars(color=color_cycle, show_legend=True, stacked=True, aspect=16/9,
                  ylabel='', xlabel='Fecha', responsive=True, tools=['hover'],
                  legend_position='top_left'),
        opts.Overlay(show_frame=False, responsive=True)
            )
    renderer = hv.renderer('bokeh')
    renderer.save(fig, 'docs/index.html')


def generate_html(csv_url):
    df = get_data(csv_url)
    df, key_dim, val_dim = preprocess(df)
    get_dashboard(df, key_dim, val_dim)


if __name__ == '__main__':
    generate_html(url)
