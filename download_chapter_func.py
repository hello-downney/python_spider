"""
main函数里true_m3u8_list = get_m3u8_url()的get_m3u8_url()要返回列表，每个元素是元组（chapter_name,m3u8_url）m3u8_url是要可以直接请求得到ts

"""
import os
import random
from get_m3u8_url_func import *
import aiohttp
import asyncio
import aiofiles
# 全局并发控制
MAX_CONCURRENT_EPISODES = 1  # 同时处理的剧集数
MAX_CONCURRENT_TS = 15 # 每个剧集同时下载的ts文件数

headers = {
    "user-agent":"Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Mobile Safari/537.36 Edg/143.0.0.0",
    "referer": "https://dxfbk.com/"
}
#给出要装资源的文件夹路径
location = " "


# 异步版本的 write_m3u8
async def async_write_m3u8(chapter_name,url):
    """异步处理m3u8文件"""
    connector = aiohttp.TCPConnector(ssl=False)
    async with aiohttp.ClientSession(headers=headers,connector=connector) as session:
        async with session.get(url, headers=headers) as response:
            content = await response.text()

    # 直接在内存中处理，避免文件操作
    ts_url_list = []
    base_url = url.split('/index.m3u8')[0]

    for line in content.split('\n'):
        line = line.strip()
        if line and not line.startswith('#') and not line.startswith('/'):
            ts_url = base_url +"/"+ line
            ts_url_list.append(ts_url)

    print(f"✅ 解析完成: {chapter_name}, 找到 {len(ts_url_list)} 个ts文件")
    return ts_url_list


# 改进的下载函数
async def download_ts(ts_url, session, chapter_name, semaphore, max_retry=5):
    """下载单个ts文件"""
    async with semaphore:  # 使用信号量控制并发
        for retry in range(max_retry):
            try:
                # 随机延迟，避免请求过于密集
                await asyncio.sleep(random.uniform(0.5, 2))

                async with session.get(ts_url, timeout=30) as response:
                    if response.status == 200:
                        content = await response.read()
                        if len(content) > 60:
                            name = ts_url.split('/')[-1]#############这个name是ts的，不要删掉了
                            filepath = fr'{location}\{chapter_name}\{name}'

                            async with aiofiles.open(filepath, 'wb') as f:
                                await f.write(content)

                            print(f"✅ 下载成功: {chapter_name}/{name}")
                            return True
                    else:
                        print(f"⚠️ HTTP {response.status} - {ts_url}")

            except asyncio.TimeoutError:
                print(f"⏰ 超时 (尝试 {retry + 1}/{max_retry}): {ts_url}")
            except aiohttp.ServerDisconnectedError:
                print(f"🔌 服务器断开 (尝试 {retry + 1}/{max_retry}): {ts_url}")
            except Exception as e:
                print(f"❌ 错误 (尝试 {retry + 1}/{max_retry}): {ts_url} - {e}")

            # 重试前等待
            if retry < max_retry - 1:
                wait_time = 2 ** retry + random.uniform(1, 3)
                await asyncio.sleep(wait_time)

        print(f"💥 最终失败: {chapter_name} - {ts_url}")
        return False


async def download_episode(ts_url_list, chapter_name):
    """下载单个剧集的所有ts文件"""
    print(f"🎬 开始下载剧集: {chapter_name}")

    # 创建目录
    os.makedirs(fr'{location}\{chapter_name}', exist_ok=True)

    # 控制ts下载并发数
    ts_semaphore = asyncio.Semaphore(MAX_CONCURRENT_TS)

    connector = aiohttp.TCPConnector(ssl=False, limit=MAX_CONCURRENT_TS)
    async with aiohttp.ClientSession(headers=headers, connector=connector) as session:
        tasks = []
        for i, ts_url in enumerate(ts_url_list):
            task = download_ts(ts_url, session, chapter_name, ts_semaphore)
            tasks.append(task)

            # 每10个任务打印进度
            if i % 10 == 0:
                print(f"📊 {chapter_name} - 已创建 {i + 1}/{len(ts_url_list)} 个下载任务")

        results = await asyncio.gather(*tasks)

        success_count = sum(1 for r in results if r)
        print(f"🎉 {chapter_name} 下载完成: {success_count}/{len(ts_url_list)}")
        return success_count


async def main(anime_url,loca):
    global location
    location = loca
    """主函数 - 控制整体流程"""
    print("🚀 开始获取m3u8列表...")
    true_m3u8_list = get_m3u8_url(anime_url,location)
    print(f"📋 找到 {len(true_m3u8_list)} 个剧集")

    # 控制剧集处理并发数
    episode_semaphore = asyncio.Semaphore(MAX_CONCURRENT_EPISODES)

    async def process_episode(chapter_name,m3u8_url):
        """处理单个剧集"""
        async with episode_semaphore:
            try:
                ts_url_list = await async_write_m3u8(chapter_name,m3u8_url)
                success_count = await download_episode(ts_url_list, chapter_name)
                return chapter_name, success_count, len(ts_url_list)
            except Exception as e:
                print(f"💥 处理剧集失败 {m3u8_url}: {e}")
                return None

    # 处理所有剧集
    tasks = [process_episode(chapter_name,m3u8_url) for chapter_name,m3u8_url in true_m3u8_list]
    results = await asyncio.gather(*tasks)

    # 打印最终统计
    print("\n" + "=" * 50)
    print("📊 下载统计:")
    for result in results:
        if result:
            chapter_name, success, total = result
            print(f"  {chapter_name}: {success}/{total}")
    print("=" * 50)

