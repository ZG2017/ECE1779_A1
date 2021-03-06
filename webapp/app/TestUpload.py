from flask import render_template, url_for, request, redirect, session
from werkzeug.utils import secure_filename
from app import webapp
from wand.image import Image
from app import ImageProcess
import os
from app import sql
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])

# show test page
@webapp.route("/test/FileUpload", methods=['GET'])
def testUpload():
    if "error" not in session:
        return render_template("testupload.html",error = None)
    else:
        return render_template("testupload.html",error = session["error"])

# check if form are fully filled and upload images
@webapp.route("/test/FileUpload", methods=['POST'])
def testUploadSubmit():
    if "userID" not in request.form or "password" not in request.form or \
       "uploadedfile" not in request.files:
        session["error"] = "upload form not compelete!"
        return redirect(url_for("testUpload"))
    myFile = request.files["uploadedfile"]
    cnx = sql.get_db()
    cursor = cnx.cursor()
    query = "SELECT * FROM user2Images WHERE userName = %s AND original = %s"
    cursor.execute(query,(request.form["userID"],os.path.join(os.path.join(webapp.config["UPLOAD_FOLDER"],request.form["userID"]),myFile.filename)))
    row = cursor.fetchone()
    if row != None:
        session["error"] = "Image with same name has already been uploaded!"
        return redirect(url_for("testUpload"))
    if myFile and ImageProcess.allowed_file(myFile.filename):
        userPath = os.path.join(webapp.config['UPLOAD_FOLDER'],request.form["userID"])
        if not os.path.exists(userPath):
            os.makedirs(userPath)
        filename = secure_filename(myFile.filename)
        path_original = os.path.join(userPath,filename)
        myFile.save(path_original)
        path_thumbnail,path_a,path_b,path_c = ImageProcess.ImageTransSave(userPath, filename)
        ImageProcess.DBImageSave(request.form["userID"],path_thumbnail,path_original,path_a,path_b,path_c)
        session["error"] = "the file has been uploaded!"
        return redirect(url_for("testUpload")) 
    else:
        session["error"] = "can not recognize the file, please reupload"
        return redirect(url_for("testUpload"))
    
