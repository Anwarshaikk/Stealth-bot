import os
from typing import List, Optional
import redis
import requests
from bs4 import BeautifulSoup
from fastapi import APIRouter, HTTPException, Depends
from ..models import Job, Candidate
from ..deps import get_redis
import json
import logging
from datetime import datetime, timedelta
import openai
import numpy as np
import asyncio

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def _embed(text: str) -> np.ndarray:
    """Create embeddings for text using OpenAI"""
    response = await openai.AsyncOpenAI().embeddings.create(
        input=text,
        model="text-embedding-3-small"
    )
    return np.array(response.data[0].embedding)

def cosine_sim(a: np.ndarray, b: np.ndarray) -> float:
    """Compute cosine similarity between two vectors"""
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b) + 1e-8))

async def rank_jobs(jobs: List[Job], candidate_skills: List[str]) -> List[Job]:
    """Rank jobs based on candidate skills using embeddings"""
    if not jobs or not candidate_skills:
        return jobs
    
    try:
        # Create candidate text from skills
        candidate_text = " ".join(candidate_skills)
        
        # Embed candidate text
        candidate_emb = await _embed(candidate_text)
        
        # Embed all job descriptions
        job_descs = [job.description or "" for job in jobs]
        job_embs = await asyncio.gather(*[_embed(desc) for desc in job_descs])
        
        # Compute scores and update jobs
        scored_jobs = []
        for job, emb in zip(jobs, job_embs):
            score = cosine_sim(candidate_emb, emb)
            # Convert score to percentage (0-100)
            score_percentage = max(0, min(100, score * 100))
            job.score = round(score_percentage, 1)
            scored_jobs.append(job)
        
        # Sort by score (highest first) and return top 10
        ranked_jobs = sorted(scored_jobs, key=lambda x: x.score or 0, reverse=True)[:10]
        
        logger.info(f"Ranked {len(jobs)} jobs, returning top {len(ranked_jobs)}")
        return ranked_jobs
        
    except Exception as e:
        logger.error(f"Error ranking jobs: {str(e)}")
        # Return original jobs if ranking fails
        return jobs

router = APIRouter()

def generate_cache_key(skills: List[str], location: str) -> str:
    """
    Generate a Redis cache key based on search parameters
    """
    # Use top 3 skills and location to create a unique key
    skills_str = "-".join(sorted(skills[:3])).lower()
    location_str = location.lower().replace(" ", "-")
    return f"job_search:{skills_str}:{location_str}"

def scrape_indeed_jobs(skills: List[str], location: str = "Remote") -> List[Job]:
    """
    Scrape job listings from Indeed based on candidate skills
    """
    # Convert skills list to search query
    search_query = " ".join(skills[:3])  # Use top 3 skills
    
    # Format URL (Note: This is a simplified example)
    base_url = "https://www.indeed.com/jobs"
    params = {
        "q": search_query,
        "l": location,
        "sort": "date"
    }
    
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        
        # Make request with timeout
        response = requests.get(base_url, params=params, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        jobs_list = []
        
        # Find job cards
        job_cards = soup.find_all('div', class_='job_seen_beacon')
        
        if not job_cards:
            logger.warning('Scraper could not find any job listings. The website structure may have changed.')
            return []
        
        for card in job_cards[:10]:  # Limit to 10 results
            try:
                title = card.find('h2', class_='jobTitle').get_text(strip=True)
                company = card.find('span', class_='companyName').get_text(strip=True)
                location = card.find('div', class_='companyLocation').get_text(strip=True)
                description = card.find('div', class_='job-snippet').get_text(strip=True)
                url = "https://www.indeed.com" + card.find('a')['href']
                
                job = Job(
                    title=title,
                    company=company,
                    location=location,
                    url=url,
                    description=description
                )
                jobs_list.append(job)
            except Exception as e:
                logger.error(f"Error parsing job card: {str(e)}")
                continue
                
        return jobs_list
    except requests.Timeout:
        logger.error("Request timed out while scraping jobs")
        return []
    except requests.RequestException as e:
        logger.error(f"Network error while scraping jobs: {str(e)}")
        return []
    except Exception as e:
        logger.error(f"Unexpected error while scraping jobs: {str(e)}")
        return []

@router.get("/{candidate_id}", response_model=List[Job])
async def get_jobs_for_candidate(candidate_id: str):
    """
    Get job listings relevant to a candidate based on their skills
    """
    # Get Redis connection
    redis_client = get_redis()
    
    try:
        # Try to get candidate data from Redis
        candidate_key = f"candidate:{candidate_id}"
        candidate_data = redis_client.get(candidate_key)
        
        if not candidate_data:
            raise HTTPException(status_code=404, detail="Candidate not found")
        
        # Parse candidate data
        candidate_dict = json.loads(candidate_data)
        candidate = Candidate(**candidate_dict)
        
        if not candidate.skills:
            raise HTTPException(status_code=400, detail="Candidate has no skills listed")
        
        # Generate cache key for this search
        cache_key = generate_cache_key(candidate.skills, "Remote")
        
        # Try to get cached results
        cached_jobs = redis_client.get(cache_key)
        if cached_jobs:
            logger.info(f"Cache hit for key: {cache_key}")
            return json.loads(cached_jobs)
            
        # If no cache hit, scrape jobs
        logger.info(f"Cache miss for key: {cache_key}")
        jobs = scrape_indeed_jobs(candidate.skills)
        
        if jobs:
            logger.info(f"Ranking {len(jobs)} jobs for candidate {candidate_id}")
            # Rank jobs based on candidate skills
            ranked_jobs = await rank_jobs(jobs, candidate.skills)
            
            # Cache the ranked results for 2 hours
            redis_client.setex(
                cache_key,
                timedelta(hours=2),
                json.dumps([job.dict() for job in ranked_jobs])
            )
            
            return ranked_jobs
        
        return jobs
        
    except redis.RedisError as e:
        logger.error(f"Redis error: {str(e)}")
        # If Redis fails, fall back to direct scraping
        return scrape_indeed_jobs(candidate.skills) if candidate.skills else []
    except Exception as e:
        logger.error(f"Unexpected error in get_jobs_for_candidate: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")
