# writing profile report to markdown

report_path = "reports/data_profiling_report.md"
with open(report_path, "w", encoding='utf-8') as f:
    f.write("# Data Profiling Report - Superstore Dataset\n\n")
    f.write("## Overview\n")
    f.write(f"- **Total Rows:** {df.shape[0]}\n")
    f.write(f"- **Total Columns:** {df.shape[1]}\n")
    f.write(f"- **Duplicate Rows:** {dup_count}\n\n")
    
    f.write("## Columns & Types\n")
    f.write("| Column Name | Data Type | Null Count | Null % | Unique Count |\n")
    f.write("| --- | --- | --- | --- | --- |\n")
    for col in df.columns:
        f.write(f"| {col} | {df[col].dtype} | {df[col].isnull().sum()} | {df[col].isnull().mean()*100:.2f}% | {df[col].nunique()} |\n")
    
    f.write("\n## Summary Statistics (Numeric)\n")
    desc = df.describe().reset_index()
    f.write("| " + " | ".join(desc.columns) + " |\n")
    f.write("| " + " | ".join(["---"] * len(desc.columns)) + " |\n")
    for index, row in desc.iterrows():
        row_str = " | ".join([f"{val:.2f}" if isinstance(val, (int, float)) else str(val) for val in row.values])
        f.write(f"| {row_str} |\n")
        
    f.write("\n## Key Data Quality Observations\n")
    if len(date_cols) >= 2:
        f.write(f"- **Date Anomalies ({ship_col} < {order_col}):** {date_anomaly}\n")
    for col in ['Sales', 'Quantity', 'Profit', 'Discount']:
        if col in df.columns:
            neg_count = (df[col] < 0).sum()
            f.write(f"- **Negative values in '{col}':** {neg_count}\n")
            
    # Check postal codes for integrity
    if 'Postal Code' in df.columns:
        df['Postal Code_Str'] = df['Postal Code'].apply(lambda x: str(int(x)).zfill(5) if pd.notnull(x) and not np.isnan(x) else '')
        invalid_postal = df[df['Postal Code_Str'] != '']['Postal Code_Str'].apply(lambda x: len(x) != 5).sum()
        null_postal = df['Postal Code'].isnull().sum()
        f.write(f"- **Potentially Malformed Postal Codes:** {invalid_postal} (expected 5-digit US postal codes)\n")
        f.write(f"- **Null Postal Codes:** {null_postal}\n")
        
    f.write("\n## Sample Data (Top 5 rows)\n")
    sample_df = df.head(5)
    f.write("| " + " | ".join(sample_df.columns) + " |\n")
    f.write("| " + " | ".join(["---"] * len(sample_df.columns)) + " |\n")
    for index, row in sample_df.iterrows():
        row_str = " | ".join([str(val) for val in row.values])
        f.write(f"| {row_str} |\n")

print(f"\nProfiling report saved to {report_path}")


