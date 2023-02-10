from flask import Flask, render_template, url_for
from flask_wtf import FlaskForm, RecaptchaField
from wtforms import FileField, SubmitField, StringField
from wtforms.validators import data_required
from werkzeug.utils import secure_filename
import os, filetype, yadisk, time
from private.config import token as TOKEN
from private.config import sec_flask_key as SEC_FLASK_KEY
from private.config import pub_captcha_key as PUB_CAP
from private.config import sec_captcha_key as SEC_CAP

app = Flask(__name__)
app.config['SECRET_KEY'] = SEC_FLASK_KEY
app.config['UPLOAD_FOLDER'] = 'static/files'
app.config['RECAPTCHA_PUBLIC_KEY'] = PUB_CAP
app.config['RECAPTCHA_PRIVATE_KEY'] = SEC_CAP

allowed_extensions = ['mp3', 'wav', 'mp4', 'mov', 'pptx', 'docx', 'jpg', 'png', 'heic']

class UploadFileForm(FlaskForm):
    surname = StringField("Фамилия")
    file = FileField("Выбрать файл", validators=[data_required()])
    recaptcha = RecaptchaField()
    submit = SubmitField("Отправить файл")

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in allowed_extensions

@app.route('/', methods=['GET','POST'])
@app.route('/home', methods=['GET', 'POST'])
def home():
    args=""
    form = UploadFileForm()
    if form.validate_on_submit():
        file = form.file.data
        fsurname = form.surname.data
        if filetype.guess(file).extension != '' and filetype.guess(file).extension in allowed_extensions:
            y = yadisk.YaDisk(token=TOKEN)
            filelist=list(y.listdir('app:/'))
            sflist = [sub['name'] for sub in filelist]
            if len(str(fsurname))!=0:
                if len([ sub for sub in filelist if sub['name']==str(fsurname) and sub['type']=='dir']) > 0:
                    if str(file.filename) in [sub ['name'] for sub in list(y.listdir('app:/'+str(fsurname)))]:
                        y.upload(file, 'app:/'+str(fsurname)+'/'+str(file.filename[:-4])+' '+str(int(time.time()))+str(file.filename[-4:]))
                        args='Такое уже есть в твоей папке, но мы сохранили снова, не благодари ;)'
                    else:
                        y.upload(file, 'app:/'+str(fsurname)+'/'+str(file.filename))
                        args='Сохранили в твою папку ;)'
                else:
                    y.mkdir('app:/'+str(fsurname))
                    y.upload(file, 'app:/'+str(fsurname)+'/'+str(file.filename))
                    args="Создали твою папку и сохранили твой файл. Было сложно, но мы справились"
            else:
                if str(file.filename) in sflist:
                    y.upload(file, 'app:/'+str(file.filename[:-4])+' '+str(int(time.time()))+str(file.filename[-4:]))
                    args='У нас такое уже есть, но мы сохранили снова, не благодари ;)'
                else:
                    y.upload(file, 'app:/'+str(file.filename))
                    args="Всё сохранили, но в общую папку"
        else:
            args="Ничего не вышло, возможно ты загрузил(а) файл не того формата."
    return render_template('index.html', form=form, args=args)

if __name__ == "__main__":
   app.run(host="0.0.0.0", debug = True)
