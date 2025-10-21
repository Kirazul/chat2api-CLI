import asyncio
import types
import warnings

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from fastapi import FastAPI, Request, Depends, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi.security import OAuth2PasswordBearer
from fastapi.templating import Jinja2Templates
from starlette.background import BackgroundTask

from chatgpt.ChatService import ChatService
from chatgpt.authorization import refresh_all_tokens
import chatgpt.globals as globals
from chatgpt.reverseProxy import chatgpt_reverse_proxy
from utils.Logger import logger
from utils.config import api_prefix, scheduled_refresh
from utils.retry import async_retry

warnings.filterwarnings("ignore")

app = FastAPI()
scheduler = AsyncIOScheduler()
templates = Jinja2Templates(directory="templates")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token", auto_error=False)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def app_start():
    if scheduled_refresh:
        scheduler.add_job(id='refresh', func=refresh_all_tokens, trigger='cron', hour=3, minute=0, day='*/4', kwargs={'force_refresh': True})
        scheduler.start()
        asyncio.get_event_loop().call_later(0, lambda: asyncio.create_task(refresh_all_tokens(force_refresh=False)))


async def to_send_conversation(request_data, req_token):
    chat_service = ChatService(req_token)
    try:
        await chat_service.set_dynamic_data(request_data)
        await chat_service.get_chat_requirements()
        return chat_service
    except HTTPException as e:
        await chat_service.close_client()
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except Exception as e:
        await chat_service.close_client()
        logger.error(f"Server error, {str(e)}")
        raise HTTPException(status_code=500, detail="Server error")


async def process(request_data, req_token):
    chat_service = await to_send_conversation(request_data, req_token)
    await chat_service.prepare_send_conversation()
    res = await chat_service.send_conversation()
    return chat_service, res


def map_apikey_to_token(api_key: str) -> str:
    """Map sk-xxx API key to ChatGPT token"""
    logger.info(f"=== API KEY MAPPING CALLED === Input: {api_key[:20] if api_key else 'None'}...")
    
    if not api_key or not api_key.startswith("sk-"):
        logger.info(f"Not an API key, passing through: {api_key[:20] if api_key else 'None'}...")
        return api_key
    
    try:
        # Load API keys mapping
        from pathlib import Path
        import os
        apikeys_file = Path("apikeys.json")
        tokens_file = Path("tokens.json")
        
        logger.info(f"Looking for API key files in: {os.getcwd()}")
        logger.info(f"apikeys.json exists: {apikeys_file.exists()}")
        logger.info(f"tokens.json exists: {tokens_file.exists()}")
        
        if not apikeys_file.exists():
            logger.warning("apikeys.json not found, returning original API key")
            return api_key
        
        with open(apikeys_file, 'r') as f:
            apikeys = json.load(f)
        
        logger.info(f"Loaded {len(apikeys)} API keys from file")
        logger.info(f"Looking for API key: {api_key[:10]}...")
        
        # Find the API key
        for name, data in apikeys.items():
            if data.get('key') == api_key:
                token_name = data.get('token_name', 'auto')
                logger.info(f"Found API key '{name}' mapped to token '{token_name}'")
                
                # Load tokens
                if tokens_file.exists():
                    with open(tokens_file, 'r') as f:
                        tokens = json.load(f)
                    
                    if token_name in tokens:
                        logger.info(f"Successfully mapped API key to ChatGPT token")
                        return tokens[token_name]
                    elif token_name == 'auto' and tokens:
                        logger.info(f"Using first available token")
                        return list(tokens.values())[0]
                else:
                    logger.warning("tokens.json not found")
        
        # API key not found, return original
        logger.warning(f"API key not found in mapping, returning original")
        return api_key
        
    except Exception as e:
        logger.error(f"API key mapping error: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return api_key


@app.post(f"/{api_prefix}/v1/chat/completions" if api_prefix else "/v1/chat/completions")
async def send_conversation(request: Request, req_token: str = Depends(oauth2_scheme)):
    try:
        request_data = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail={"error": "Invalid JSON body"})
    
    # Map API key to ChatGPT token
    req_token = map_apikey_to_token(req_token)
    
    chat_service, res = await async_retry(process, request_data, req_token)
    try:
        if isinstance(res, types.AsyncGeneratorType):
            background = BackgroundTask(chat_service.close_client)
            return StreamingResponse(res, media_type="text/event-stream", background=background)
        else:
            background = BackgroundTask(chat_service.close_client)
            return JSONResponse(res, media_type="application/json", background=background)
    except HTTPException as e:
        await chat_service.close_client()
        if e.status_code == 500:
            logger.error(f"Server error, {str(e)}")
            raise HTTPException(status_code=500, detail="Server error")
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except Exception as e:
        await chat_service.close_client()
        logger.error(f"Server error, {str(e)}")
        raise HTTPException(status_code=500, detail="Server error")


@app.get(f"/{api_prefix}/tokens" if api_prefix else "/tokens", response_class=HTMLResponse)
async def upload_html(request: Request):
    tokens_count = len(set(globals.token_list) - set(globals.error_token_list))
    return templates.TemplateResponse("tokens.html",
                                      {"request": request, "api_prefix": api_prefix, "tokens_count": tokens_count})


@app.post(f"/{api_prefix}/tokens/upload" if api_prefix else "/tokens/upload")
async def upload_post(text: str = Form(...)):
    lines = text.split("\n")
    for line in lines:
        if line.strip() and not line.startswith("#"):
            globals.token_list.append(line.strip())
            with open("data/token.txt", "a", encoding="utf-8") as f:
                f.write(line.strip() + "\n")
    logger.info(f"Token count: {len(globals.token_list)}, Error token count: {len(globals.error_token_list)}")
    tokens_count = len(set(globals.token_list) - set(globals.error_token_list))
    return {"status": "success", "tokens_count": tokens_count}


@app.post(f"/{api_prefix}/tokens/clear" if api_prefix else "/tokens/clear")
async def upload_post():
    globals.token_list.clear()
    globals.error_token_list.clear()
    with open("data/token.txt", "w", encoding="utf-8") as f:
        pass
    logger.info(f"Token count: {len(globals.token_list)}, Error token count: {len(globals.error_token_list)}")
    tokens_count = len(set(globals.token_list) - set(globals.error_token_list))
    return {"status": "success", "tokens_count": tokens_count}


@app.post(f"/{api_prefix}/tokens/error" if api_prefix else "/tokens/error")
async def error_tokens():
    error_tokens_list = list(set(globals.error_token_list))
    return {"status": "success", "error_tokens": error_tokens_list}


@app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "HEAD", "PATCH", "TRACE"])
async def reverse_proxy(request: Request, path: str):
    return await chatgpt_reverse_proxy(request, path)
