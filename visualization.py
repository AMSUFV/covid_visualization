import pandas as pd
import holoviews as hv

from datetime import datetime, timedelta
from holoviews import opts
from urllib.error import URLError
hv.extension('bokeh')

url = 'https://covid19.isciii.es/resources/serie_historica_acumulados.csv'


def get_data(csv_url):
    try:
        df = pd.read_csv(csv_url, engine='python', skipfooter=2)
        df.to_csv('COVID19_Spain.csv', index=False)
    except URLError:
        df = pd.read_csv('COVID19_Spain.csv')
    return df


def preprocess(df):
    df.rename(columns={'CCAA Codigo ISO': 'Comunidad Autónoma'}, inplace=True)
    df.columns = map(str.rstrip, df.columns)

    # Avoiding user's input mistakes
    df.fillna(value=0, inplace=True)
    # Removing characters from columns
    for col in df.columns[-4:]:
        df[col] = df[col].astype(str)
        df[col] = df.loc[:, col].str.replace(r'\.0', '')
        df[col] = df.loc[:, col].str.replace(r'\D', '')
        df[col] = df.loc[:, col].astype(int)

    df.Fecha = pd.to_datetime(df.Fecha, format='%d/%m/%Y')
    #     df.Fecha = df.loc[:, 'Fecha'].dt.strftime('%d-%m')

    # Autonomous communities names
    tag_list = ['MD', 'CT', 'PV', 'CL', 'CM', 'AN', 'VC', 'GA', 'NC', 'AR', 'RI', 'EX', 'AS', 'CN', 'CB', 'IB', 'MC',
                'ME', 'CE']
    name_list = ['Madrid', 'Cataluña', 'País Vasco', 'Castilla y León', 'Castilla-La Mancha', 'Andalucía',
                 'Comunidad Valenciana', 'Galicia', 'Comunidad Foral de Navarra', 'Aragón', 'La Rioja', 'Extremadura',
                 'Principado de Asturias', 'Canarias', 'Cantabria', 'Islas Baleares', 'Murcia', 'Melilla', 'Ceuta']
    df.replace(tag_list, name_list, inplace=True)

    return df


def get_global(complete_df):
    # preprocessing
    df = complete_df[['Comunidad Autónoma', 'Fecha', 'Casos']]
    df = df.sort_values(by=['Casos'], ascending=False)
    df.reset_index(drop=True, inplace=True)

    # plot
    key_dimensions = ['Fecha', 'Comunidad Autónoma']
    value_dimensions = ['Casos']
    # for better date representation
    df.Fecha = df.loc[:, 'Fecha'].dt.strftime('%d-%m')

    macro = hv.Table(df, key_dimensions, value_dimensions)
    fig = macro.to.bars(key_dimensions, value_dimensions, [], label='Total')

    color_cycle = hv.Palette('Category20')
    fig.opts(
        opts.Bars(color=color_cycle, aspect=16 / 9, xrotation=90, ylabel='', xlabel='Fecha',
                  responsive=True, fontsize=dict(xticks='8pt'), active_tools=['pan', 'wheel_zoom'],
                  tools=['hover'], stacked=True, show_legend=False, title='Desglose por comunidades'),
    )
    return fig


def get_ccaa(complete_df):
    # preprocessing
    df = complete_df.copy()
    df['Leves'] = abs(df['Casos'] - (df['Hospitalizados'] + df['UCI']))
    df = df[['Comunidad Autónoma', 'Fecha', 'Leves', 'Hospitalizados', 'UCI', 'Fallecidos']]

    df = pd.melt(df, id_vars=df.columns[:2], var_name='Estado', value_name='Número')

    # plot
    key_dimensions = ['Fecha', 'Estado']
    value_dimensions = ['Número']

    # for better date representation
    df.Fecha = df.loc[:, 'Fecha'].dt.strftime('%d-%m')

    macro = hv.Table(df, key_dimensions, value_dimensions)
    fig = macro.to.bars(key_dimensions, value_dimensions, 'Comunidad Autónoma')

    color_cycle = hv.Cycle(['#FEE5AD', '#F7A541', '#F45D4C', '#2E2633'])
    fig.opts(
        opts.Bars(color=color_cycle, show_legend=True, stacked=True, aspect=16 / 9,
                  ylabel='', xlabel='Fecha', responsive=True, tools=['hover'], title='Desglose por estado',
                  legend_position='top_left', xrotation=90, active_tools=['pan', 'wheel_zoom']),
    )
    return fig


def get_daily_increment(complete_df):
    df = complete_df.copy()


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
    layout.opts(
        opts.Layout(show_title=False, shared_axes=False)
    )

    renderer = hv.renderer('bokeh')
    renderer.save(layout, 'docs/index.html')


def generate_html(csv_url):
    get_dashboard(csv_url)


if __name__ == '__main__':
    generate_html(url)
