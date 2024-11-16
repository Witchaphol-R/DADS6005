import requests
import pandas as pd
import streamlit as st

st.write('Test')

PINOT_BROKER_URL = "http://pinot-broker:8099/query/sql"

queries = [
  {"sql": "SELECT * FROM pageview_country_REALTIME LIMIT 10"}
  , {"sql": "SELECT * FROM pageview_hopping_REALTIME LIMIT 10"}
  , {"sql": "SELECT * FROM pageview_session_REALTIME LIMIT 10"}
  , {"sql": "SELECT * FROM pageview_tumbling_REALTIME LIMIT 10"}
]

dfs = []
for query in queries:
  response = requests.post(PINOT_BROKER_URL, json=query)
  if response.status_code == 200:
    result = response.json()
    columns = result['resultTable']['dataSchema']['columnNames']
    rows = result['resultTable']['rows']
    df = pd.DataFrame(rows, columns=columns)
    dfs.append(df)

st.title('Realtime Dashboard')

st.subheader('Pageview Country')
st.write(dfs[0])

st.subheader('Pageview Hopping')
st.write(dfs[1])

st.subheader('Pageview Session')
st.write(dfs[2])

st.subheader('Pageview Tumbling')
st.write(dfs[3])