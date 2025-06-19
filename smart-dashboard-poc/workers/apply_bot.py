import asyncio
from datetime import datetime, timezone
from typing import Dict, Optional
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeoutError, Page
import redis
import json
import os
import logging
from urllib.parse import urlparse

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Redis connection
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
redis_client = redis.from_url(REDIS_URL)

async def fill_common_fields(page: Page, candidate: Dict) -> None:
    """Fill common application form fields based on field detection."""
    common_field_selectors = {
        'name': [
            'input[name*="name" i]',
            'input[placeholder*="name" i]',
            'input[aria-label*="name" i]'
        ],
        'email': [
            'input[type="email"]',
            'input[name*="email" i]',
            'input[placeholder*="email" i]'
        ],
        'phone': [
            'input[type="tel"]',
            'input[name*="phone" i]',
            'input[placeholder*="phone" i]'
        ],
        'resume': [
            'input[type="file"]',
            'input[accept*=".pdf"]',
            'input[accept*=".docx"]'
        ]
    }

    # Try to fill in name fields
    for selector in common_field_selectors['name']:
        try:
            if await page.locator(selector).count() > 0:
                await page.fill(selector, candidate.get('name', ''))
                break
        except Exception:
            continue

    # Try to fill in email
    for selector in common_field_selectors['email']:
        try:
            if await page.locator(selector).count() > 0:
                await page.fill(selector, candidate.get('email', ''))
                break
        except Exception:
            continue

    # Try to fill in phone
    for selector in common_field_selectors['phone']:
        try:
            if await page.locator(selector).count() > 0:
                await page.fill(selector, candidate.get('mobile_number', ''))
                break
        except Exception:
            continue

    # Try to upload resume if field exists
    for selector in common_field_selectors['resume']:
        try:
            if await page.locator(selector).count() > 0:
                await page.set_input_files(selector, candidate.get('resume_file_path', ''))
                break
        except Exception:
            continue

async def handle_indeed_application(page: Page, candidate: Dict) -> bool:
    """Handle Indeed.com specific application flow."""
    try:
        # Check if we need to sign in
        if await page.locator('text="Sign in"').count() > 0:
            logger.info("Indeed sign-in required - skipping automated application")
            return False

        # Fill the application form if it exists
        if await page.locator('button:has-text("Apply now")').count() > 0:
            await page.click('button:has-text("Apply now")')
            await page.wait_for_load_state('networkidle')
            
            # Fill common fields
            await fill_common_fields(page, candidate)
            
            # Handle Indeed-specific fields
            await page.fill('textarea[name="jobSeekerSummary"]', 
                          f"Experienced professional with expertise in: {', '.join(candidate.get('skills', []))}")
            
            return True
    except Exception as e:
        logger.error(f"Error in Indeed application: {str(e)}")
        return False

async def handle_linkedin_application(page: Page, candidate: Dict) -> bool:
    """Handle LinkedIn specific application flow."""
    try:
        # Check if we need to sign in
        if await page.locator('text="Sign in"').count() > 0:
            logger.info("LinkedIn sign-in required - skipping automated application")
            return False

        # Look for the apply button
        if await page.locator('button:has-text("Easy Apply")').count() > 0:
            await page.click('button:has-text("Easy Apply")')
            await page.wait_for_load_state('networkidle')
            
            # Fill common fields
            await fill_common_fields(page, candidate)
            
            return True
    except Exception as e:
        logger.error(f"Error in LinkedIn application: {str(e)}")
        return False

async def apply_job(job_url: str, candidate: Dict) -> Dict:
    """
    Apply to a job using Playwright automation.
    Returns a dictionary with the application status and details.
    """
    try:
        async with async_playwright() as p:
            # Launch browser with stealth mode
            browser = await p.chromium.launch(
                headless=True,
                args=['--no-sandbox', '--disable-setuid-sandbox']
            )
            
            # Create a new context with custom viewport and user agent
            context = await browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            )
            
            page = await context.new_page()
            
            # Navigate to the job URL
            try:
                await page.goto(job_url, wait_until='networkidle')
            except Exception as e:
                return {"status": "failed", "reason": f"Failed to load page: {str(e)}"}

            # Determine the job site and handle accordingly
            domain = urlparse(job_url).netloc
            application_submitted = False
            
            if 'indeed.com' in domain:
                application_submitted = await handle_indeed_application(page, candidate)
            elif 'linkedin.com' in domain:
                application_submitted = await handle_linkedin_application(page, candidate)
            else:
                # Generic application handling
                try:
                    # Look for common apply buttons
                    apply_button_selectors = [
                        'button:has-text("Apply")',
                        'a:has-text("Apply")',
                        'button:has-text("Submit")',
                        'input[type="submit"]'
                    ]
                    
                    for selector in apply_button_selectors:
                        if await page.locator(selector).count() > 0:
                            await page.click(selector)
                            await page.wait_for_load_state('networkidle')
                            break
                    
                    # Fill common fields
                    await fill_common_fields(page, candidate)
                    application_submitted = True
                    
                except Exception as e:
                    logger.error(f"Error in generic application: {str(e)}")
                    application_submitted = False

            await browser.close()
            
            if application_submitted:
                return {
                    "status": "submitted",
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
            else:
                return {
                    "status": "manual_required",
                    "reason": "Could not complete automated application, manual application required"
                }
                
    except PlaywrightTimeoutError as e:
        return {"status": "failed", "reason": f"Timeout or captcha encountered: {str(e)}"}
    except Exception as e:
        return {"status": "failed", "reason": str(e)}

def apply_for_job(data: Dict[str, str]) -> None:
    """
    Process a job application using Playwright automation.
    
    Args:
        data: Dictionary containing:
            - candidate_id: ID of the candidate
            - job_url: URL of the job to apply for
            - application_id: ID of the application record
    """
    candidate_id = data["candidate_id"]
    job_url = data["job_url"]
    application_id = data["application_id"]

    logger.info(f"Processing application {application_id}")
    logger.info(f"Applying for candidate {candidate_id} to job at {job_url}")

    # Get candidate data from Redis
    candidate_data = redis_client.get(f"candidate:{candidate_id}")
    if not candidate_data:
        logger.error(f"Candidate {candidate_id} not found")
        return

    candidate = json.loads(candidate_data)
    
    # Run the Playwright automation
    result = asyncio.run(apply_job(job_url, candidate))
    
    # Update the application status in Redis
    redis_key = f"application:{application_id}"
    application_json = redis_client.get(redis_key)
    
    if application_json:
        application = json.loads(application_json)
        application.update({
            "status": result["status"],
            "updated_at": datetime.utcnow().isoformat(),
            "last_error": result.get("reason", None)
        })
        redis_client.set(redis_key, json.dumps(application))

    logger.info(f"Completed processing application {application_id} with status: {result['status']}")
