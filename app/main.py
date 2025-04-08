from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import uvicorn
from pydantic import BaseModel
from typing import List, Optional
import json

app = FastAPI(title="格子游戏")

# 挂载静态文件目录
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# 初始化模板目录
templates = Jinja2Templates(directory="app/templates")

# 游戏状态
class GameState:
    def __init__(self):
        self.grid_size = 5
        self.grid = [[{"id": i * self.grid_size + j, "token": True} for j in range(self.grid_size)] for i in range(self.grid_size)]
        self.collection_area = []

    def get_grid(self):
        return self.grid
    
    def get_collection_area(self):
        return self.collection_area
    
    def move_token(self, row, col):
        # 确保row和col是整数
        try:
            row = int(row)
            col = int(col)
        except (ValueError, TypeError):
            return False
            
        if 0 <= row < self.grid_size and 0 <= col < self.grid_size:
            cell = self.grid[row][col]
            if cell["token"]:
                # 移除令牌
                cell["token"] = False
                # 添加到收集区
                self.collection_area.append(cell["id"])
                return True
        return False

# 初始化游戏状态
game_state = GameState()

# 路由
@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse(
        "index.html", 
        {
            "request": request, 
            "grid": game_state.get_grid(),
            "collection_area": game_state.get_collection_area()
        }
    )

# API路由 - 获取格子状态
@app.get("/api/grid")
async def get_grid():
    return {
        "grid": game_state.get_grid(),
        "collection_area": game_state.get_collection_area()
    }

# API路由 - 移动令牌
@app.post("/api/move")
async def move_token(row: str = Form(...), col: str = Form(...)):
    success = game_state.move_token(row, col)
    if not success:
        raise HTTPException(status_code=400, detail="无效的移动")
    return {
        "success": True,
        "grid": game_state.get_grid(),
        "collection_area": game_state.get_collection_area()
    }

# 重置游戏
@app.post("/api/reset")
async def reset_game():
    global game_state
    game_state = GameState()
    return {
        "success": True,
        "grid": game_state.get_grid(),
        "collection_area": game_state.get_collection_area()
    }

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)