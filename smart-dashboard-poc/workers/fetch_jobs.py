import os
import httpx
import asyncio
import feedparser
import openai
import numpy as np
from typing import List, Dict, Any

MONSTER_API_URL = "https://api.monster.com/jobs"
MONSTER_KEY = os.getenv("MONSTER_KEY")

async def fetch_monster_jobs(skills, location):
    headers = {"Authorization": f"Bearer {MONSTER_KEY}"}
    params = {
        "q": ",".join(skills),
        "location": location,
        "limit": 10
    }
    async with httpx.AsyncClient() as client:
        resp = await client.get(MONSTER_API_URL, headers=headers, params=params, timeout=10)
        resp.raise_for_status()
        jobs = resp.json().get("jobs", [])
        results = []
        for job in jobs:
            results.append({
                "id": job.get("id"),
                "title": job.get("title"),
                "company": job.get("company", {}).get("name"),
                "location": job.get("location"),
                "description": job.get("description"),
                "source": "monster"
            })
        return results

async def fetch_indeed_jobs(skills, location):
    jobs = []
    for kw in skills:
        url = f"https://rss.indeed.com/rss?q={kw}&l={location}&radius=50"
        async with httpx.AsyncClient() as client:
            resp = await client.get(url, timeout=10)
            feed = feedparser.parse(resp.text)
            for entry in feed.entries:
                jobs.append({
                    "id": entry.get("id", entry.get("link")),
                    "title": entry.get("title"),
                    "company": entry.get("author", ""),
                    "location": location,
                    "description": entry.get("summary", ""),
                    "source": "indeed"
                })
    return jobs

async def fetch_jobs(candidate_dict: dict) -> List[Dict]:
    skills = candidate_dict.get("skills", [])[:5]
    location = candidate_dict.get("location", "")
    monster, indeed = await asyncio.gather(
        fetch_monster_jobs(skills, location),
        fetch_indeed_jobs(skills, location)
    )
    return monster + indeed

async def _embed(text: str) -> np.ndarray:
    response = await openai.AsyncOpenAI().embeddings.create(
        input=text,
        model="text-embedding-3-small"
    )
    return np.array(response.data[0].embedding)

async def rank_jobs(jobs: list[dict], candidate_text: str) -> list[dict[str, Any]]:
    # Embed candidate text
    candidate_emb = await _embed(candidate_text)
    # Embed all job descriptions
    job_descs = [job.get("description", "") for job in jobs]
    job_embs = await asyncio.gather(*[_embed(desc) for desc in job_descs])
    # Compute cosine similarity
    def cosine_sim(a, b):
        return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b) + 1e-8))
    scored = []
    for job, emb in zip(jobs, job_embs):
        score = cosine_sim(candidate_emb, emb)
        scored.append({"job": job, "score": score})
    # Sort and return top 10
    return sorted(scored, key=lambda x: x["score"], reverse=True)[:10]
