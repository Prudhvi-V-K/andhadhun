from typing import Optional, Dict
from fastapi import FastAPI, File, Form, UploadFile, WebSocket
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import json

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def ping():
    return {"ping": "pong"}


@app.post("/img/")
async def upload_image(file: UploadFile = File(...), prompt: Optional[str] = Form(...)):
    contents = await file.read()

    return {
        "filename": file.filename,
        "content_type": file.content_type,
        "file_size": len(contents),
        "message": "Image uploaded successfully",
    }


@app.websocket_route("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            try:
                message: Dict = json.loads(data)
                response_data = {"message": f"Received: {message}"}
                await websocket.send_text(json.dumps(response_data))
            except json.JSONDecodeError:
                await websocket.send_text("Invalid JSON format")
    except Exception as e:
        print(f"WebSocket error: {e}")
    finally:
        await websocket.close()


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
