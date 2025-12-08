import json
import asyncio
import aiohttp
from pathlib import Path
import time
import re

PARALLEL_WORKERS = 8
MODEL = "qwen2.5:1.5b"
MAX_IN = 2000
MAX_OUT = 2048

class Progress:
    def __init__(self, total):
        self.total = total
        self.completed = 0
        self.start_time = time.time()

    def update(self):
        self.completed += 1
        if self.completed % 10 == 0 or self.completed == self.total:
            elapsed = time.time() - self.start_time
            if self.completed == 0: return
            avg = elapsed / self.completed
            rem = self.total - self.completed
            eta = rem * avg
            print(f"{self.completed}/{self.total}  ETA: {int(eta//60)}m {int(eta%60)}s  {avg:.2f}s/chunk")

def clean_text(text):
    text = re.sub(r'```.*?```', '', text, flags=re.DOTALL)
    text = " ".join(text.split())
    return text[:MAX_IN]

async def extract_chunk(text, session, chunk_id):
    clean_input = clean_text(text)
    if len(clean_input) < 20:
        return {"chunk_id": chunk_id, "entities": [], "relationships": [], "status": "skipped"}

    prompt = f"""
    Extract knowledge graph nodes from the text below.
    Return ONLY JSON.
    {{
      "entities":[{{"id":"Entity","type":"Concept/Resource/Example","desc":"Short"}}],
      "relationships":[{{"source":"Entity","target":"Entity","relation":"prereq_of/explains/exemplifies/related_to"}}]
    }}
    If unsure, use "Unknown".
    "{clean_input}"
    """

    try:
        async with session.post(
            "http://127.0.0.1:11434/api/generate",
            json={
                "model": MODEL,
                "prompt": prompt,
                "format": "json",
                "stream": False,
                "keep_alive": -1,
                "options": {"temperature": 0.2, "num_ctx": 2048, "num_predict": MAX_OUT}
            },
            timeout=aiohttp.ClientTimeout(total=90)
        ) as resp:

            if resp.status != 200:
                return {"chunk_id": chunk_id, "entities": [], "relationships": [], "status": "error"}

            raw = (await resp.json()).get("response", "")
            try:
                data = json.loads(raw)
                return {
                    "chunk_id": chunk_id,
                    "entities": data.get("entities", []),
                    "relationships": data.get("relationships", []),
                    "status": "success"
                }
            except:
                return {"chunk_id": chunk_id, "entities": [], "relationships": [], "status": "parse_error"}

    except:
        return {"chunk_id": chunk_id, "entities": [], "relationships": [], "status": "conn_error"}

async def worker(worker_id, queue, session, out_path, progress):
    while True:
        job = await queue.get()
        if job is None:
            queue.task_done()
            return

        idx, text = job
        result = await extract_chunk(text, session, idx)

        with open(out_path, "a") as f:
            f.write(json.dumps(result) + "\n")

        progress.update()
        queue.task_done()

async def main():
    chunks = []
    input_file = Path("data/chunks.jsonl")
    if input_file.exists():
        with open(input_file) as f:
            for line in f:
                if line.strip():
                    obj = json.loads(line)
                    text = obj.get("text") or obj.get("content") or obj.get("chunk") or ""
                    if text:
                        chunks.append(text)
    else:
        print("chunks.jsonl missing")
        return

    out_path = "data/entities_relations.jsonl"
    Path(out_path).unlink(missing_ok=True)

    queue = asyncio.Queue()
    for i, t in enumerate(chunks):
        queue.put_nowait((i, t))

    progress = Progress(len(chunks))
    connector = aiohttp.TCPConnector(limit=None)

    async with aiohttp.ClientSession(connector=connector) as session:
        try:
            await session.post("http://127.0.0.1:11434/api/generate",
                               json={"model": MODEL, "prompt": "hi"})
        except:
            print("Ollama not reachable")
            return

        tasks = [asyncio.create_task(worker(i, queue, session, out_path, progress))
                 for i in range(PARALLEL_WORKERS)]

        await queue.join()
        for _ in tasks:
            queue.put_nowait(None)
        await asyncio.gather(*tasks)

    print(f"Done in {time.time() - progress.start_time:.2f}s")

if __name__ == "__main__":
    asyncio.run(main())