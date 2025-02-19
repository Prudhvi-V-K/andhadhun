import logging

from fastapi.responses import FileResponse
import grpc
import pyttsx3
import uvicorn
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
import numpy as np
from google import genai
from google.genai import types
from transcribe_pb2 import AudioFile
from transcribe_pb2_grpc import AudioServiceStub

# DANGER: DONOT FUCKING COMMIT THIS!!
client = genai.Client(api_key="AIzaSyBAwAwPzjetIm_q9vvEh_rXpfQbMnLxzVk")

system_instruction = (
    'You are an assistant to a blind person. Your task is to provide accurate and relevant descriptions of what is happening in an image given to you. Omit irrelevant descriptions that a blind person would not understand, such as color. Also assume that the person knows the context of what is happening, such as being indoors.\n\n*Instructions:*\n\n1.  *Object Detection:* Identify all prominent objects present in the image.  Focus on concrete, recognizable objects.  Avoid abstract interpretations.\n2.  *Object Listing:* Create a list of the identified objects.  Use concise, single-word labels for each object (e.g., "dog", "car", "building", "tree", "person").\n3.  *Object Description:* Provide a short, descriptive sentence for each object identified in the "objects" list.  Include relevant details such as:\n    *   Appearance (color, size, shape)\n    *   Any immediately apparent attributes (e.g., "running", "parked", "smiling").\n    *   Contextual information that is directly observable from the image and helps differentiate the object.\n4.  *General Description:* Offer a brief (1-2 sentence) overview of the overall scene depicted in the image. This description should capture the general atmosphere, setting, and any apparent relationships between the objects.\n5.  *JSON Formatting:*  Your output MUST be a valid JSON object conforming to the following schema:\n\n\n{\n    "objects": ["object1", "object2", ...],\n    "obj_description": {\n        "object1": "Description of object1.",\n        "object2": "Description of object2.",\n        ...\n    },\n    "general_description": "A brief description of the overall scene."\n}',
)

engine = pyttsx3.init()
engine.setProperty("rate", 125)
engine.setProperty("volume", 1.0)
voices = engine.getProperty("voices")
engine.setProperty("voice", voices[1].id)
app = FastAPI()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger(__name__)

contexts = {}


@app.post("/transcribe")
async def transcribe(file: UploadFile = File(...)):
    try:
        content = await file.read()
        with grpc.insecure_channel("localhost:50052", []) as channel:
            stub = AudioServiceStub(channel)
            reqs = []

            chunk_size = 1024
            for i in range(0, len(content), chunk_size):
                chunk = content[i : i + chunk_size]
                request = AudioFile(
                    filename=file.filename, format="m4a", audio_data=chunk
                )
                reqs.append(request)

            response = stub.TranscribeAudio(iter(reqs))

            return {"message": response.message}

    except grpc.RpcError as e:
        logger.error(f"RPC failed: {e.code()}: {e.details()}")
        raise HTTPException(status_code=500, detail="Failed to transcribe audio")
    except Exception as e:
        logger.error(f"Error processing file: {str(e)}")
        raise HTTPException(status_code=400, detail="Error processing file")


@app.post("/img")
async def img(
    prompt: str = Form(...),
    image: UploadFile = File(...),
):
    try:
        content = await image.read()

        file = types.Part.from_bytes(data=content, mime_type="image/jpeg")

        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=[prompt, file],
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
                temperature=1,
                response_mime_type="application/json",
            ),
        )

        res = response.candidates[0].content.parts[0].text

        return {"message": res}

    except Exception as e:
        return {"message": str(e)}


@app.post("/tts")
def tts(
    text: str = Form(...),
):
    random_number = np.random.randint(10000, 99999)
    tmp_path = f"{random_number}.wav"
    engine.save_to_file(text, tmp_path)
    engine.runAndWait()

    return FileResponse(tmp_path, media_type="audio/wav", filename="output.wav")


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
