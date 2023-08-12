"""Script used to establish MongoDB connection with Streamlit."""

import pymongo

import streamlit as st

USERNAME = st.secrets["username"]
PASSWORD = st.secrets["password"]
CLUSTER = st.secrets["cluster"]

@st.cache_resource
def init_connection():
    return pymongo.MongoClient(
        f"mongodb+srv://{USERNAME}:{PASSWORD}@{CLUSTER}.turo8pf.mongodb.net/?tlsAllowInvalidCertificates=true"
    )
