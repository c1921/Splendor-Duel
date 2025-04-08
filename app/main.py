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

# 玩家枚举
class Player:
    P1 = "P1"
    P2 = "P2"

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
        # 为每个玩家创建独立的收集区域
        self.players = {
            Player.P1: {
                "name": "玩家1",
                "collection_area": []
            },
            Player.P2: {
                "name": "玩家2",
                "collection_area": []
            }
        }
        self.current_player = Player.P1  # 当前回合玩家
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
    
    def get_player_collection(self, player):
        return self.players[player]["collection_area"]
    
    def get_all_collections(self):
        return {
            "P1": self.players[Player.P1]["collection_area"],
            "P2": self.players[Player.P2]["collection_area"]
        }
    
    def get_current_player(self):
        return self.current_player
    
    def switch_player(self):
        self.current_player = Player.P2 if self.current_player == Player.P1 else Player.P1
        return self.current_player
    
    def move_gem(self, row, col):
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
                # 添加到当前玩家的收集区
                self.players[self.current_player]["collection_area"].append(cell["gem"])
                # 清除格子中的宝石
                cell["gem"] = None
                # 切换玩家
                self.switch_player()
                return True
        return False

# 初始化游戏状态
game_state = GameState()

# 路由
@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    collections = game_state.get_all_collections()
    return templates.TemplateResponse(
        "index.html", 
        {
            "request": request, 
            "grid": game_state.get_grid(),
            "player1_collection": collections["P1"],
            "player2_collection": collections["P2"],
            "current_player": game_state.get_current_player()
        }
    )

# API路由 - 获取游戏状态
@app.get("/api/game_state")
async def get_game_state():
    collections = game_state.get_all_collections()
    return {
        "grid": game_state.get_grid(),
        "player1_collection": collections["P1"],
        "player2_collection": collections["P2"],
        "current_player": game_state.get_current_player()
    }

# API路由 - 移动宝石
@app.post("/api/move")
async def move_gem(row: str = Form(...), col: str = Form(...)):
    success = game_state.move_gem(row, col)
    if not success:
        raise HTTPException(status_code=400, detail="无效的移动")
    
    collections = game_state.get_all_collections()
    return {
        "success": True,
        "grid": game_state.get_grid(),
        "player1_collection": collections["P1"],
        "player2_collection": collections["P2"],
        "current_player": game_state.get_current_player()
    }

# 重置游戏
@app.post("/api/reset")
async def reset_game():
    global game_state
    game_state = GameState()
    
    collections = game_state.get_all_collections()
    return {
        "success": True,
        "grid": game_state.get_grid(),
        "player1_collection": collections["P1"],
        "player2_collection": collections["P2"],
        "current_player": game_state.get_current_player()
    }

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)