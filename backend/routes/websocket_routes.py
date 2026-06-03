import asyncio

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from asr.streaming import TranscriptionWorker

router = APIRouter()


@router.websocket("/ws/audio")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    print("WebSocket client connected")

    worker = TranscriptionWorker(websocket.app.state.transcriber)
    worker.start()
    receiver_task = asyncio.create_task(_receive_audio(websocket, worker))
    sender_task = asyncio.create_task(_send_results(websocket, worker))

    try:
        done, pending = await asyncio.wait(
            {receiver_task, sender_task},
            return_when=asyncio.FIRST_COMPLETED,
        )

        for task in pending:
            task.cancel()
        await asyncio.gather(*pending, return_exceptions=True)
        await asyncio.gather(*done, return_exceptions=True)

    except WebSocketDisconnect:
        print("WebSocket client disconnected")

    except Exception as exc:
        print("WebSocket error:", exc)

    finally:
        await worker.stop()
        for task in (receiver_task, sender_task):
            if not task.done():
                task.cancel()
        try:
            await websocket.close()
        except RuntimeError:
            pass
        print("Connection closed")


async def _receive_audio(websocket: WebSocket, worker: TranscriptionWorker) -> None:
    while True:
        message = await websocket.receive()

        if message["type"] == "websocket.disconnect":
            break

        data = message.get("bytes")
        if data is not None:
            worker.enqueue_audio(data)


async def _send_results(websocket: WebSocket, worker: TranscriptionWorker) -> None:
    while True:
        message = await worker.result_queue.get()
        try:
            if message is None:
                return
            await websocket.send_json(message)
        finally:
            worker.result_queue.task_done()
