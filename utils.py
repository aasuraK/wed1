import os
# @title
import sqlite3
import pandas as pd
import re
from pathlib import Path
from openai import OpenAI

FILE_DIR = Path(__file__).resolve().parent

# clean the data and convert to uniform date format
def check(file_path):
    # file_path = '/content/new_Sales-Accrual (July-Dec 2020) - Sales-Accrual (1).csv'
    # Load the CSV file
    if file_path:
        df = pd.read_csv(file_path, encoding='ISO-8859-1')
    else:
        raise ValueError("No file path provided.")
    first_15_rows = df.head(8)
    client = OpenAI(
        # defaults to os.environ.get("OPENAI_API_KEY")
        api_key='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',
    )
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a powerful text-to-SQL model. Your job is to answer questions about a database. You are given a question and context regarding one or more tables.\n\nYou must output the SQL query that answers the question.\n"},
            {"role": "user", "content":
                f'''Based on the data snippet provided:
        Invoice ID	Branch	City	Customer type	Gender	Product line	Unit price	Quantity	Tax 5%	Total	date	Time	Payment	cogs	gross margin percentage	gross income	Rating
        750-67-8428	A	Yangon	Member	Female	Health and beauty	74.69	7	26.1415	548.9715	01-05-2019	13:08	Ewallet	522.83	4.761904762	26.1415	9.1
        226-31-3081	C	Naypyitaw	Normal	Female	Electronic accessories	15.28	5	3.82	80.22	03-08-2019	10:29	Cash	76.4	4.761904762	3.82	9.6
        631-41-3108	A	Yangon	Normal	Male	Home and lifestyle	46.33	7	16.2155	340.5255	03-03-2019	13:23	Credit card	324.31	4.761904762	16.2155	7.4
        123-19-1176	A	Yangon	Member	Male	Health and beauty	58.22	8	23.288	489.048	1/27/2019	20:33	Ewallet	465.76	4.761904762	23.288	8.4
        373-73-7910	A	Yangon	Normal	Male	Sports and travel	86.31	7	30.2085	634.3785	02-08-2019	10:37	Ewallet	604.17	4.761904762	30.2085	5.3
        699-14-3026	C	Naypyitaw	Normal	Male	Electronic accessories	85.39	7	29.8865	627.6165	3/25/2019	18:30	Ewallet	597.73	4.761904762	29.8865	4.1
        355-53-5943	A	Yangon	Member	Female	Electronic accessories	68.84	6	20.652	433.692	2/25/2019	14:36	Ewallet	413.04	4.761904762	20.652	5.8, identify the column that is most likely to be the date column and respond with the phrase The most probable date column is :'''},
            {"role": "assistant", "content": "The date coloumn will be 'date' "},
            {"role": "system", "content": "you are data analyst with experty in excel, sql, python"},
            {"role": "user", "content":
                f"Based on the data snippet provided: {first_15_rows}, identify the column that is most likely to be the date column and respond with the phrase "}
        ],
        temperature=0,
        max_tokens=2100
    )
    sentence = response.choices[0].message.content

    # Step 1: Extract column name from the sentence
    match = re.search(r"['\"](.*?)['\"]", sentence)
    if match:
        column_name = match.group(1)
    else:
        raise ValueError("No column name found in the sentence.")

    # Step 2: Check if this column exists in your DataFrame columns
    if column_name not in df.columns.tolist():
        raise ValueError(f"Column '{column_name}' not found in DataFrame.")

    # Step 3: Convert the specified column to a uniform date format
    # (Attempting to convert to datetime, letting Pandas infer the format)
    df[column_name] = pd.to_datetime(df[column_name], errors='coerce')

    # Filter out rows with invalid or missing dates
    df = df[df[column_name].notnull()]

    # Convert the date column back to a uniform date format (YYYY-MM-DD)
    df[column_name] = df[column_name].dt.strftime('%Y-%m-%d')

    # Step 4: Create new columns for month and year
    # df['month'] = pd.to_datetime(df[column_name]).dt.month
    df['year'] = pd.to_datetime(df[column_name]).dt.year
    df['day_of_week'] = pd.to_datetime(df[column_name]).dt.day_name()

    output_file_name = "check_v1_" + file_path.split("/")[-1]

    output_file_path = os.path.join("output", output_file_name)

    df.to_csv(output_file_path, index=False)
    file_path = output_file_path
    return file_path


