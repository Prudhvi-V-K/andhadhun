import logging
import grpc
import uvicorn
from fastapi import FastAPI, File, HTTPException, UploadFile, WebSocket

from transcribe_pb2 import AudioFile
from transcribe_pb2_grpc import AudioServiceStub

app = FastAPI()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger(__name__)

@app.post("/transcribe/")
async def transcribe(
    file: UploadFile = File(...)
):
    try:
        content = await file.read()

        with grpc.insecure_channel("localhost:50052", []) as channel:
            stub = AudioServiceStub(channel)
            reqs = []

            chunk_size = 1024
            for i in range(0, len(content), chunk_size):
                chunk = content[i:i+chunk_size]
                request = AudioFile(
                    filename=file.filename,
                    format="wav",
                    audio_data=chunk
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

@app.websocket_route("/talk")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            await websocket.send_text(f"Message text was: {data}")
    except Exception as e:
        print(f"WebSocket error: {e}")
    finally:
        await websocket.close()


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
