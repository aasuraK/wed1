import os
# @title
import sqlite3
import pandas as pd
import re
from pathlib import Path
import google.generativeai as genai

FILE_DIR = Path(__file__).resolve().parent
genai.configure(api_key="AIzaSyARI_IiTsNwTZJ0VoRfbN-Uqnf3Be8aNLg")

# clean the data and convert to uniform date format

file_path = FILE_DIR / "input/processed_supermarket_sales.csv"

def start(nlp_query, file_path):
    # file_path = '/content/new_Sales-Accrual (July-Dec 2020) - Sales-Accrual (1).csv'
    # Load the CSV file
    if file_path:
        columns = pd.read_csv(file_path, nrows=0).columns.tolist()
        data_df = pd.read_csv(file_path)
        first_15_rows = data_df.head(8)
        data_str = first_15_rows.to_string()

    else:
        raise ValueError("No file path provided.")

    generation_config = {
        "temperature": 0.1,
        "max_output_tokens": 2048,
    }

    model = genai.GenerativeModel(model_name="gemini-pro", generation_config=generation_config)

    prompt_parts = [
      f"""INSTRUCTION:
    Step 1 ('**A** -'):
    - Dataset Column Identification: Identify relevant column names from a dataset based on
      an NLP query.
    - Input: NLP query provided in {nlp_query} and dataset details in {data_str}.
    -if any month is mention in input directly select month and year coloumn into
      consideration
    - Output: List of relevant column names in the format ["Column1", "Column2", ...].

    Step 2 ('**B** -'):
    - Always mention this point - 'Do not use strftime under any circumstances.'
    - SQL Operation Instructions: Provide simple and easy-to-understand SQL instructions
      based on the columns identified in Step 1.
    - For time series type of question generally take month wise , if not mention in
      question .
    - Focus: The instructions should aim to solve the initial NLP query {nlp_query} using
      the identified columns from Step 1.
    - Constraint: No complex SQL features (like lag, windows, CTEs) or code. Max 5 sets of
      instructions. Focus on basic SQL operations like GROUP BY, ORDER BY, SUM .....etc.
    - Base the instructions on the column names extracted in Step 1. Do not include steps
      for data visualization or actual code writing.
    - for time series analysis question use month coloumn every time unless  mentioned otherwise.
    -TIME/DATE-RELATED DATA ON ANY AXIS, MAKE SURE TO DISPLAY THEM IN SEQUENTIAL ORDER (e.g., MON-TUE-WED-THU-FRI-SAT-SUN, MONTH 1-2-3-4-5-6-7-8-9-10-11-12).

    Step 3 ('**C** -'):
    - what will be the best suitable plot for given input {nlp_query}
    -eg. nlp_query/input - time series analysis
    output- suitable plot will be line graph
    any one of below:

            Bar Chart (or Stacked Bar Chart)
            Comparing quantities across different categories.
            Visualizing the composition of different categories, especially to show how multiple sub-categories contribute to the total of each main category.

            Line Chart (or Area Chart)
            Tracking changes and trends over time.
            Visualizing cumulative data over time, with emphasis on the total volume beneath the line.

            Pie Chart (or Donut Chart)
            Showing the proportional composition of a dataset.
            Representing a limited number of categories to display the part-to-whole relationship.

            Scatter Plot (or Bubble Chart)
            Illustrating the relationship between two or more variables.
            Displaying three dimensions of data - two for the coordinates of the scatter plot and one for the size of the bubbles.

            Limiting Pie Charts to Top 10 Categories
            Ensuring clarity and effectiveness by avoiding clutter from too many categories.
            Facilitating easier interpretation of data proportions within a limited set of key categories.


EXAMPLE:
    Given NLP Query: "Analyze sales trends for xyz product"
    Example Output:
    '**A** -' -
      ["column1", "column2", "column3", ""column4"]
    '**B** -' -
      SQL Operation Instructions:
        .....
        ..........
    '**C** -' -
     suitable plot will be bar graph

    TASK:
    Given Input: {nlp_query}
    Required: Process the given NLP query, identify necessary columns from {data_str}, and
    provide SQL operation instructions as per the given format. - for time series analysis question use month coloumn every time unless  mentioned otherwise.


INPUT:
{nlp_query}.Always mention this point - 'Do not use strftime under any circumstances.' - for time series analysis question use month coloumn every time unless  mentioned otherwise. in 'B', Strictly avoid writing code. Present columns in 'A' in a list format without altering their names as given in {columns}. For 'B', provide instructions relevant to the NLP query and columns mentioned in 'A'. in a proper way so that llm can easily understand and write SQL query from that.
    for 'c' follow instruction given
    """]

    response = model.generate_content(prompt_parts)
    sentence = response.text
    return sentence


