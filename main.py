import uvicorn
import logging
import toml
import os
from fastapi import FastAPI

config = toml.load('config.toml')
app = FastAPI(title="NewsAPI")
logging.basicConfig(filename='logs.log', level=logging.INFO,
                    format='%(asctime)s:%(levelname)s:%(message)s')

import routes

if not os.path.exists(config['database']['media_folder']):
    os.mkdir(config['database']['media_folder'])
