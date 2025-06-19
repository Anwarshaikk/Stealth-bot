import os
from typing import List, Optional
import redis
import requests
from bs4 import BeautifulSoup
from fastapi import APIRouter, HTTPException, Depends
from ..models import Job, Candidate
import json
import logging
from datetime import datetime, timedelta

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

def get_redis():
    redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    return redis.from_url(redis_url)

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
            # Cache the results for 2 hours
            redis_client.setex(
                cache_key,
                timedelta(hours=2),
                json.dumps([job.dict() for job in jobs])
            )
        
        return jobs
        
    except redis.RedisError as e:
        logger.error(f"Redis error: {str(e)}")
        # If Redis fails, fall back to direct scraping
        return scrape_indeed_jobs(candidate.skills) if candidate.skills else []
    except Exception as e:
        logger.error(f"Unexpected error in get_jobs_for_candidate: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")