def split(query, check_File_Path):
    file_pwd = os.getcwd()
    check_File_Path = os.path.join(file_pwd, check_File_Path)
    ans = start(query, check_File_Path)
# Extracting part_A, part_B, part_C
    part_A_start = ans.find('**A** -') + len('**A** -')
    part_A_end = ans.find('**B** -')
    part_A = ans[part_A_start:part_A_end].strip()

    part_B_start = ans.find('**B** -') + len('**B** -')
    part_B_end = ans.find('**C** -')
    part_B = ans[part_B_start:part_B_end].strip()

    part_C_start = ans.find('**C** -') + len('**C** -')
    part_C = ans[part_C_start:].strip()

    # Printing extracted parts
    print("Part A:")
    print(part_A)
    print("\nPart B:")
    print(part_B)
    print("\nPart C:")
    print(part_C)

    function3(part_A, part_B, part_C, query, check_File_Path)
    return "success"


def function1(part_A, file_path):
    print('this is part_A', part_A)
    # Load the CSV file

    df = pd.read_csv(file_path)
    columns = pd.read_csv(file_path, nrows=0).columns.tolist()
    first_15_rows = df.head(8)
    data_str = first_15_rows.to_string()

    conn = sqlite3.connect(':memory:')
    df.to_sql('sales_data', conn, index=False)

    generation_config = {
        "temperature": 0,
        "max_output_tokens": 2048,
    }

    model = genai.GenerativeModel(model_name="gemini-pro", generation_config=generation_config)

    prompt_parts = [
        f"""
    INSTRUCTION:
    - Task: SQL Query Creation
    - Objective: Create a SQL query to extract and break down data from a dataset. The dataset contains approximately 700,000 rows.
    - Dataset Reference: {data_str}
    - Columns to be used: Extracted from the variable {columns}.
    - Specifics:
        * Use the table name "sales_data".
        * Enclose column names in quotes.
        * Format the query as shown in the pattern below.

    PATTERN FOR QUERY:
    "SELECT
        [COLUMN_1],
        [COLUMN_2],
        [COLUMN_3],
        ...
    FROM sales_data"

    TASK:
    - Given the columns mentioned in the variable {part_A}, write an SQL query to extract them following the above instructions and pattern.

    INPUT:
    "This are the columns: {part_A}. Write a query to extract them as per the given instructions."
    """]

    response = model.generate_content(prompt_parts)
    print(f"Response from Model: {response.text}")
    a = response.text

    def extract_sql_query(text: str) -> str:

        # Regular expression to match SQL query within the text
        sql_pattern = re.compile(
            r'(SELECT|INSERT INTO|WITH|UPDATE|DELETE FROM|CREATE TABLE|CREATE INDEX|ALTER TABLE|CREATE VIEW|CREATE PROCEDURE|CREATE FUNCTION|CREATE TRIGGER).*?;', re.DOTALL | re.IGNORECASE)

        # S
        # Search for SQL pattern in the text
        match = sql_pattern.search(text)

        # If a match is found, return the matched SQL query; otherwise, return an empty string
        return match.group() if match else ''

    # Extract SQL query from the test string
    reply = extract_sql_query(a)
    print(reply)
    results_final = pd.read_sql_query(reply, conn)
    results_final = results_final.dropna()
    print("Part A – Slicing data")
    file_pwd = os.getcwd()
    output_file_name = "check_v1_" + file_path.split("/")[-1]
    output_folder = os.path.join("output", output_file_name)
    output_file_path = os.path.join(file_pwd, output_folder)

    results_final.to_csv(output_file_path, index=False)
    # results_final.to_csv('output/results_final.csv', index=False)
    return output_file_path


