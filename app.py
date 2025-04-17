
# imports
import streamlit as st
import pandas as pd 
import os
from io import BytesIO

# app setup
st.set_page_config(page_title="Data Sweeper", layout='wide')
st.title("🧹📁 Data Sweeper")
st.write("Streamline your file conversions from CSV to Excel and back—complete with built-in data cleanup and charts!")
st.write("by Shahzar Khan")

# file upload
uploaded_files = st.file_uploader(
    "Upload your files (CSV or Excel):", 
    type=["csv", "xlsx"], 
    accept_multiple_files=True
)

if uploaded_files:
    for file in uploaded_files:
        file_ext = os.path.splitext(file.name)[-1].lower()
        key_name = f"{file.name}_df"

        # Load and store in session state if not already there
        if key_name not in st.session_state:
            if file_ext == ".csv":
                st.session_state[key_name] = pd.read_csv(file)
            elif file_ext == ".xlsx":
                st.session_state[key_name] = pd.read_excel(file)
            else:
                st.error(f"Unsupported file type {file_ext}")
                continue

        df = st.session_state[key_name]

        # Display info
        st.write(f"**File Name:** {file.name}")
        st.write(f"**File Size:** {file.size / 1024:.2f} KB")
        st.write("**First Few Rows of Data:**")
        st.dataframe(df.head())

        # Data cleaning options
        st.subheader("Data Cleaning Options")
        if st.checkbox(f"Clean Data for {file.name}"):
            col1, col2 = st.columns(2)

            with col1:
                if st.button(f"Remove Duplicates from {file.name}"):
                    st.session_state[key_name].drop_duplicates(inplace=True)
                    st.success("Duplicates Removed!")

            with col2:
                if st.button(f"Filling Missing Values for {file.name}"):
                    numeric_cols = st.session_state[key_name].select_dtypes(include=['number']).columns
                    st.session_state[key_name][numeric_cols] = st.session_state[key_name][numeric_cols].fillna(
                        st.session_state[key_name][numeric_cols].mean()
                    )
                    st.success("Missing Values Filled!")

        # Column selector
        st.subheader("Select Columns to Convert")
        columns = st.multiselect(
            f"Choose Columns for {file.name}", 
            df.columns, 
            default=df.columns
        )

        # Visualization
        st.subheader("Data Visualization")
        if st.checkbox(f"Show Visualizations for {file.name}"):
            numeric = st.session_state[key_name][columns].select_dtypes(include=['number'])
            if not numeric.empty:
                st.bar_chart(numeric.iloc[:, :2])
            else:
                st.info("No numeric columns available for visualization.")

        # Conversion
        st.subheader("Conversion Options")
        conversion_type = st.radio(
            f"Convert {file.name} to:",
            ["CSV", "Excel"],
            key=f"conversion_type_{file.name}"
        )

        if st.button(f"Convert {file.name}"):
            buffer = BytesIO()
            df_to_export = st.session_state[key_name][columns]

            if conversion_type == "CSV":
                df_to_export.to_csv(buffer, index=False)
                file_name = file.name.replace(file_ext, ".csv")
                mime_type = "text/csv"
            elif conversion_type == "Excel":
                df_to_export.to_excel(buffer, index=False)
                file_name = file.name.replace(file_ext, ".xlsx")
                mime_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"

            buffer.seek(0)

            st.download_button(
                label=f"Download {file.name} as {conversion_type}",
                data=buffer,
                file_name=file_name,
                mime=mime_type
            )
            st.success("All Files Processed Successfully!")
