import numpy as np
import holoviews as hv
import pandas as pd

from datetime import datetime
from holoviews import opts
from urllib.error import URLError
hv.extension('bokeh')

url = 'https://covid19.isciii.es/resources/serie_historica_acumulados.csv'
width = 900
height = 450


def get_data(csv_url):
    try:
        df = pd.read_csv(csv_url, engine='python', skipfooter=1)
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


def render(figure, name):
    renderer = hv.renderer('bokeh')
    renderer.save(figure, f'{name}.html')


def get_acc_table(complete_df):
    daily_cases = complete_df.groupby('Fecha').sum()
    daily_cases = daily_cases.reindex(index=daily_cases.index[::-1])
    table = hv.Table(daily_cases, kdims='Fecha', vdims=list(daily_cases.columns)[0:], label='Tabla')
    table.opts(width=width, height=450, show_title=False)
    return table


def get_ccaa(complete_df):
    # preprocessing
    df = complete_df[['Comunidad Autónoma', 'Fecha', 'Casos']]

    df = df.sort_values(by='Casos', ascending=False)
    df.reset_index(drop=True, inplace=True)

    # plot
    # for better date representation
    df.Fecha = df.loc[:, 'Fecha'].dt.strftime('%d-%m')

    color_cycle = hv.Palette('Inferno')
    opts_dict = dict(color=color_cycle, width=width, height=450, xrotation=90, invert_xaxis=True, shared_axes=False,
                     tools=['hover'], stacked=True, show_legend=False, colorbar=True, line_color='white',
                     show_grid=True, show_title=False)

    bars = hv.Bars(df, kdims=['Fecha', 'Comunidad Autónoma'], vdims='Casos', label='Escala lineal')
    bars.opts(**opts_dict)

    log_bars = hv.Bars(df, kdims=['Fecha', 'Comunidad Autónoma'], vdims='Casos', label='Escala logarítmica')

    opts_dict['logy'] = True
    opts_dict['title'] = 'Escala logarítmica'
    log_bars.opts(**opts_dict)

    layout = (bars * log_bars)
    layout.opts(tabs=True, title='Casos por comunidad')

    return layout


def get_ccaa_heatmap(complete_df):
    df = complete_df[['Comunidad Autónoma', 'Fecha', 'Casos']]
    df = df.sort_values(by=['Comunidad Autónoma', 'Fecha'], ascending=[False, True])
    df.Fecha = df.loc[:, 'Fecha'].dt.strftime('%d-%m')

    heatmap = hv.HeatMap(df, kdims=['Fecha', 'Comunidad Autónoma'], vdims='Casos')
    heatmap.opts(width=width, height=450, tools=['hover'], logz=True, title='Casos acumulados',
                 toolbar='above', xlabel='Fecha', ylabel='', colorbar=True, clim=(1, np.nan), xrotation=90)
    return heatmap


def get_split(complete_df):
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
    bars = macro.to.bars(key_dimensions, value_dimensions, 'Comunidad Autónoma')

    # color_cycle = hv.Cycle(['#FEE5AD', '#F7A541', '#F45D4C', '#2E2633'])
    color_cycle = hv.Palette('Inferno', reverse=True)
    bars.opts(
        opts.Bars(color=color_cycle, show_legend=True, stacked=True, width=900, height=450, shared_axes=False,
                  ylabel='', xlabel='Fecha', responsive=True, tools=['hover'], title='Desglose por estado',
                  legend_position='top_left', xrotation=90, active_tools=['pan', 'wheel_zoom']),
    )
    return bars


def get_daily_increment(complete_df):
    df = complete_df.copy()

    # preprocessing
    # New columns
    for column in df.columns[-4:]:
        df[f'Incremento porcentual en {column}'] = ''
        df[f'Incremento diario en {column}'] = ''

    key_values = ['Casos', 'Hospitalizados', 'UCI', 'Fallecidos']
    for ccaa in df['Comunidad Autónoma'].unique():
        for value in key_values:
            before = df.loc[df['Comunidad Autónoma'] == ccaa, :][value][1:]
            after = df.loc[df['Comunidad Autónoma'] == ccaa, :][value][:-1]
            difference = before.values - after.values
            difference = np.append(difference, 0)

            # daily increment
            df.loc[df['Comunidad Autónoma'] == ccaa, f'Incremento diario en {value}'] = difference
            # daily percentual increment, you have to replace the zeros for ones in order to divide properly
            divisor = df.loc[df['Comunidad Autónoma'] == ccaa, :][value][:].values
            divisor = np.where(divisor == 0, 1, divisor)

            increment = difference / divisor
            df.loc[df['Comunidad Autónoma'] == ccaa, f'Incremento porcentual en {value}'] = increment

    df = pd.concat([df[['Comunidad Autónoma', 'Fecha']], df.filter(regex='Incremento')], axis=1)
    df = pd.melt(df, id_vars=df.columns[:2], var_name='Estado', value_name='Incremento')

    # plot
    key_dimensions = ['Fecha', 'Estado']
    value_dimensions = ['Incremento']

    # for better date representation
    df.Fecha = df.loc[:, 'Fecha'].dt.strftime('%d-%m')

    # barplot
    #     macro = hv.Table(df, key_dimensions, value_dimensions)
    #     fig = macro.to.bars(key_dimensions, value_dimensions, ['Comunidad Autónoma', 'Estado'])

    #     fig.opts(
    #         opts.Bars(show_legend=True, stacked=True, aspect=16 / 9,
    #                   ylabel='', xlabel='Fecha', responsive=True, tools=['hover'], title='Incremento',
    #                   legend_position='top_left', xrotation=90, active_tools=['pan', 'wheel_zoom']),
    #     )


def get_dashboard(csv_url):
    # obtaining data
    df = get_data(csv_url)

    # preprocessing
    df = preprocess(df)

    # global cases by ccaa
    fig_global = get_ccaa(df)
    # heatmap and table
    heatmap = get_ccaa_heatmap(df)
    table = get_acc_table(df)

    layout = (fig_global + heatmap * table).cols(2)
    render(layout, 'docs/index')


def generate_html(csv_url):
    get_dashboard(csv_url)


if __name__ == '__main__':
    generate_html(url)
