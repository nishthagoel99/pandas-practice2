import os
import pandas as pd
from werkzeug.utils import secure_filename
from flask import Flask, flash, request, redirect, send_file, render_template

UPLOAD_FOLDER = 'uploads/'
app = Flask(__name__, template_folder='templates')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['UPLOAD_EXTENSION'] = [".xlsx"]


# Upload API
@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            print('no file')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            print('no filename')
            return redirect(request.url)
        else:
            filename = secure_filename(file.filename)
            file_ext = os.path.splitext(filename)[1]
            if file_ext not in app.config['UPLOAD_EXTENSION']:
                print('invalid file type')
                return redirect(request.url)
            app.config['filename'] = filename
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            print("saved file successfully")
            return redirect('/downloadfile/' + filename)
    return render_template('upload.html')


@app.route("/task/1")
def task1():
    filename = app.config['filename']
    dataset = pd.read_excel(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    pc = dataset[dataset['Accepted Compound ID'].str.contains("PC", na=False)]
    lpc = dataset[dataset['Accepted Compound ID'].str.contains("LPC", na=False)]
    plasmalogen = dataset[dataset['Accepted Compound ID'].str.contains("plasmalogen", na=False)]

    df = pd.DataFrame(pc)
    df.to_excel(os.path.join(app.config['UPLOAD_FOLDER'], "task1PC.xlsx"), index=False, header=True)

    df = pd.DataFrame(lpc)
    df.to_excel(os.path.join(app.config['UPLOAD_FOLDER'], "task1LPC.xlsx"), index=False, header=True)

    df = pd.DataFrame(plasmalogen)
    df.to_excel(os.path.join(app.config['UPLOAD_FOLDER'], "task1plasmalogen.xlsx"), index=False, header=True)
    return redirect('/downloadfile/' + filename)


@app.route("/task/2")
def task2():
    filename = app.config['filename']
    dataset = pd.read_excel(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    y_pred = dataset['Retention time (min)'].round()
    dataset['Retention Time Roundoff (in mins)'] = y_pred
    df = pd.DataFrame(dataset)
    df.to_excel(os.path.join(app.config['UPLOAD_FOLDER'], "task2.xlsx"), index=False, header=True)
    return redirect('/downloadfile/' + filename)


@app.route("/task/3")
def task3():
    filename = app.config['filename']
    dataset = pd.read_excel(os.path.join(app.config['UPLOAD_FOLDER'], "task2.xlsx"))
    df = pd.DataFrame(dataset)
    df.drop(df.columns[[0, 1, 2]], axis = 1, inplace = True) 
    grouped=pd.DataFrame(df.groupby('Retention Time Roundoff (in mins)'))
    print(grouped)
    final = pd.DataFrame(grouped[1][0].T).mean(axis=1)
    final = pd.DataFrame(final)
    for i in range(1,12):
    	x = pd.DataFrame(grouped[1][i].T).mean(axis=1)
    	final = pd.concat([final,x],axis=1)
    ThirdTask = pd.DataFrame(final.T)
    ThirdTask.to_excel(os.path.join(app.config['UPLOAD_FOLDER'], "task3.xlsx"), index = False, header=True)
    return redirect('/downloadfile/'+filename)



# Download API
@app.route("/downloadfile/<filename>", methods=['GET'])
def download_file(filename):
    return render_template('download.html', value=filename)


@app.route('/return-files/<filename>')
def return_files_tut(filename):
    file_path = UPLOAD_FOLDER + filename
    return send_file(file_path, as_attachment=True, attachment_filename='')


if __name__ == "__main__":
    app.run()
