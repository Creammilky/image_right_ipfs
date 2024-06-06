import hashlib
from flask import Flask, request, render_template, jsonify, redirect, send_from_directory, make_response
from blockchain import *
import os

config = configparser.ConfigParser()
config.read('CONFIG.ini')

UPLOAD_FOLDER = config.get('Folders', 'UPLOAD_FOLDER')
TMP_FOLDER = config.get('Folders', 'TMP_FOLDER')

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['TMP_FOLDER'] = TMP_FOLDER

blockchain = Blockchain()

# 存根目录
if os.path.exists('./blockchain/chain.pkl'):
    with open('./blockchain/chain.pkl', 'rb') as input:
        blockchain.chain = pickle.load(input)

if not os.path.exists('./blockchain'):
    os.mkdir('blockchain')
if not os.path.exists('./uploads'):
    os.mkdir('uploads')
if not os.path.exists('./tmp'):
    os.mkdir('tmp')


def on_chain(filename, author=None, original_filename=None, title=None):
    kps, npy = compute_sift_features(cv2.imread(path.join(UPLOAD_FOLDER, filename)))
    save_kps(kps, npy, filename, filename)
    kps_path = path.join(TMP_FOLDER, filename + '.kps.pkl')
    npy_path = path.join(TMP_FOLDER, filename + '.npy')
    img_cid = upload_file(path.join(UPLOAD_FOLDER, filename))
    kps_cid = upload_file(kps_path)
    npy_cid = upload_file(npy_path)
    print(kps_cid)
    # 删除临时文件
    delete_tmp(kps_path)
    delete_tmp(npy_path)
    blockchain.new_transaction(title, filename, author, img_cid, kps_cid, npy_cid)


@app.route('/verify', methods=['POST'])
def verify():
    global blockchain

    print(request)
    if 'contentFile' not in request.files:
        response = {'ok': False}
        return jsonify(response), 500
    file = request.files['contentFile']

    filename = hashlib.sha256(file.read()).hexdigest()
    file.seek(0)  # reset read pointer

    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    # Create a new transaction
    print(request.form)
    title = request.form['title']
    author = request.form['author']
    original_filename = file.filename
    # 自己的上链函数
    on_chain(filename, author, original_filename, title)
    result = blockchain.mine()
    if result == None:
        print("FALSE")
        os.remove(os.path.join(app.config['UPLOAD_FOLDER'], filename))  # remove uploaded file
        response = {'unique': False, 'message': 'Similar Object Detected, Input File Rejected'}
    else:
        print("TEST")
        print(result)
        response = {'unique': True, 'block': result.__dict__}
    return jsonify(response), 200


@app.route('/chain', methods=['GET'])
def get_chain():
    chain_data = []
    for block in blockchain.chain:
        chain_data.append(block.__dict__)

    response = {'chain': chain_data}
    return jsonify(response), 200


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8000)
