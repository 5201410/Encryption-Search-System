from flask import Flask, render_template, request, jsonify
import subprocess
import os

app = Flask(__name__, template_folder='templates', static_folder='static')

UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/intersection')
def intersection_page():
    return render_template('intersection.html')

@app.route('/union')
def union_page():
    return render_template('union.html')

@app.route('/boolean')
def boolean_page():
    return render_template('boolean.html')

@app.route('/search', methods=['POST'])
def search_intersection():
    index_file = request.form['index_file']
    inverted_file = request.form['inverted_file']
    query_file = request.files.get('query_file')

    if not query_file:
        return jsonify({'error': '未提供查询文件'}), 400

    query_path = os.path.join(UPLOAD_FOLDER, 'query.txt')
    query_file.save(query_path)

    with open(query_path, 'r', encoding='utf-8') as f:
        keywords = [line.strip() for line in f if line.strip()]

    cmd = ['python3', 'Conjunctive.py', index_file, inverted_file] + keywords

    try:
        result = subprocess.check_output(cmd, stderr=subprocess.STDOUT, text=True)
        return jsonify({'result': result})
    except subprocess.CalledProcessError as e:
        return jsonify({'result': f"查询失败: {e.output}"}), 500

@app.route('/search_union', methods=['POST'])
def search_union():
    index_file = request.form['index_file']
    inverted_file = request.form['inverted_file']
    query_file = request.files.get('query_file')

    if not query_file:
        return jsonify({'error': '未提供查询文件'}), 400

    query_path = os.path.join(UPLOAD_FOLDER, 'query.txt')
    query_file.save(query_path)

    with open(query_path, 'r', encoding='utf-8') as f:
        keywords = [line.strip() for line in f if line.strip()]

    cmd = ['python3', 'Disjunctive.py', index_file, inverted_file] + keywords

    try:
        result = subprocess.check_output(cmd, stderr=subprocess.STDOUT, text=True)
        return jsonify({'result': result})
    except subprocess.CalledProcessError as e:
        return jsonify({'result': f"查询失败: {e.output}"}), 500

@app.route('/search_boolean', methods=['POST'])
def search_boolean():
    query_file = request.files.get('query_file')
    inverted_file = request.files.get('inverted_file')

    if not query_file or not inverted_file:
        return jsonify({'error': '必须提供查询结构文件和倒排索引文件'}), 400

    query_path = os.path.join(UPLOAD_FOLDER, 'query.csv')
    inverted_path = os.path.join(UPLOAD_FOLDER, 'inverted.csv')
    query_file.save(query_path)
    inverted_file.save(inverted_path)

    try:
        result = subprocess.check_output(
            ['python3', 'Boolean.py', query_path, inverted_path],
            stderr=subprocess.STDOUT,
            text=True
        )
        return jsonify({'result': result})
    except subprocess.CalledProcessError as e:
        return jsonify({'result': f'查询失败: {e.output}'}), 500

if __name__ == '__main__':
    app.run(debug=True)

