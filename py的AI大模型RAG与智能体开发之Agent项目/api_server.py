# 你的 FastAPI 代码应该这样写
from fastapi import Request, HTTPException, FastAPI
from pydantic import BaseModel
from uvicorn import run
from agent.react_agent import ReactAgent
from agent.tools import skyway_crud_tools
from agent.tools.skyway_crud_tools import get_jwt_token, set_jwt_token

app = FastAPI(title="苍穹外卖智能客服 API")


class ChatRequest(BaseModel):
    question: str


agent = None


@app.on_event("startup")
async def startup_event():
    global agent
    agent = ReactAgent()
    print("Agent 已初始化")


@app.post("/api/chat")
async def chat(request: Request):
    try:
        # 获取请求体
        data = await request.json()
        question = data.get('question', '')

        # 从请求头获取 Token
        authorization = request.headers.get('Authorization', '')
        print(f"[DEBUG] 完整 Authorization 头：{authorization}")

        # 去掉 "Bearer " 前缀
        token = ""
        if authorization.startswith('Bearer '):
            token = authorization[7:]
            print(f"[DEBUG] 提取的 Token: {token[:20]}...")
        else:
            print(f"[DEBUG] Authorization 不以 'Bearer' 开头，实际值：{authorization}")

        # 关键：把 Token 传递给工具模块
        if token:
            set_jwt_token(token)
            print(f"✓ 收到用户 Token: {token[:20]}...")
            print(f"✓ Token 已设置到全局变量")
            # 立即验证 Token 是否设置成功
            verify_token = get_jwt_token()
            print(f"[DEBUG] 设置后立即验证 - Token: {verify_token[:20] if verify_token else 'None'}...")

        else:
            print("⚠ 警告：请求未携带 Token")
            return {
                "code": 0,
                "data": "请先登录获取 Token"
            }

        # 调用智能体
        answer = ""
        print(f"[DEBUG] 开始调用 Agent...")
        for chunk in agent.execute_stream(question):
            answer += chunk
        print(f"[DEBUG] Agent 调用完成")
        return {
            "code": 1,
            "data": answer
        }

    except Exception as e:
        print(f"✗ 错误：{str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/")
async def health():
    return {"status": "running", "message": "智能客服 API 运行中"}


if __name__ == "__main__":
    run(app, host="0.0.0.0", port=5000)
