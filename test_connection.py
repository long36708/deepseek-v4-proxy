import requests
import json

# 测试 models 接口
print("测试 /v1/models 接口...")
try:
    response = requests.get(
        "http://localhost:9000/v1/models",
        headers={"Authorization": "Bearer test-key"},
        timeout=10
    )
    print(f"状态码: {response.status_code}")
    print(f"响应: {response.text[:200]}")
except Exception as e:
    print(f"错误: {e}")

print("\n" + "="*50 + "\n")

# 测试 chat completions 接口（非流式）
print("测试 /v1/chat/completions 接口...")
try:
    response = requests.post(
        "http://localhost:9000/v1/chat/completions",
        headers={
            "Content-Type": "application/json",
            "Authorization": "Bearer test-key"
        },
        json={
            "model": "deepseek-chat",
            "messages": [{"role": "user", "content": "Hello"}],
            "stream": False
        },
        timeout=30
    )
    print(f"状态码: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"响应成功!")
        print(json.dumps(data, indent=2, ensure_ascii=False)[:500])
    else:
        print(f"响应: {response.text[:500]}")
except Exception as e:
    print(f"错误: {e}")
