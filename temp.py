import pdfplumber
import pandas as pd
import numpy as np

def extract_tables_from_pdf(pdf_path):
    all_tables = []
    
    # Table extraction settings
    table_settings = {
        "vertical_strategy": "lines",
        "horizontal_strategy": "lines",
        "intersection_tolerance": 5
    }
    
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                tables = page.extract_tables(table_settings)
                for table in tables:
                    all_tables.append(table)
    except Exception as e:
        print(f"Error opening PDF file: {e}")
    
    return all_tables

def extract_text_from_pdf(pdf_path):
    all_text = []
    
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    all_text.append(text)
    except Exception as e:
        print(f"Error opening PDF file: {e}")
    
    return "\n".join(all_text)  # Join pages with newlines for better separation

def clean_table(table):
    # Handle empty tables
    if not table or not table[0]:
        return pd.DataFrame()
    
    # Convert table to DataFrame
    df = pd.DataFrame(table[1:], columns=table[0])
    
    # Drop rows and columns where all elements are NaN
    df.dropna(how='all', inplace=True)
    df.dropna(axis=1, how='all', inplace=True)
    
    # Reset index
    df.reset_index(drop=True, inplace=True)
    
    # Forward fill for merged cells (NaNs resulting from merged cells in the PDF)
    df.ffill(axis=0, inplace=True)
    
    # Strip whitespace from headers and data
    df.columns = df.columns.str.strip()
    df = df.apply(lambda x: x.str.strip() if x.dtype == "object" else x)  # Use apply with lambda
    
    return df

def validate_and_standardize_columns(dfs):
    # Get the set of all column names
    all_columns = set()
    for df in dfs:
        all_columns.update(df.columns)
    
    # Remove any NoneType values
    all_columns = {col for col in all_columns if col is not None}
    
    # Ensure all DataFrames have the same columns
    standardized_dfs = []
    for df in dfs:
        for col in all_columns:
            if col not in df.columns:
                df[col] = np.nan  # Add missing columns with NaN values
        standardized_dfs.append(df[sorted(all_columns)])  # Sort columns alphabetically
    
    return standardized_dfs

def convert_pdf_to_csv(pdf_path, csv_path):
    all_tables = extract_tables_from_pdf(pdf_path)
    text_content = extract_text_from_pdf(pdf_path)
    
    # Convert tables to DataFrames and clean them
    df_list = [clean_table(table) for table in all_tables if clean_table(table).shape[0] > 0]
    
    # Write tables to CSV
    try:
        with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
            writer = pd.ExcelWriter(csvfile, engine='xlsxwriter')
            
            if df_list:
                # Validate and standardize columns across all DataFrames
                df_list = validate_and_standardize_columns(df_list)
                
                # Concatenate all DataFrames into one
                final_df = pd.concat(df_list, ignore_index=True)
                
                # Write tables to CSV
                final_df.to_csv(csvfile, index=False)
            
            # Write text content to CSV as a new section
            text_df = pd.DataFrame({"Text Content": [text_content]})
            text_df.to_csv(csvfile, mode='a', index=False)
            
            print(f"Data has been successfully extracted and saved to {csv_path}")
    except Exception as e:
        print(f"Error saving CSV file: {e}")

# Define the path to the PDF file and the output CSV file
pdf_path = "tests\sample file 2table.pdf"
csv_path = "D:\output_file.csv"

convert_pdf_to_csv(pdf_path, csv_path)
