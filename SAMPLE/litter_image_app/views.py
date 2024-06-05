import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from PIL import Image
from io import BytesIO
import numpy as np
import tensorflow as tf
from rembg import remove
import datetime
import os

# class definition
CLASSES = ["cardboard", "compost", "glass", "metal", "paper", "plastic", "trash"]

# Load TensorFlow Lite model
interpreter = tf.lite.Interpreter(model_path="littersort_model.tflite")
interpreter.allocate_tensors()


@csrf_exempt
@csrf_exempt
def upload(request):
    if request.method == "POST" and request.FILES.get("image"):
        image_file = request.FILES["image"]
        original_image = Image.open(image_file)

        # Resize and remove-background
        image = original_image.resize((224, 224))
        image = remove(image)

        # convert from RGBA to RGB
        if image.mode == "RGBA":
            r, g, b, a = image.split()
            image = Image.merge("RGB", (r, g, b))

        # Image Classification
        class_name, confidence = classify_image(image, interpreter)
        confidence = float(confidence)

        # Create save dir
        os.makedirs("uploads", exist_ok=True)

        now = datetime.datetime.now()
        filename = f"{class_name}_{now:%Y%m%d%H%M%S}.jpg"

        # save uploaded image
        original_image.save(f"uploads/{filename}")
        # Added filename to response
        return JsonResponse(
            {"class": class_name, "confidence": confidence, "filename": filename}
        )

    return JsonResponse({"error": "Invalid request"}, status=400)


def classify_image(img, interpreter):
    # pre processing
    img_arr = np.array(img).astype(np.float32) / 255.0
    input_details = interpreter.get_input_details()
    output_details = interpreter.get_output_details()

    interpreter.set_tensor(input_details[0]["index"], [img_arr])
    interpreter.invoke()
    output_data = interpreter.get_tensor(output_details[0]["index"])
    pred_label = np.argmax(output_data)

    return CLASSES[pred_label], output_data[0][pred_label]


@csrf_exempt
def update_img_classification(request):
    if request.method == "PUT":
        raw_data = request.body
        decoded_data = raw_data.decode("utf-8")
        json_data = json.loads(decoded_data)

        # Extract json data for updating class
        classification_data = json_data.get("class")
        if not isinstance(classification_data, dict):
            return JsonResponse(
                {"error": "Missing or invalid 'class' field."}, status=422
            )

        # Extract original and updated class
        original = classification_data.get("original")
        updated = classification_data.get("updated")

        # Validate class data, send error if not valid
        if (
            not original
            or not updated
            or original not in CLASSES
            or updated not in CLASSES
        ):
            return JsonResponse(
                {
                    "error": "Both 'original' and 'updated' fields required",
                    "valid_classifications": CLASSES,
                },
                status=422,
            )

        # Extract filename from json
        file_name_data = json_data.get("filename")

        if file_name_data == None:
            return JsonResponse({"error": "filename field required"}, status=422)

        # TODO: check if file exists and send error if it doesnt

        # If original class is equal to updated class nothing needs to be done.
        # This is just redundency, the front end doesnt even need to make a request to this endpoint if that is the case.
        if original == updated:
            return JsonResponse(
                {
                    "status": "success",
                    "message": "Image filename does not need to be updated ",
                }
            )

        # TODO: Update filename if original classification changed

        return JsonResponse(
            {"status": "success", "message": "Image classification updated."}
        )
    # Catch-all for non-POST requests or other unhandled cases
    else:
        return JsonResponse({"error": "Unsupported request method."}, status=405)
