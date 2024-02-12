from flask import Flask, render_template, request, jsonify, send_from_directory
from werkzeug.utils import secure_filename
import pandas as pd
import os
from datetime import datetime
from pathlib import Path
from utils import check, start, graph_file

FILE_DIR = Path(__file__).resolve().parent
template_folder = FILE_DIR / "template"
static_folder = FILE_DIR / "static"
app = Flask(__name__, template_folder=template_folder, static_folder=static_folder)

# test queries
# on which centre we should more focus to improve its sales?
# give me top sales giving serivce from Ahmadabad - Novotel for each month
# where should we focus to improve our sales
# what is the oct - dec sales for top  services for ahmedabad novotel
# month on month growth with respect to our product
# what are top sales giving services

# do time series analysis on our data


# test file path
check_File_Path = '/Users/amoghnigam/Downloads/pathsetter/dashboard/input/processed_supermarket_sales.csv'

ALLOWED_EXTENSIONS = set(['csv'])


# set allowed file extensions
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# read graph data from binary text file
def get_graph():
    """Generate Plotly graph based on user input (e.g., data or query)"""
    with open('graph/graph_data.txt') as f:
        graph_data = f.read()
    return graph_data


# processing the input csv file
def file_process(file_path):
    global check_File_Path
    check_File_Path = check(file_path)


# getting insights and graph response (success or failure)
def bot_answer(query):
    global check_File_Path
    # print(f'\n\nquery: {query}, check_File_Path: {check_File_Path}\n\n')
    query_file_csv, bot_insight = start(check_File_Path, query)
    # print(f'\n\nquery_file_csv: {query_file_csv}')
    graph_response = graph_file(query_file_csv)
    print(f'\n\ngraph_response: {graph_response}\n')
    if graph_response != 'success':
        graph_response = ''
    return graph_response, query_file_csv, bot_insight


# landing page
@app.route("/")
def home():
    return render_template("index.html")


# download csv file
@app.route('/<filename>')
def download_file(filename):
    return send_from_directory('output', filename)


# chatbot response endpoint
@app.route('/ask', methods=['GET', 'POST'])
def chat_response():
    """Generate chatbot response based on user query"""
    query = request.form['query']
    print(f'\n\nrequest: {query}')

    # Process user query and generate your chatbot response
    graph_response, file_csv, bot_insight = bot_answer(query)
    print(f'\nresponse:\n {bot_insight}')
    if graph_response == 'success':
        graph = get_graph()
    else:
        graph = ''
    # print(f'graph: {graph}')
    file_csv_name = file_csv.split('/')[-1]
    print(f'\nfile_csv_name: {file_csv_name}')
    print(f'\ncheck_File_Path: {check_File_Path}')

    # # Testing without CHATGPT API comment above code and uncomment below code
    # file_csv = '/Users/amoghnigam/Downloads/pathsetter/dashboard/output/csv_file.csv'
    # file_csv_name = file_csv.split('/')[-1]
    # print(f'\nfile_csv_name: {file_csv_name}')
    # print(f'\ncheck_File_Path: {check_File_Path}')
    # bot_insight = 'success\n'
    # graph = get_graph()
    # # Tesing code end 

    df = pd.read_csv(file_csv).head(5)
    print(f'\n {df.head()}\n')
    df_rec = df.to_dict(orient='records')
    return jsonify({"csv": file_csv_name, "response": bot_insight, "graph": graph, "records": df_rec})


# upload csv file endpoint
@app.route("/upload", methods=["POST"])
def upload_file():
    if request.method == "POST":
            file = request.files['file']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                new_filename = f'{filename.split(".")[0]}_{str(datetime.now())}.csv'
                save_location = os.path.join('input', new_filename)
                file.save(save_location)

                # file processing function call
                file_process(save_location)

                return jsonify({"success": "File uploaded successfully"})
            else:
                return jsonify({"error": "Invalid file type"})
    else:
        return jsonify({"error": "Invalid request method"})


if __name__ == '__main__':
    app.run(debug=True)