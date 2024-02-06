from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from PIL import Image
from io import BytesIO
import numpy as np
import tensorflow as tf
from rembg import remove

# クラスの定義
CLASSES = ['cardboard','compost', 'glass', 'metal', 'paper',  'plastic', 'trash']

# TensorFlow Liteモデルの読み込み
interpreter = tf.lite.Interpreter(model_path="littersort_model.tflite")
interpreter.allocate_tensors()

@csrf_exempt
@csrf_exempt
def upload(request):
    if request.method == 'POST' and request.FILES.get('image'):
        image_file = request.FILES['image']
        image = Image.open(image_file)

        # リサイズと背景除去
        image = image.resize((224, 224))
        image = remove(image)

        # RGBAからRGBへの変換
        if image.mode == 'RGBA':
            r, g, b, a = image.split()
            image = Image.merge("RGB", (r, g, b))

        # 画像分類
        class_name, confidence = classify_image(image, interpreter)
        confidence = float(confidence)
        
        return JsonResponse({'class': class_name, 'confidence': confidence})

    return JsonResponse({'error': 'Invalid request'}, status=400)

def classify_image(img, interpreter):
    # 画像の前処理
    img_arr = np.array(img).astype(np.float32) / 255.0
    input_details = interpreter.get_input_details()
    output_details = interpreter.get_output_details()
    
    interpreter.set_tensor(input_details[0]['index'], [img_arr])
    interpreter.invoke()
    output_data = interpreter.get_tensor(output_details[0]['index'])
    pred_label = np.argmax(output_data)
    
    return CLASSES[pred_label], output_data[0][pred_label]
