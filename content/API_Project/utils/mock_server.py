from flask import Flask, request, jsonify
import pymysql
from dotenv import load_dotenv
import os
import sys
from pathlib import Path

sys.path.insert(0,str(Path(__file__).parent.parent))
from config import common_varaints as cv


app = Flask(__name__)

load_dotenv(dotenv_path=cv.ENV_FILE)

# 数据库配置（改为你自己的）
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': os.getenv('DB_PASSWORD'),
    'database': os.getenv('DB_NAME'),
    'charset': 'utf8mb4'
}

def get_db():
    return pymysql.connect(**DB_CONFIG)

@app.route('/api/users', methods=['POST'])
def create_user():
    """创建用户并写入 MySQL（真实操作）"""
    data = request.json
    username = data.get('username')
    email = data.get('email')
    
    conn = get_db()
    try:
        with conn.cursor() as cursor:
            sql = "INSERT INTO users (username, email) VALUES (%s, %s)"
            cursor.execute(sql, (username, email))
            conn.commit()
            new_id = cursor.lastrowid
            
        return jsonify({
            'code': 201,
            'id': new_id,
            'username': username,
            'message': '创建成功'
        }), 201
    except Exception as e:
        conn.rollback()
        return jsonify({'code': 500, 'error': str(e)}), 500
    finally:
        conn.close()

@app.route('/api/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    """查询用户（供验证用）"""
    conn = get_db()
    try:
        with conn.cursor(pymysql.cursors.DictCursor) as cursor:
            cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
            user = cursor.fetchone()
            
        if user:
            return jsonify({'code': 200, 'data': user})
        return jsonify({'code': 404, 'message': '用户不存在'}), 404
    finally:
        conn.close()

if __name__ == '__main__':
    app.run(debug=True, port=5000)