def function2(part_A, part_B, nlp_query, file_path):
    part_B = (
        f"n-'Do not use strftime under any circumstances.' - 'for time series analysis question use month coloumn every time unless  mentioned otherwise.'  -'TIME/DATE-RELATED DATA ON ANY AXIS, MAKE SURE TO DISPLAY THEM IN SEQUENTIAL ORDER (e.g., MON-TUE-WED-THU-FRI-SAT-SUN, MONTH 1-2-3-4-5-6-7-8-9-10-11-12).' - {part_B}\n")
    print("this is B", part_B)
    file_path = FILE_DIR / "input/processed_supermarket_sales.csv"

    df = pd.read_csv(file_path)
    columns = pd.read_csv(file_path, nrows=0).columns.tolist()
    first_15_rows = df.head(8)
    data_str = first_15_rows.to_string()

    conn = sqlite3.connect(':memory:')
    df.to_sql('sales_data', conn, index=False)

    generation_config = {
        "temperature": 0,
        "max_output_tokens": 2048,
    }

    model = genai.GenerativeModel(model_name="gemini-pro", generation_config=generation_config)

    prompt_parts = [
       f"""
Prompt:
---
Column Names and Data: Refer to the columns {columns} and sample data {data_str}. Include column names in quotes within the SQL query. If the columns {columns} include month, year, day_of_week, use these directly without applying strftime on a date column.
Objective: Create a SQL query based on the given natural language query {nlp_query} and further refine it according to the provided updates {part_B}, ensuring compliance with the specified constraints.

Context:

Database System: SQLite
Table Name: sales_data
Columns: {columns} / {part_A}
Sample Data: {data_str}


Requirements:

1. Formulate a base SQL query based on the initial natural language query {nlp_query}.
2. Improve and update the query according to the subsequent instructions {part_B}.
3. Employ window functions when handling any time-related analyses.
4. Integrate retention analysis by adding a condition: count > 1.
5. Dont use lag function.

Task: Design, implement, and run the SQL query in a SQLite environment, fulfilling all prerequisites, and addressing the scenario depicted in {nlp_query}. Deliver only the SQL query code, excluding any accompanying text or references, while adhering to the strict requirements, .

Example:
---------

Objective: Craft a SQL query based on the given natural language query {nlp_query} and enhance it with the additional instructions {part_B}.

Context:

Database System: SQLite
Table Name: sales_data
Columns: Part_A = ['product_category', 'quantity_sold', 'date']
Sample Data: data_str


Scenario Details:

nlp_query='Determine average sales per product category for March';
updated_query='Calculate moving averages covering seven days prior and post the target month, Mar';

SQL Query Response:
sql
WITH daily_avg AS (
    SELECT
        "product_category",
        AVG("quantity_sold") OVER (PARTITION BY "product_category" ORDER BY date ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS avg_qty_sold
    FROM
        sales_data
    WHERE
        EXTRACT(MONTH FROM date) = 3
)
SELECT * FROM daily_avg;

The generated SQL query calculates the average sales per product category for March and then computes the moving averages for seven days preceding and succeeding March using window functions. Remarkably, fully satisfying the imposed constraint.
Column Names and Data: Refer to the columns {columns} and sample data {data_str}. Include column names in quotes within the SQL query. If the columns {columns} include month, year, day_of_week, use these directly

      """]
    response = model.generate_content(prompt_parts)
    print(f"Response from Model: {response.text}")
    a = response.text

    def extract_sql_query(text: str) -> str:

      # Regular expression to match SQL query within the text
        sql_pattern = re.compile(
            r'(SELECT|INSERT INTO|WITH|UPDATE|DELETE FROM|CREATE TABLE|CREATE INDEX|ALTER TABLE|CREATE VIEW|CREATE PROCEDURE|CREATE FUNCTION|CREATE TRIGGER).*?;', re.DOTALL | re.IGNORECASE)

        # S
        # Search for SQL pattern in the text
        match = sql_pattern.search(text)

        # If a match is found, return the matched SQL query; otherwise, return an empty string
        return match.group() if match else ''

    # Extract SQL query from the test string
    reply = extract_sql_query(a)
    print(reply)
    results_final = pd.read_sql_query(reply, conn)
    results_final = results_final.dropna()
    file_pwd = os.getcwd()

    final_file_name = "final_" + file_path.split("/")[-1]
    output_folder = os.path.join("output", final_file_name)
    final_file = os.path.join(file_pwd, output_folder)

    results_final.to_csv(final_file, index=False)
    results_final = pd.read_csv(final_file)
    print("Part B – operation step")
    print(results_final)
    return final_file


