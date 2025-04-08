from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import uvicorn
from pydantic import BaseModel
from typing import List, Optional, Dict
import json
import random

app = FastAPI(title="Splendor-Duel")

# 挂载静态文件目录
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# 初始化模板目录
templates = Jinja2Templates(directory="app/templates")

# 宝石类型及数量定义
class GemType:
    A = "A"
    B = "B"
    C = "C"
    D = "D"
    E = "E"
    ALPHA = "α"
    BETA = "β"

# 宝石数量配置
GEM_COUNTS = {
    GemType.A: 4,
    GemType.B: 4,
    GemType.C: 4,
    GemType.D: 4,
    GemType.E: 4,
    GemType.ALPHA: 3,
    GemType.BETA: 2
}

# 宝石类
class Gem:
    def __init__(self, gem_id: int, gem_type: str):
        self.id = gem_id
        self.type = gem_type
    
    def to_dict(self):
        return {
            "id": self.id,
            "type": self.type
        }

# 游戏状态
class GameState:
    def __init__(self):
        self.grid_size = 5
        self.grid = [[{"id": i * self.grid_size + j, "has_gem": True, "gem": None} for j in range(self.grid_size)] for i in range(self.grid_size)]
        self.collection_area = []
        self.initialize_gems()
    
    def initialize_gems(self):
        # 创建所有宝石
        all_gems = []
        gem_id = 0
        
        for gem_type, count in GEM_COUNTS.items():
            for _ in range(count):
                all_gems.append(Gem(gem_id, gem_type))
                gem_id += 1
        
        # 随机打乱宝石
        random.shuffle(all_gems)
        
        # 将宝石放入格子
        gem_index = 0
        for i in range(self.grid_size):
            for j in range(self.grid_size):
                if gem_index < len(all_gems):
                    self.grid[i][j]["gem"] = all_gems[gem_index].to_dict()
                    gem_index += 1

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
            if cell["has_gem"] and cell["gem"]:
                # 标记格子为空
                cell["has_gem"] = False
                # 添加到收集区
                self.collection_area.append(cell["gem"])
                # 清除格子中的宝石
                cell["gem"] = None
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

# API路由 - 移动宝石
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
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)