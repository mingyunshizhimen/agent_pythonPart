from langchain.tools import tool
import requests
import json
import threading

# agent/tools/skyway_crud_tools.py
from langchain.tools import tool
import requests
import json

# 全局变量
BASE_URL = "http://127.0.0.1:8080"

#使用全局变量存储Token
_current_token=None
_token_lock = threading.Lock()


def set_jwt_token(token: str):
    """
    设置当前请求的 Token（在线程内有效）

    Args:
        token: JWT Token 字符串
    """
    global _current_token
    with _token_lock:
        _current_token = token
        print(f"[DEBUG] set_jwt_token 已设置 Token: {token[:20] if token else 'None'}...")


def get_jwt_token():
    """
    获取当前请求的 Token

    Returns:
        Token 字符串，没有返回 None
    """
    print(f"[DEBUG] get_jwt_token 获取到 Token: {_current_token[:20] if _current_token else 'None'}...")
    return _current_token


def create_session_with_token():
    """
    创建带有 Token 的 Session

    Returns:
        带有 Authorization 头的 Session 对象
    """
    session = requests.Session()
    token = get_jwt_token()
    print(f"[DEBUG] Token 是否存在：{token is not None}")
    print(f"[DEBUG] Token 前 20 位：{token[:20] if token else 'None'}...")

    if token:
        session.headers.update({
            "token": token
        })
        print(f"✓ 请求已携带 Token: {token[:20]}...")
        print(f"[DEBUG] Session Headers: {dict(session.headers)}")
    else:
        print("⚠ 警告：当前请求未携带 Token")
        print(f"[DEBUG] _current_token 的值：{_current_token}")

    return session


# ... existing code ...

@tool(description="查询菜品分类列表，可以指定分类类型（1-菜品分类，2-套餐分类）")
def query_category_list(category_type: int = 1) -> str:
    """
    查询分类列表

    Args:
        category_type: 分类类型 (1-菜品分类，2-套餐分类)

    Returns:
        分类列表的 JSON 字符串
    """
    try:
        session = create_session_with_token()

        response = session.get(
            f"{BASE_URL}/admin/category/list",
            params={"type": category_type},
            timeout=10
        )
        response.raise_for_status()
        result = response.json()

        if result.get('code') == 1:
            categories = result.get('data', [])
            if not categories:
                return "暂无分类数据"

            output = f"共查询到 {len(categories)} 个分类:\n"
            for cat in categories:
                output += f"\n分类 ID: {cat.get('id')}\n"
                output += f"分类名称：{cat.get('name')}\n"
                output += f"类型：{'菜品' if cat.get('type') == 1 else '套餐'}\n"
                output += f"排序：{cat.get('sort')}\n"
                output += f"状态：{'启用' if cat.get('status') == 1 else '禁用'}\n"

            return output
        else:
            return f"查询失败：{result.get('msg', '未知错误')}"
    except Exception as e:
        return f"查询异常：{str(e)}"


@tool(description="查询菜品列表，需要提供分类 ID，返回该分类下的所有菜品")
def query_dish_list(category_id: int) -> str:
    """
    查询菜品列表

    Args:
        category_id: 菜品分类 ID

    Returns:
        菜品列表的 JSON 字符串
    """
    try:
        session = create_session_with_token()

        response = session.get(
            f"{BASE_URL}/admin/dish/list",
            params={"categoryId": category_id},
            timeout=10
        )
        response.raise_for_status()
        result = response.json()

        if result.get('code') == 1:
            dishes = result.get('data', [])
            if not dishes:
                return f"分类 {category_id} 下暂无菜品"

            output = f"分类 {category_id} 共有 {len(dishes)} 个菜品:\n"
            for dish in dishes:
                output += f"\n菜品 ID: {dish.get('id')}\n"
                output += f"菜品名称：{dish.get('name')}\n"
                output += f"价格：¥{dish.get('price', 0)}\n"
                output += f"分类 ID: {dish.get('categoryId')}\n"
                output += f"图片：{dish.get('image', 'N/A')}\n"
                output += f"简介：{dish.get('description', 'N/A')}\n"
                output += f"状态：{'在售' if dish.get('status') == 1 else '停售'}\n"

            return output
        else:
            return f"查询失败：{result.get('msg', '未知错误')}"
    except Exception as e:
        return f"查询异常：{str(e)}"


# 导出工具列表供智能体使用
tools = [
    query_category_list,
    query_dish_list,
]

