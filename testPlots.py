from flask import Flask, render_template, request, jsonify, send_from_directory
from werkzeug.utils import secure_filename
import pandas as pd
import os
from datetime import datetime
from pathlib import Path
from utils_makersuite import split

FILE_DIR = Path(__file__).resolve().parent
template_folder = FILE_DIR / "template"
static_folder = FILE_DIR / "static"
app = Flask(__name__, template_folder=template_folder, static_folder=static_folder)


# test file path
check_File_Path = '/Users/amoghnigam/Downloads/pathsetter/dashboard/input/processed_supermarket_sales.csv'

ALLOWED_EXTENSIONS = set(['csv'])


# set allowed file extensions
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# read graph data from binary text file
def get_graph():
    """Generate Plotly graph based on user input (e.g., data or query)"""
    file_pwd = os.getcwd()
    file_path = 'graph_data.txt'
    graph_folder = os.path.join("graph", file_path)
    graph_path = os.path.join(file_pwd, graph_folder)
    with open(graph_path) as f:
        graph_data = f.read()
    print(f'\n\ngraph_data: {len(graph_data)}\n\n')
    return graph_data


def list_html_files(directory):
    """List all HTML files in the specified directory."""
    html_files = [f for f in os.listdir(directory) if f.endswith('.html')]
    # print(html_files)  # Debug: Print the list of found HTML files
    return html_files

# landing page


@app.route("/")
def home():
    html_files = list_html_files('graphhtml')
    return render_template('plots.html', html_files=html_files)


@app.route('/uploads/<filename>')
def uploaded_file(filename):
    """Serve the uploaded HTML files."""
    return send_from_directory('graphhtml', filename)


@app.route('/ask', methods=['GET', 'POST'])
def graph_response():
    """Generate chatbot response based on user query"""
    query = request.form['query']
    print(f'\n\nrequest: {query}')
    graph_res = 'success'
    # Process user query and generate your chatbot response
    graph_res = split(query, check_File_Path)
    print(f'\nresponse: {graph_res}')
    if graph_res == 'success':
        graph = get_graph()
    else:
        graph = ''
    print(f'\n\ngraph: {len(graph)}\n\n')
    bot_insight = 'Success'
    return jsonify({"response": bot_insight, "graph": graph})


@app.route("/delete_chart", methods=["POST"])
def delete_chart():
    file_name = request.form.get("file_name")
    if not file_name:
        return jsonify({"error": "Missing file name"}), 400

    try:
        file_path = os.path.join('graphhtml', file_name)
        os.remove(file_path)
        return jsonify({"success": True})
    except FileNotFoundError:
        return jsonify({"error": "File not found"}), 404
    except Exception as e:
        print(f"Error deleting chart: {e}")
        return jsonify({"error": "An error occurred"}), 500


@app.route("/upload", methods=["POST"])
def upload_file():
    if request.method == "POST":
        file = request.files['file']
        if file and allowed_file(file.filename):
            global check_File_Path

            filename = secure_filename(file.filename)
            new_filename = f'{filename.split(".")[0]}_{str(datetime.now())}.csv'
            save_location = os.path.join('input', new_filename)
            file.save(save_location)
            check_File_Path = save_location

            return jsonify({"success": "File uploaded successfully"})
        else:
            return jsonify({"error": "Invalid file type"})
    else:
        return jsonify({"error": "Invalid request method"})


if __name__ == '__main__':
    app.run(debug=True)
