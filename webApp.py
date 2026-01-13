from fastapi import FastAPI, File, Form, Request, UploadFile
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from PIL import Image
from fastapi.concurrency import run_in_threadpool
import uvicorn
import numpy as np
import io
import os
import uuid
import cv2 

import collageGeneratorOPTOMIZED as collage

# Create FastAPI app
app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

PORT = 3000
HOST = "localhost"

LUT = np.load("lut.npy")
cachedImages = collage.cacheInputImages("images")

# Point FastAPI to your templates directory
templates = Jinja2Templates(directory="templates")

# Define a simple route
@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/", response_class=HTMLResponse)
async def upload_image(request: Request, file: UploadFile = File(...), resolution: int = Form(...)):

    contents = await file.read()

    image = Image.open(io.BytesIO(contents)).convert("RGB")
    image = np.array(image)
    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

    filename = f"{uuid.uuid4().hex}.png"
    save_path = os.path.join("static", "processed", filename)
    cv2.imwrite(save_path, image)


    result_path = await run_in_threadpool(collage.createCollageForWebServer, image, resolution, LUT, cachedImages)

    imgWidth = image.shape[0]
    imgHeight = image.shape[1]

    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "uploaded_image": f"{save_path}",
            "processed_image": result_path,
            "done_loading": True,
            "image_width": imgWidth,
            "image_height": imgHeight,
        },
    )
    

uvicorn.run(app, host=HOST, port=PORT)