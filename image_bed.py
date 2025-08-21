"""
图床服务

import requests

IMAGE_UPLOAD_URL = 'http://127.0.0.1/upload/'

with open('test.jpg', 'rb') as f:
    file = {'file': f}
    response = requests.post(IMAGE_UPLOAD_URL, files=file)
    print(response.json())  # {'url': 'http://127.0.0.1/images/test.jpg'}

with open('test.jpg', 'rb') as f:
    content = f.read()
    file = {'file': ('abcdef.jpg', content)}
    response = requests.post(IMAGE_UPLOAD_URL, files=file)
    print(response.json())  # {'url': 'http://127.0.0.1/images/abcdef.jpg'}
"""

from pathlib import Path
import aiofiles
from fastapi import FastAPI, File, UploadFile
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

# 供外部访问的图片服务地址、端口和路由, 如果是 Fastapi 则同服务端口一致, 如果是 Nginx 则根据 Nginx 的配置规则来写
SERVER_URL_PREFIX = 'http://127.0.0.1:10000'  
IMAGE_SERVER_ROUTE = '/images/'

# IMAGE_SAVE_DIR: Path = Path('/var/www/images')  # Nginx 图片存储目录
IMAGE_SAVE_DIR: Path = Path(__file__).parent.resolve() / 'images'  # Fastapi 图片存储目录
IMAGE_SAVE_DIR.mkdir(parents=True, exist_ok=True)  # 确保目录存在

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],  # 允许所有来源
    allow_credentials=True,
    allow_methods=['*'],  # 允许所有方法
    allow_headers=['*'],  # 允许所有头
)

# 如果不用 Nginx 映射图片目录, 可以直接使用 FastAPI 的静态文件服务
app.mount(IMAGE_SERVER_ROUTE, StaticFiles(directory=str(IMAGE_SAVE_DIR)), name='images')

@app.post('/upload/') 
async def upload_image(file: UploadFile = File(...)):
    try:
        async with aiofiles.open(IMAGE_SAVE_DIR / file.filename, 'wb') as out_file:
            content = await file.read()
            await out_file.write(content)
        return {'status': 'success', 'url': f'{SERVER_URL_PREFIX}{IMAGE_SERVER_ROUTE}{file.filename}'}
    except Exception as e:
        return {'status': 'error', 'msg': str(e)}

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=10000)