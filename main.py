from quart import Quart
from hypercorn.asyncio import serve
from hypercorn.config import Config
from cmyui.logging import log, Ansi
from cmyui import Version
from fatFuckSQL import fatFawkSQL

from objects import glob

import asyncio
import os

app = Quart(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.secret_key = os.urandom(24)

config = Config()
config.bind = [f'unix:{glob.config.socket}']
config.loglevel = 'error'
config.use_reloader = True

glob.version = Version(0, 0, 1)

@app.before_serving
async def connect() -> None:
    log(f'==== AsahiPanel v{glob.version} starting ====', Ansi.GREEN)

    try:
        glob.db = await fatFawkSQL.connect(**glob.config.sql)
        log('==== AsahiPanel connected to SQL ====', Ansi.GREEN)
    except Exception as e:
        log(f'==== AsahiPanel failed to connect to SQL ====\n{e}', Ansi.LRED)

    log(f'==== AsahiPanel v{glob.version} started ====', Ansi.GREEN)

@app.after_serving
async def disconnect() -> None:
    log(f'==== AsahiPanel v{glob.version} stopping ====', Ansi.GREEN)

    if glob.db:
        await glob.db.close()

    log(f'==== AsahiPanel v{glob.version} stopped ====', Ansi.GREEN)

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(serve(app, config))