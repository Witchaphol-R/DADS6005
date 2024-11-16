import requests, time
import pandas as pd
import streamlit as st
import plotly.express as px

st.title("Real-Time Dashboards")

country_plot = st.empty()
hopping_plot = st.empty()
session_plot = st.empty()
tumbling_plot = st.empty()

country_df = pd.DataFrame()
hopping_df = pd.DataFrame()
session_df = pd.DataFrame()
tumbling_df = pd.DataFrame()

def run_query(df_old, table_name, date_col, group_col, metric, unit):
  query = {
    "sql": f"SELECT {group_col}, {date_col}, SUM({metric}) as {metric} "
           f"FROM {table_name} GROUP BY {group_col}, {date_col} "
           f"ORDER BY {date_col} DESC LIMIT 100"
  }
  response = requests.post("http://pinot-broker:8099/query/sql", json=query)
  response.raise_for_status()
  result = response.json()

  if 'resultTable' not in result or 'rows' not in result['resultTable']:
    return df_old

  columns = result['resultTable']['dataSchema']['columnNames']
  rows = result['resultTable']['rows']
  df = pd.DataFrame(rows, columns=columns)
  df_new = pd.concat([df, df_old]).drop_duplicates()
  try:
    df_new[date_col] = pd.to_datetime(df_new[date_col], unit=unit)
  except ValueError:
    df_new[date_col] = pd.to_datetime(df_new[date_col])
  return df_new

def create_plot(df, x, y, color, title):
  if df.empty:
    fig = px.scatter(title=title)
    fig.add_annotation(x=0, y=0,
      text="No data available",
      showarrow=False,
      font=dict(size=32, color="red")
    )
  else:
    fig = px.line(df, x=x, y=y, color=color, title=title)
  return fig

def main():
  global country_df, hopping_df, session_df, tumbling_df

  country_df = run_query(country_df, "pageview_country_REALTIME", "timestamp", "country", "pageview_count", "m")
  fig = create_plot(country_df, "timestamp", "pageview_count", "country", "Page Views by Country")
  country_plot.plotly_chart(fig)

  hopping_df = run_query(hopping_df, "pageview_hopping_REALTIME", "window_start", "source", "pageview_count", "m")
  fig = create_plot(hopping_df, "window_start", "pageview_count", "source", "Page Views by Source over Hopping Window")
  hopping_plot.plotly_chart(fig)

  session_df = run_query(session_df, "pageview_session_REALTIME", "window_start", "source", "pageview_count", "m")
  fig = create_plot(session_df, "window_start", "pageview_count", "source", "Page Views by Source over Session")
  session_plot.plotly_chart(fig)

  tumbling_df = run_query(tumbling_df, "pageview_tumbling_REALTIME", "window_start", "source", "pageview_count", "m")
  fig = create_plot(tumbling_df, "window_start", "pageview_count", "source", "Page Views by Source over Tumbling Window")
  tumbling_plot.plotly_chart(fig)

while True:
  main()
  time.sleep(15)