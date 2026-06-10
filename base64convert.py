import base64

with open("logo.png", "rb") as image_file:
    base64_string = base64.b64encode(image_file.read()).decode('utf-8')
    print(f"data:image/png;base64,{base64_string}")