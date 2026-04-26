import asyncio
from routers.report import get_report

async def test():
    # Provide a dummy audit_id, we expect 404
    res = await get_report("dummy", "download")
    print(res.status_code)

asyncio.run(test())
