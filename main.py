from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
from datetime import datetime, timedelta
from logs.logger import write_log  
import uuid

app = FastAPI()

url_db = {}     
stats_db = {}   


@app.middleware("http")
async def log_requests(request: Request, call_next):
    response = await call_next(request)

    log_data = {
        "method": request.method,
        "url": str(request.url),
        "client_ip": request.client.host,
        "status_code": response.status_code
    }

    write_log(log_data)  

    return response


class URLRequest(BaseModel):
    url: str
    validity_minutes: int = 60  
    shortcode: str | None = None



@app.post("/shorturls")
def create_short_url(request: URLRequest):
    shortcode = request.shortcode or str(uuid.uuid4())[:6]  
    expiry = datetime.now() + timedelta(minutes=request.validity_minutes)

    url_db[shortcode] = {"url": request.url, "expiry": expiry}
    stats_db[shortcode] = {"clicks": 0, "timestamps": []}

    write_log({"event": "create", "shortcode": shortcode, "url": request.url, "expiry": str(expiry)})
    return {"shortcode": shortcode, "expiry": expiry}


@app.get("/shorturls/{shortcode}")
def get_stats(shortcode: str):
    if shortcode not in stats_db:
        raise HTTPException(status_code=404, detail="Shortcode not found")
    return stats_db[shortcode]


@app.get("/{shortcode}")
def redirect_to_url(shortcode: str):
    if shortcode not in url_db:
        raise HTTPException(status_code=404, detail="Shortcode not found")

    entry = url_db[shortcode]
    if datetime.now() > entry["expiry"]:
        raise HTTPException(status_code=410, detail="Link expired")

    
    stats_db[shortcode]["clicks"] += 1
    stats_db[shortcode]["timestamps"].append(datetime.now().isoformat())
    write_log({"event": "click", "shortcode": shortcode, "time": datetime.now().isoformat()})

    return RedirectResponse(entry["url"])
