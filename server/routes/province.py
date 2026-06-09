# 省份路由 —— 返回省份列表
from flask import Blueprint, jsonify
from database.db import get_conn

province_bp = Blueprint('province', __name__)

@province_bp.route('/')
def list_provinces():
    """GET /api/provinces —— 获取省份列表"""
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT id, name, code FROM provinces ORDER BY id")
    rows = cur.fetchall()  # DictCursor 返回字典列表
    cur.close()
    conn.close()

    return jsonify({'success': True, 'data': rows})
