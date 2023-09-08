import os
import cv2
import copy
from flask import Flask, request, render_template, send_from_directory

app = Flask(__name__)

APP_ROOT = os.path.dirname(os.path.abspath(__file__))

def size_detection(image):
    image = cv2.imread(image)
    copy = image
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_OTSU + cv2.THRESH_BINARY)[1]

    cnts = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts = cnts[0] if len(cnts) == 2 else cnts[1]

    ROI_number = 0
    for c in cnts:
        x, y, w, h = cv2.boundingRect(c)
        ROI = image[y:y + h, x:x + w]
        # cv2.imwrite('static/images/ROI_{}.png'.format(ROI_number), ROI)
        cv2.rectangle(copy, (x, y), (x + w, y + h), (36, 255, 12), 2)
        cv2.putText(copy, "w={},h={}".format(w, h), (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (36, 255, 12), 2)

        # ROI_number += 1

    return thresh,copy;
    # =================== cv2 code end ========================



@app.route("/")
def index():
    return render_template("index.html")


@app.route("/upload", methods=["POST"])
def upload():
    # target = os.path.join(APP_ROOT, 'files/{}'.format(folder_name))
    target = os.path.join(APP_ROOT, 'static/images/')
    print(target)
    if not os.path.isdir(target):
        os.mkdir(target)
    files = request.files.getlist('files[]')
    for upload in request.files.getlist('files[]'):
        filename = upload.filename

        # This is to verify files are supported
        ext = os.path.splitext(filename)[1]

        destination = "/".join([target, filename])
        upload.save(destination)

        # ============== calling size detection method ================

        thresh, copy = size_detection(destination);
        cv2.imshow('thresh', thresh)
        cv2.imwrite('static/images/thresh.png', thresh)
        cv2.imshow('copy', copy)

        cv2.imwrite('static/images/copy.png', copy)
        # cv2.imwrite('static/images/copy.png')
        cv2.waitKey()
        cv2.destroyAllWindows()

    return render_template("index.html")


@app.route('/upload/<filename>')
def send_image(filename):
    return send_from_directory("images", filename)

if __name__ == "__main__":
    app.run(port=4555, debug=True)
