from fastapi import FastAPI, UploadFile, File, HTTPException
import cv2
import pytesseract
import numpy as np
from typing import List

pytesseract.pytesseract.tesseract_cmd = r'/usr/bin/tesseract'

app = FastAPI()

# Function for reading card number from image
def read_bank_card(image_data):
    # Decode image data to numpy array
    image = cv2.imdecode(np.frombuffer(image_data, np.uint8), cv2.IMREAD_COLOR)

    # Use Pytesseract to extract text
    text = pytesseract.image_to_string(image)
    print("Extracted text:", text[:20])

    # Find algorithm for numbers
    card_numbers = []
    for word in text.split():
        if word.isnumeric() and len(word) == 4:
            if len(card_numbers) > 0:
                card_numbers[0] = card_numbers[0]+word
            else:
                card_numbers.append(word)
            if len(card_numbers[0]) == 16:
                return card_numbers


@app.post("/process/")
async def process(file: UploadFile = File(...)) -> List[str]:
    if not file.filename.lower().endswith(('.png', '.jpg', '.jpeg')):
        raise HTTPException(status_code=400, detail="Unsupported file type. Please upload a PNG or JPEG image.")

    try:
        image_data = await file.read()
        card_numbers = read_bank_card(image_data)
        if not card_numbers:
            raise HTTPException(status_code=404, detail="No card numbers found.")
        return card_numbers
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred while processing the file: {e}")

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=8000)