# Using OpenAI API to convert NLP to SQL and generate insights
def start(file_path, nlp_query):
    df = pd.read_csv(file_path)
    columns = pd.read_csv(file_path, nrows=0).columns.tolist()
    first_15_rows = df.head(8)
    # openai.api_key = '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'

    # Load the CSV file into a pandas DataFrame (again)
    data_df = pd.read_csv(file_path)
    data_str = first_15_rows.to_string()

    # Re-establish the SQLite connection and table
    conn = sqlite3.connect(':memory:')
    data_df.to_sql('sales_data', conn, index=False)
    b = nlp_query
    try:
        # Write the SQL query
        # Check if "day to day", "month to month", or "year to year" is present in the nlp_query
        if any(phrase in nlp_query for phrase in ["day to day", "month to month", "year to year"]):
            nlp_query += f" (use lag function) and {a}"
        client = OpenAI(
            api_key='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',
        )
        query = client.chat.completions.create(
            model="gpt-3.5-turbo-16k",
            messages=[{"role": "system", "content": "your task is to convert nlp query to proper prompt to ask gpt model for making an sql query try making relation with other coloumns as well"},
                      {"role": "user", "content": "Best Performing Service in Terms of Sales and Quantity"},
                      {"role": "assistant", "content": '''"Please provide an SQL query to find the service(s) with the highest total sales (including tax) and quantity sold from the 'sales_data' table. The table includes columns such as 'Item Name', 'Qty', and 'Sales(Inc. Tax)'. The query should return the service name, total sales amount (including tax), and total quantity sold, handling cases of ties in both sales and quantity."
    '''},

                      {"role": "system", "content": f'your task is to Craft a well-structured prompt to request a GPT model to generate an SQL query based on the provided dataset: \n{data_str}.\n The dataset is housed in a table named "sales_data," and the column names are specified as {columns}.'
                       },
                      {"role": "user", "content":
                       f" {nlp_query}"
                       }
                      ],
            temperature=0,
            max_tokens=8000
        )
        # Extracting the SQL portion from the response
        reply = query.choices[0].message.content
        nlp_query_reply = reply
        a = nlp_query_reply
        system_instruction = 'you are a helpfull assistant and helper to have great nlp to sql convertor as well as Data scientist, ML scientist'
        response = client.chat.completions.create(
            model="gpt-3.5-turbo-16k",
            messages=[{"role": "system", "content": "As an advanced text-to-SQL model, your role involves responding to inquiries about a database. Given a question and contextual information related to one or more tables, your objective is to generate and output the SQL query that effectively answers the question. \n\nYou must output the SQL query that answers the question.Try making connection with respect to other coloumn also \n"},
                      {"role": "user", "content": "Best Performing Service in Terms of Sales and Quantity'table name is xyz'"},
                      {"role": "assistant", "content": '''SELECT `Item Name`, SUM(`Qty`) as Total_Quantity
    FROM xyz
    GROUP BY `Item Name`
    ORDER BY Total_Quantity DESC
    LIMIT 5;
    '''},
                      {"role": "system", "content": f"Generate a natural language processing (NLP) to SQL query tailored for a sizable dataset, akin to the data structure represented by: \n{data_str}. \nThe database in question is characterized by the table named 'sales_data,' with column names as outlined in {columns}. Please furnish an NLP query that aligns with the nature of this extensive dataset."
                       },
                      {"role": "user", "content": '''Which centre has the the highest retention of customers? 'database is named "sales_data"'''},
                      {"role": "assistant", "content": '''WITH RetainedGuests AS (
        SELECT
            `Center Code`,
            `Guest Code`,
            COUNT(`Guest Code`) AS GuestCount
        FROM sales_data
        GROUP BY `Center Code`, `Guest Code`
        HAVING GuestCount > 2
    )

    SELECT
        `Center Code`,
        COUNT(`Guest Code`) AS RetainedGuestCount
    FROM RetainedGuests
    GROUP BY `Center Code`
    ORDER BY RetainedGuestCount DESC
    LIMIT 5;
    '''},
                      {"role": "system", "content": f"Generate a natural language processing (NLP) to SQL query tailored for a sizable dataset, akin to the data structure represented by: {data_str}. The database in question is characterized by the table named 'sales_data,' with column names as outlined in {columns}. Please furnish an NLP query that aligns with the nature of this extensive dataset."
                       },
                      {"role": "user", "content":
                       f'''Try making connection with respect to other coloumns atleast 2-3 coloumns and Generate output incorporating a minimum of 3 columns. For time-related queries, leverage the window function in SQL, and for retention analysis (where retention signifies customers returning for further purchases or continued product/service usage), ensure that counts greater than 1 are considered. The dataset is housed in a SQLite database, with the table named "sales_data" and the columns as follows: {columns}, Sample Data:{data_str} The query to be executed is: {nlp_query_reply}. Utilize the capabilities of the SQLite database system to accomplish this task.'''
                       }
                      ],
            temperature=0,
            max_tokens=1250
        )
        # Extracting the SQL portion from the response
        reply = response.choices[0].message.content

        print(f'\n\n SQL Query Generate : \n{reply}\n')

        sql_reply = reply

        def extract_sql_query(text: str) -> str:

            # Regular expression to match SQL query within the text
            sql_pattern = re.compile(
                r'(SELECT|INSERT INTO|WITH|UPDATE|DELETE FROM|CREATE TABLE|CREATE INDEX|ALTER TABLE|CREATE VIEW|CREATE PROCEDURE|CREATE FUNCTION|CREATE TRIGGER).*?;', re.DOTALL | re.IGNORECASE)

            # Search for SQL pattern in the text
            match = sql_pattern.search(text)

            # If a match is found, return the matched SQL query; otherwise, return an empty string
            return match.group() if match else ''

        # Extract SQL query from the test string
        reply = extract_sql_query(sql_reply)
        results_final = pd.read_sql_query(reply, conn)
        results_final = results_final.dropna()

        final_file_name = "final_" + file_path.split("/")[-1]
        final_file = os.path.join("output", final_file_name)
        results_final.to_csv(final_file, index=False)

        insights = client.chat.completions.create(
            model="gpt-3.5-turbo-16k",
            messages=[
                {"role": "system", "content": "As a proficient data scientist, your role involves responding to inquiries related to a database. You are presented with questions and contextual information pertaining to one or more tables. Your task is to deliver insightful analyses that contribute to a deeper understanding of the business implications derived from the provided data."},
                {"role": "user", "content":
                    """Based on the data snippet provided: '''top 5 product having highest sales
                  Product line  Total_Sales
      0  Electronic accessories          971
      1      Food and beverages          952
      2       Sports and travel          920
      3      Home and lifestyle          911
      4     Fashion accessories          902
      ''', Deliver business insights derived from the data, ensuring that the provided analysis goes beyond mere descriptions of results or visualizations. The emphasis is on offering additional and meaningful insights that contribute to a more comprehensive understanding of the business implications within the dataset."""},
                {"role": "assistant", "content": '''1) The 'Electronic accessories' category leads in total sales, indicating a strong market demand for these products. This presents an opportunity to diversify and expand the range of electronic accessories offered to cater to various consumer needs and preferences, potentially driving further sales in this category.\n

      2)With 'Food and beverages' being the second-highest in total sales, it would be strategic to intensify marketing initiatives for products under this category. Special promotions, discounts, or bundled offers can be introduced to attract more customers and stimulate purchase behavior.\n

      3)The 'Sports and travel' and 'Home and lifestyle' categories also exhibit substantial sales. Efficient inventory management for these product lines is crucial to ensure that supply meets demand, especially during peak seasons or promotional periods. This will help in avoiding stockouts or excess inventory, both of which could impact profitability.\n

      4)Since 'Fashion accessories' are among the top-selling products, engaging marketing campaigns that highlight the latest trends, styles, and fashion tips can be rolled out. This approach not only promotes the products but also enhances customer engagement, potentially leading to increased brand loyalty and customer retention.'''},
                {"role": "system", "content": "you are data analyst with experty in excel, sql, python"},
                {"role": "user", "content":
                    f"Drawing from the provided data snippet: {results_final}, offer business insights specifically centered on the effects and impacts discernible within the dataset. Generate 2-5 substantial insights grounded in the data, ensuring that the analysis surpasses a mere description of results or visualizations. The objective is to provide additional, valuable insights into the business context encapsulated by the data."}
            ],
            temperature=0,
            max_tokens=1800
        )
        insight = insights.choices[0].message.content
        insight = insight + '\n'
        return final_file, insight
    except Exception as e:
        return (f"Error: {e}")


