import streamlit as st
import pandas as pd
import plotly.express as px
import os

# --- FILE PATHS ---
EXCEL_FILE = 'main_data.xlsx'
USER_DB = 'users.csv'

# --- INITIALIZE FILES ---
if not os.path.exists(EXCEL_FILE):
    df_init = pd.DataFrame({
        'Category': ['Electricity', 'Natural Gas', 'Transport', 'Waste'],
        'Value': [450, 200, 150, 100],
        'Type': ['Direct', 'Direct', 'Indirect', 'Indirect']
    })
    df_init.to_excel(EXCEL_FILE, index=False)

if not os.path.exists(USER_DB):
    # Added 'recovery_key' to store a secret answer for password reset
    pd.DataFrame(columns=['username', 'password', 'recovery_key']).to_csv(USER_DB, index=False)

# --- APP CONFIG ---
st.set_page_config(page_title="GHG Tracker", layout="wide")

if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

# --- AUTHENTICATION FUNCTIONS ---
def login_page():
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.title("🌱 GHG Management Portal")
        choice = st.selectbox("Select Action", ["Login", "Sign Up", "Forgot Password"])

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

        elif choice == "Sign Up":
            new_user = st.text_input("New Username").strip().lower()
            new_pass = st.text_input("New Password", type='password')
            st.info("Recovery Key: This is used to reset your password if you forget it.")
            recovery_key = st.text_input("Favorite City or Secret Word")
            
            if st.button("Create Account", use_container_width=True):
                if new_user and new_pass and recovery_key:
                    users = pd.read_csv(USER_DB)
                    if new_user in users['username'].astype(str).values:
                        st.warning("User already exists!")
                    else:
                        new_entry = pd.DataFrame([[new_user, new_pass, recovery_key]], 
                                               columns=['username', 'password', 'recovery_key'])
                        new_entry.to_csv(USER_DB, mode='a', header=False, index=False)
                        st.success("Account created! Now select 'Login' above.")
                else:
                    st.error("Please fill all fields.")

        elif choice == "Forgot Password":
            st.subheader("Recover Password")
            user_to_find = st.text_input("Enter your Username").strip().lower()
            key_check = st.text_input("Enter your Recovery Key (Secret Word)")
            
            if st.button("Show Password", use_container_width=True):
                users = pd.read_csv(USER_DB)
                users['username'] = users['username'].astype(str).str.strip().str.lower()
                match = users[(users['username'] == user_to_find) & (users['recovery_key'].astype(str) == str(key_check))]
                
                if not match.empty:
                    st.success(f"Your password is: **{match.iloc[0]['password']}**")
                else:
                    st.error("Username or Recovery Key is incorrect.")

# --- MAIN APP ---
def main_app():
    st.sidebar.title(f"👤 {st.session_state['user'].capitalize()}")
    page = st.sidebar.radio("Navigation", ["Current Status & CO2 Contributor", "GHG Tracker", "Input for GHG Calc"])
    
    if st.sidebar.button("Logout"):
        st.session_state['logged_in'] = False
        st.rerun()

    df = pd.read_excel(EXCEL_FILE)

    if page == "Current Status & CO2 Contributor":
        st.header("Current Status & CO2 Contributor")
        fig = px.pie(df, values='Value', names='Category', 
                     title='Carbon Contribution by Category',
                     color_discrete_sequence=px.colors.sequential.Greens_r)
        st.plotly_chart(fig, use_container_width=True)

    elif page == "GHG Tracker":
        st.header("GHG Tracker")
        fig = px.pie(df, values='Value', names='Category', hole=0.4)
        st.plotly_chart(fig, use_container_width=True)

    elif page == "Input for GHG Calc":
        st.header("Update Data")
        with st.form("update_form"):
            selected_cat = st.selectbox("Select Category", df['Category'].unique())
            new_val = st.number_input("New Value", min_value=0.0, step=0.1)
            if st.form_submit_button("Update Data"):
                df.loc[df['Category'] == selected_cat, 'Value'] = new_val
                df.to_excel(EXCEL_FILE, index=False)
                st.success(f"Updated {selected_cat}!")

if st.session_state['logged_in']:
    main_app()
else:
    login_page()
