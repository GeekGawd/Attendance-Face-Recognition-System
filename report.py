import streamlit as st
import pandas as pd
import requests


data = requests.get("http://localhost:5000/report").json()

# Convert JSON to DataFrame
df = pd.DataFrame(data)

# Remove rows where 'student' is null
df = df[df['student'].notna()]

# Display the table
st.table(df)