# graph generation using plotly and PNG conversion using base64
def graph_file(file_path):
    results_final = pd.read_csv(file_path)
    data_str = results_final
    num_rows = len(results_final)
    print(f'\n\nNumber of Records :{num_rows}')
    client = OpenAI(
        api_key='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',
    )
    response = client.chat.completions.create(
        model="gpt-3.5-turbo-16k",
        messages=[
            {"role": "system", "content": '''You are a powerful python visualization code generater that answers the question.\n
               The visualizations should be easy for an executive to understand and interpret. Please choose "ANY ONE" from the following types of visualizations, making adjustments as necessary for the data along with give units/values for axis whenever needed:

              1. Bar Chart or Stacked Bar Chart: Horizontal or vertical bars, with sub-categories if applicable.
              Used bar chart for Comparison, Trends, Categorical Data, Distribution, Frequency
              2. Line Chart or Area Chart: Display data points connected by lines, possibly with the area under the lines filled.
              Used line chart for Trends, Time Series, Progress Tracking, Correlations, Fluctuations
              3. Pie Chart or Donut Chart: Represent categories of data with slices of a circle (limit to top 10 categories for Pie Chart).
              Used pie chart for Proportions, Percentages, Categorical Data, Non-continuous data:, Comparisons
              4. Scatter Plot or Bubble Chart: Display individual data points on a two-dimensional graph, with varying bubble sizes for Bubble Chart.
              Used scatter plot for Correlation, Distribution, Categorical Data, Outliers, Clustering
               '''},
            {"role": "user", "content": '''"This is the dataset:
          Day  Product_A  Product_B  Product_C  Product_D
        0    1         94         88         99        143
        1    2         97         95        102         48
        2    3         50         69        119         27
        3    4         53        117         49         89
        4    5         53         76         52        142
      give me bar chart"
        '''},
            {"role": "assistant", "content": """
  import plotly.express as px
  import pandas as pd
  import base64
               

  # Assuming 'data' is already defined and is a valid dataset
  df = pd.DataFrame(data)

  # Creating a bar chart using Plotly, may use line chart, scatter plot or pie chart as well
  fig = px.bar(df, x='Day', y='Number of Products Sold',
              title='Sales of Products Over 5 Days',
              labels={'Day': 'Day', 'Number of Products Sold': 'Number of Products Sold'},
              template='plotly')

  # Customizing the layout
  fig.update_layout(
      xaxis_title="Day",
      yaxis_title="Number of Products Sold",
      plot_bgcolor='rgba(0,0,0,0)',
      yaxis=dict(gridcolor='gray', gridwidth=0.5),
      xaxis=dict(gridcolor='gray', gridwidth=0.5)
  )

  # Convert figure to PNG byte stream and encode as base64
  img_bytes = fig.to_image(format="png")
  graph_data = base64.b64encode(img_bytes).decode("utf-8")
  # Display the encoded image data
  with open("graph/graph_data.txt", "w") as f:
      f.write(graph_data)
        """},
            {"role": "system", "content": f"As a proficient Python visualization code generator, create compelling visualizations for the given data in the file named file_path, without the need to create a dataframe. Utilize the file directly, considering it contains- \n data in the format {data_str}, \n and take into account that the file has a size of {num_rows} rows."
             },
            {"role": "user", "content": f'''Generate only the python code using the Plotly library based on the data provided in the file located at file_path. Develop code to create visualizations with appropriate titles using Plotly as the template. Additionally, convert the generated graph to PNG format, encode it using base64, and store the encoded image data in the 'graph/graph_data.txt' file. Ensure that the plotted data adheres to a maximum limit of 10 data points. Consider the following parameters:

              - Data Sample: {data_str}
              - Number of Rows: {num_rows}

  '''
             }],
        temperature=0,
        max_tokens=3500
    )

    # def extract_python_code(response_text):
    #     python_code_pattern = re.compile(r'```(?:python)?(.*?)```', re.DOTALL)

    #     matches = python_code_pattern.findall(response_text)

    #     python_code_list = [match.strip() for match in matches]

    #     if python_code_list:
    #         return python_code_list
    #     else:
    #         return None

    reply = response.choices[0].message.content
    # with open('graph/graph_code.txt', 'w') as f:
    #     f.write(reply)
    # f.close()
    # reply = extract_python_code(reply)

    try:
        exec(reply)
        return 'success'
    except Exception as e:
        return (f"Error: {e}")
