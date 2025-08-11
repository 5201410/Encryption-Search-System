from flask import Flask, render_template, request, jsonify, send_from_directory
import subprocess
import os
import time
import csv

app = Flask(__name__, template_folder='templates', static_folder='static')

UPLOAD_FOLDER = 'uploads'
DEBUG_LOG_FOLDER = 'debug_logs'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
if not os.path.exists(DEBUG_LOG_FOLDER):
    os.makedirs(DEBUG_LOG_FOLDER)

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

    query_path = os.path.join(UPLOAD_FOLDER, f'query_{int(time.time())}.txt')
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


    timestamp = int(time.time())
    query_path = os.path.join(UPLOAD_FOLDER, f'query_{timestamp}.txt')
    debug_log_filename = f'debug_log_{timestamp}.txt'
    debug_log_path = os.path.join(DEBUG_LOG_FOLDER, debug_log_filename)
    

    query_file.save(query_path)


    with open(query_path, 'r', encoding='utf-8') as f:
        keywords = [line.strip() for line in f if line.strip()]


    cmd = ['python3', 'Disjunctive.py', index_file, inverted_file] + keywords

    try:

        result = subprocess.check_output(cmd, stderr=subprocess.STDOUT, text=True)
        

        with open(debug_log_path, 'w', encoding='utf-8') as log_file:
            log_file.write(result)
        
  
        return jsonify({
            'result': result,
            'debug_log': debug_log_filename
        })
    except subprocess.CalledProcessError as e:

        with open(debug_log_path, 'w', encoding='utf-8') as log_file:
            log_file.write(e.output)
        
        return jsonify({
            'result': f"查询失败: {e.output}",
            'debug_log': debug_log_filename
        }), 500

@app.route('/search_boolean', methods=['POST'])
def search_boolean():
    query_structure_file = request.files.get('query_structure_file')
    inverted_index_file = request.files.get('inverted_index_file')
    query_file = request.files.get('query_file')

    if not query_structure_file or not inverted_index_file or not query_file:
        return jsonify({'error': '必须提供查询结构文件、倒排索引文件和查询文件'}), 400


    timestamp = int(time.time())
    query_structure_path = os.path.join(UPLOAD_FOLDER, f'query_structure_{timestamp}.csv')
    inverted_index_path = os.path.join(UPLOAD_FOLDER, f'inverted_index_{timestamp}.csv')
    query_path = os.path.join(UPLOAD_FOLDER, f'query_{timestamp}.txt')
    
    query_structure_file.save(query_structure_path)
    inverted_index_file.save(inverted_index_path)
    query_file.save(query_path)


    try:
        result = subprocess.check_output(
            ['python3', 'Boolean.py', query_structure_path, inverted_index_path, query_path],
            stderr=subprocess.STDOUT,
            text=True
        )
        return jsonify({'result': result})
    except subprocess.CalledProcessError as e:
        return jsonify({'result': f'查询失败: {e.output}'}), 500

if __name__ == '__main__':
    app.run(debug=True)
