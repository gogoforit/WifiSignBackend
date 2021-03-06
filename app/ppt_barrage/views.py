import os
import time
import json
from flask import jsonify
from flask import Flask
from flask import render_template
from flask import request
from flask_bootstrap import Bootstrap
from . import ppt_barrage as ppt_barrage_Blueprint
from app.models.PPTBarrage import Barrage

UPLOAD_FOLDER = './static/doc'
app = Flask(__name__)
bootstrap = Bootstrap(app)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER  # 设置文件上传的目标文件夹


@ppt_barrage_Blueprint.route('/')
def hello_world():
    return 'Hello World!'


@ppt_barrage_Blueprint.route('/index')
def index():
    abs_path = os.path.abspath(os.path.dirname(__file__))
    ppt_path = ''.join([abs_path, '/static/doc'])
    print(ppt_path)
    folds = []
    for root, dirnames, filenames in os.walk(ppt_path):
        for dirname in dirnames:
            folds.append(dirname)
    return render_template('ppt_barrage_home.html', folds=folds)


@ppt_barrage_Blueprint.route('/upload', methods=["GET", "POST"])
def upload_test():
    return render_template("upload.html")


@ppt_barrage_Blueprint.route('/show', methods=["GET", "POST"])
def show_test():
    return render_template("show.html")


@ppt_barrage_Blueprint.route("/api/upload", methods=["GET", "POST"])
def upload():
    file = request.files.get("file_data")
    msg = api_upload(app, file)
    upload_msg = json.loads(msg.data.decode("utf-8"))
    errmsg = upload_msg.get("errmsg")
    return jsonify({"msg": errmsg})


@ppt_barrage_Blueprint.route('/show_pic')
def show_pic():
    abs_path = os.path.abspath(os.path.dirname(__file__))
    ppt_path = ''.join([abs_path, '/static/doc'])
    print(ppt_path)
    folds = []
    for root, dirnames, filenames in os.walk(ppt_path):
        for dirname in dirnames:
            folds.append(dirname)
    return render_template('show_pic.html', folds=folds)


@ppt_barrage_Blueprint.route('/api/info_file', methods=['POST'])
def show_info_file():
    show_pic_info = {}
    basedir = os.path.abspath(os.path.dirname(__file__))
    basedir = basedir + '/static/doc'
    filename = request.form.get('filename')
    file_path = os.path.join(basedir, filename )
    files_info = os.walk(file_path)
    files = None
    for root, dirs, files in files_info:
        pass
    number_pic = len(files)
    opposite_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    show_pic_info['path'] = opposite_path
    show_pic_info['number'] = number_pic
    show_pic_info[filename] = number_pic
    show_pic_info['filename'] = filename
    return jsonify(show_pic_info)


def api_upload(app_boj, file):
    basedir = os.path.abspath(os.path.dirname(__file__))  # 获取当前项目的绝对路径
    file_dir = os.path.join(basedir, app_boj.config['UPLOAD_FOLDER'])  # 拼接成合法文件夹地址
    if not os.path.exists(file_dir):
        os.makedirs(file_dir)  # 文件夹不存在就创建
    fname = file.filename
    ext = fname.rsplit('.', 1)[1]  # 获取文件后缀
    file_name = fname.rsplit('.', 1)[0]
    judge_file = os.path.join(file_dir, fname)
    if os.path.exists(judge_file):
        return jsonify({"result": 1, "new_name": fname, "errmsg": "上传失败，文件名已存在！"})
    unix_time = int(time.time())
    new_filename = str(unix_time)+'.'+ext   # 修改文件名
    file.save(os.path.join(file_dir, fname))  #保存文件到upload目录
    ppt_pdf_pic(fname, file_name)
    return jsonify({"result": 0, "new_name": fname, "errmsg": "上传成功"})


# 上传的ppt转为pdf再转为picture
def ppt_pdf_pic(filename_ext,filename):
    basedir = os.path.abspath(os.path.dirname(__file__))
    basedir = basedir + '/static/doc'
    file_dir = ''.join([basedir, '/', filename_ext])
    folder_dir = ''.join([basedir, '/', str(filename)])
    os.system('mkdir ' + folder_dir)
    # ppt转pdf的命令
    ppt_pdf_command = ('echo wsx8208279|sudo -S soffice --headless --invisible --convert-to pdf ' +
                       file_dir + ' --outdir ' + basedir)
    result_command = os.popen(ppt_pdf_command)
    result_command = result_command.read()

    pdf_dir = ''.join([basedir, '/', str(filename), '.pdf'])
    # pdf转为图片的命令
    pic_command = ''.join([folder_dir, '/%d.jpg'])
    pdf_pic_command = ('convert -resize 1200x -density 150 -quality 100 ' + pdf_dir + ' ' + pic_command)

    result_command = os.popen(pdf_pic_command)
    result_command = result_command.read()


@ppt_barrage_Blueprint.route('/api/ppt_barrage', methods=['POST'])
def save_ppt_barrage():
    barrage_time = request.form.get('time')
    barrage_text = request.form.get('text')
    ppt_name = request.form.get('ppt_name')
    print(barrage_text, barrage_time)
    barrage = Barrage(barrage_time=barrage_time, barrage_text=barrage_text,
                      ppt_name=ppt_name)
    barrage.save()
    return jsonify({"status": "ok"})


@ppt_barrage_Blueprint.route('/api/ppt_barrage/db', methods=['POST'])
def ppt_barrage_db():
    ppt_name = request.form.get('ppt_name')
    barrages_obj = Barrage.objects(ppt_name=ppt_name)
    barrages = []
    barrages_info = {}
    for barrage in barrages_obj:
        dic = {}
        dic['barrage_time'] = barrage['barrage_time']
        dic['barrage_text'] = barrage['barrage_text']
        barrages.append(dic)
    barrages_info['barrages'] = barrages
    return jsonify(barrages_info)

if __name__ == '__main__':
    app.run(debug=True, port=8006)