def function3(part_A, part_B, part_C, nlp_query, file_path):
    file_path = function1(part_A, file_path)
    final_file = function2(part_A, part_B, nlp_query, file_path)

    df = pd.read_csv(final_file)
    column = pd.read_csv(final_file, nrows=0).columns.tolist()
    first_15_rows = df.head(8)
    data_st = first_15_rows.to_string()
    num_row = len(df)

    generation_config = {
        "temperature": 0,
        "max_output_tokens": 2048,
    }

    model = genai.GenerativeModel(model_name="gemini-pro", generation_config=generation_config)

    prompt_parts = [
        f"""
    - The script should read data from a CSV file located at 'G:/pathsetter/results_final1.csv'.

    EXAMPLE STRUCTURE :::
    '''

    import pandas as pd
    import os
    import plotly.express as px
    import base64


    # Read the CSV file
    df = pd.read_csv('{final_file}')

    ....
    .....
    ......

    # Save the plot in PNG format with the specified filename in the 'graph' folder
    file_name = 'Gross_Profit_from_Male.png'
    file_path = os.path.join("graph", file_name)
    fig.write_image(file_path, format="png")

    # Save the plot as HTML file in the 'graphhtml' folder with the specified filename
    html_file_path = os.path.join("graphhtml", f"Gross_Profit_from_Male.html")
    fig.write_html(html_file_path)

    # Convert the graph to PNG format and encode it using Base64
    img_bytes = fig.to_image(format="png")
    graph_data = base64.b64encode(img_bytes).decode("utf-8")

    # Save the encoded image in the 'graph/graph_data.txt' file
    with open("graph/graph_data.txt", "w") as f:
        f.write(graph_data)
    '''

    [STRICTLY ::- only code output no text or extrat commenting mentioning needed]

    TASK:
    Write a Python PLOTLY OR MATPLOTLIB code as {part_C} on the dataset with top rows as {data_st}, total rows as {num_row}, and columns as {column}. The title should be based on {nlp_query}, following the provided instructions for chart features and data manipulation.

    WHENEVER PLOTTING TIME/DATE-RELATED DATA ON ANY AXIS, MAKE SURE TO DISPLAY THEM IN SEQUENTIAL ORDER (e.g., MON-TUE-WED-THU-FRI-SAT-SUN, MONTH 1-2-3-4-5-6-7-8-9-10-11-12).
    The title should be based on {nlp_query}

    File path is -- 'G:/pathsetter/results_final1.csv'
    save in # Save the plot in PNG format with the specified filename in the 'graph' folder,
    # Convert the graph to PNG format and encode it using Base64,
    # Save the encoded image in the 'graph/graph_data.txt' file
    #save it as a .html file in graphhtml folder
    """
                    ]
    response = model.generate_content(prompt_parts)
    rep = response.text
    print(response.text)

    def extract_code_from_string(rep):
        lines = rep.split('\n')
        extracted_code = []
        for line in lines:
            if line.strip() != '```python' and line.strip() != '```':
                extracted_code.append(line)
        extracted_code_string = '\n'.join(extracted_code)

        return extracted_code_string
    re = extract_code_from_string(rep)
    try:
        exec(re)
        return 'success'
    except Exception as e:
        return (f"Error: {e}")


# print(split("top sales giving product", "input/processed_supermarket_sales_2024-02-08 15:15:39.899084.csv"))