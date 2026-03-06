import httpx
import asyncio

BASE_URL = "http://localhost:8000"

async def test_health():
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        print("✅ Health check passed")

async def test_chat():
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BASE_URL}/chat",
            json={"messages": [{"role": "user", "content": "Привет!"}]}
        )
        assert response.status_code == 200
        data = response.json()
        assert "response" in data
        print(f"✅ Chat response: {data['response'][:50]}...")

async def test_stream():
    async with httpx.AsyncClient() as client:
        async with client.stream(
            "POST",
            f"{BASE_URL}/chat/stream",
            json={"messages": [{"role": "user", "content": "Привет!"}]}
        ) as response:
            assert response.status_code == 200
            chunks = 0
            async for line in response.aiter_lines():
                if line.startswith("data: "):
                    chunks += 1
            print(f"✅ Stream completed: {chunks} chunks")

if __name__ == "__main__":
    asyncio.run(test_health())
    asyncio.run(test_chat())
    asyncio.run(test_stream())
    print("\n🎉 Все тесты пройдены!")