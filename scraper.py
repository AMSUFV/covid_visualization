import io
import pandas as pd
import requests
from bs4 import BeautifulSoup


def scrap(address, save_csv=False):
    """Scraps https://github.com/CSSEGISandData/COVID-19 for the daily COVID19 updates and returns it as a pandas
    DataFrame.
    :param address: str. Web address.
    :param save_csv: bool. Whether or not to save the DataFrame as a csv
    :return: pandas.DataFrame
    """
    page = requests.get(address)
    soup = BeautifulSoup(page.content, 'html.parser')
    content = soup.get_text()

    data = io.StringIO(content)
    df = pd.read_csv(data)

    if save_csv:
        df.to_csv('COVID19.csv')

    return df
