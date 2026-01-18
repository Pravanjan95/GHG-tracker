import streamlit as st
import pandas as pd
import plotly.express as px
import os

# --- FILE PATHS ---
EXCEL_FILE = 'main_data.xlsx'
USER_DB = 'users.csv'

# --- INITIALIZE FILES (Matching your specific Excel structure) ---
if not os.path.exists(EXCEL_FILE):
    df_init = pd.DataFrame({
        'Category': ['Electricity', 'Natural Gas', 'Transport', 'Waste'],
        'Value': [450, 200, 150, 100],
        'Type': ['Direct', 'Direct', 'Indirect', 'Indirect']
    })
    df_init.to_excel(EXCEL_FILE, index=False)

if not os.path.exists(USER_DB):
    pd.DataFrame(columns=['username', 'password']).to_csv(USER_DB, index=False)

# --- APP CONFIG ---
st.set_page_config(page_title="GHG Tracker", layout="wide")

# --- AUTHENTICATION ---
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

def login_page():
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.title("🌱 GHG Management Portal")
        choice = st.radio("Select Action", ["Login", "Sign Up"], horizontal=True)

        if choice == "Login":
            username = st.text_input("Username").strip().lower()
            password = st.text_input("Password", type='password')
            if st.button("Login", use_container_width=True):
                users = pd.read_csv(USER_DB)
                users['username'] = users['username'].astype(str).str.strip().str.lower()
                if ((users['username'] == username) & (users['password'].astype(str) == str(password))).any():
                    st.session_state['logged_in'] = True
                    st.session_state['user'] = username
                    st.rerun()
                else:
                    st.error("Invalid Username or Password")

        else:
            new_user = st.text_input("New Username").strip().lower()
            new_pass = st.text_input("New Password", type='password')
            if st.button("Create Account", use_container_width=True):
                if new_user and new_pass:
                    users = pd.read_csv(USER_DB)
                    if new_user in users['username'].astype(str).values:
                        st.warning("User already exists!")
                    else:
                        new_entry = pd.DataFrame([[new_user, new_pass]], columns=['username', 'password'])
                        new_entry.to_csv(USER_DB, mode='a', header=False, index=False)
                        st.success("Account created! Please switch to Login.")

# --- MAIN APP ---
def main_app():
    # Sidebar Navigation
    st.sidebar.title(f"👤 {st.session_state['user'].capitalize()}")
    page = st.sidebar.radio("Navigation", ["Current Status & CO2 Contributor", "GHG Tracker", "Input for GHG Calc"])
    
    if st.sidebar.button("Logout"):
        st.session_state['logged_in'] = False
        st.rerun()

    # Read Excel Data
    df = pd.read_excel(EXCEL_FILE)

    if page == "Current Status & CO2 Contributor":
        st.header("Current Status & CO2 Contributor")
        # Using 'Value' instead of 'CO2_Value' to match your Excel
        fig = px.pie(df, values='Value', names='Category', 
                     title='Carbon Contribution by Category',
                     color_discrete_sequence=px.colors.sequential.Greens_r)
        st.plotly_chart(fig, use_container_width=True)

    elif page == "GHG Tracker":
        st.header("GHG Tracker")
        st.write("Distribution of Emissions")
        fig = px.pie(df, values='Value', names='Category', hole=0.4)
        st.plotly_chart(fig, use_container_width=True)

    elif page == "Input for GHG Calc":
        st.header("Update GHG Calculation Data")
        with st.form("update_form"):
            selected_cat = st.selectbox("Select Category to Update", df['Category'].unique())
            new_val = st.number_input("New Value", min_value=0.0, step=0.1)
            
            if st.form_submit_button("Update Main Excel File"):
                df.loc[df['Category'] == selected_cat, 'Value'] = new_val
                df.to_excel(EXCEL_FILE, index=False)
                st.success(f"Successfully updated {selected_cat} in the Excel sheet!")
                st.balloons()

# Run Control
if st.session_state['logged_in']:
    main_app()
else:
    login_page()