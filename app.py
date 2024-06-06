from fastapi import FastAPI,Response,Request
from fastapi.middleware.cors import CORSMiddleware
import json
from db import Query
from cache import Cache
import asyncio
from fastapi.responses import StreamingResponse,HTMLResponse

app = FastAPI()
cache=Cache(256)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get('/')
def root():
    return {"message":"running"}

@app.post("/api/v1/login/")
async def login(req:Request):
    try:
        req_body = await req.json()
        res,status=Query.login(username=req_body.get('username'),password=req_body.get('password'))
        if not status:
            return Response(content=json.dumps(res),status_code=400)
        return Response(content=json.dumps(res),status_code=200)
    except Exception as e:
        return Response(content=json.dumps({"message":str(e)}),status_code=500)

@app.post("/api/v1/update-task/{rasp_id}")
async def updatetask(req:Request,rasp_id:str):
    try:
        req_body = await req.json()
        Query.update_raspberry_task(
            raspberry_id=rasp_id,
            auto_harvest=req_body.get('auto_harvest'),
            pump_schedule_start_time=req_body.get('pump_schedule_start_time'),
            pump_schedule_end_time=req_body.get('pump_schedule_end_time'),
            system_cooling=req_body.get('system_cooling'),
            pump_start_now=req_body.get('pump_start_now')
        )
        data=Query.get_updated_task(raspberry_id=rasp_id)
        return Response(content=json.dumps({"data":data}),status_code=200)
    except Exception as e:
        return Response(content=json.dumps({"message":str(e)}),status_code=500)

@app.get("/api/v1/get-tasks/{rasp_id}")
async def get_tasks(rasp_id:str):
    try:
        if not rasp_id:
            return Response(content=json.dumps({"message":"raspberry id is needed!"}),status_code=400)
        data=Query.get_updated_task(raspberry_id=rasp_id)
        return Response(content=json.dumps({"data":data}),status_code=200)
    except Exception as e:
        return Response(content=json.dumps({"message":str(e)}),status_code=500)



@app.get("/events/{rasp_id}")
async def events(request: Request,rasp_id:str):
    async def event_generator():
        while True:

            if await request.is_disconnected():
                cache.delete(key=rasp_id)
                break
            data=Query.get_raspall_data(rasp_id)

            yield f"""data: {json.dumps({
                "mydata":data
            })}\n\n"""

            await asyncio.sleep(5)
            
    cache.put(key=rasp_id,value=event_generator())

    return StreamingResponse(cache.get(key=rasp_id), media_type="text/event-stream")

if __name__=="__main__":
    import uvicorn
    uvicorn.run(app,host='0.0.0.0',port=8000)