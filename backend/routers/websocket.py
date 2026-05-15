import asyncio
import json
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from config import settings
import redis.asyncio as redis
from utils.logger import logger

router = APIRouter()

@router.websocket("/progress/{job_id}")
async def websocket_endpoint(websocket: WebSocket, job_id: str):
    await websocket.accept()

    redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)
    pubsub = redis_client.pubsub()

    channel = f"job_progress_{job_id}"
    await pubsub.subscribe(channel)

    logger.info(f"WebSocket client connected for job: {job_id}")

    try:
        # Loop to read messages from Redis and push to WS
        while True:
            message = await pubsub.get_message(ignore_subscribe_messages=True, timeout=1.0)
            if message:
                data = message['data']
                await websocket.send_text(data)

                # Check if we should close the connection
                try:
                    parsed = json.loads(data)
                    if parsed.get("status") in ["completed", "failed"]:
                        # Give a little time for the client to receive the message
                        await asyncio.sleep(1)
                        break
                except json.JSONDecodeError:
                    pass

            # Ping/pong to keep connection alive if needed
            await asyncio.sleep(0.1)

    except WebSocketDisconnect:
        logger.info(f"WebSocket client disconnected for job: {job_id}")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
    finally:
        await pubsub.unsubscribe(channel)
        await redis_client.aclose()
        # Cleanly close websocket if it's not already disconnected
        try:
            await websocket.close()
        except:
            pass
