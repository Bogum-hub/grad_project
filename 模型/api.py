import os
from flask import  Flask, request, jsonify
from torch_utili import transform_image, get_prediction

app = Flask(__name__)
UPLOAD_FOLDER = "C:/Users/USER/Desktop/FLASK/static"

@app.route("/", methods=["GET", 'POST'])
def upload_pred():
    
    if request.method == "POST":
        file = request.files.get('file')
        img_bytes = file.read()
        tensor = transform_image(img_bytes)
        prediction = get_prediction(tensor)
        data = prediction.item()
        return jsonify(data)
        # image_file = request.files["file"]
        # if file:
        #     image_location = os.path.join(
        #         UPLOAD_FOLDER,
        #         file.filename
        #     )
        #     file.save(image_location)
        
        #     with open(image_location, "rb") as f:
        #         img_bytes = f.read()
        #     f.close()
        #     tensor = transform_image(img_bytes)
        #     prediction = get_prediction(tensor)
        #     data = prediction.item()
        #     return jsonify(s)
    else:
        return jsonify("error")


if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)