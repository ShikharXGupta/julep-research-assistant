from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import os
import httpx
import traceback
import yaml
import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = FastAPI(
    title="Julep AI Research Assistant API",
    description="API for performing research using Julep AI",
    version="1.0.0",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Replace with specific origins in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ResearchRequest(BaseModel):
    topic: str
    format: str  # Allow any custom format string

class ResearchResponse(BaseModel):
    result: str
    success: bool
    error: Optional[str] = None

# Initialize Julep client using their official SDK
try:
    from julep import Julep
    print("Initializing Julep client...")
    print(f"JULEP_API_KEY available: {'Yes' if os.getenv('JULEP_API_KEY') else 'No'}")
    
    # Initialize the official Julep client
    julep_sdk = Julep(api_key=os.getenv("JULEP_API_KEY"))
    
    # Create an agent
    agent = julep_sdk.agents.create(
        name="Research Assistant",
        model="claude-3.5-sonnet",
        about="You are a helpful research assistant. Your goal is to find concise information on topics provided by the user."
    )
    
    # Task definition
    task_definition = yaml.safe_load("""
    name: Research Request
    description: Perform research on a given topic and format
    main:
    - prompt:
      - role: system
        content: >
          You are a research assistant. Return research results strictly and only in one of the selected format the user asks for:
          - summary: 3-4 sentences
          - bullet points: max 5 points
          - short report: max 150 words
          - or a custom user-defined format.
      - role: user
        content: "$ f'Please provide a {steps[0].input.output_format} on the topic: {steps[0].input.topic}'"
    """)
    
    # Create the task
    task = julep_sdk.tasks.create(agent_id=agent.id, **task_definition)
    print(f"Julep agent created with ID: {agent.id}")
    print(f"Julep task created with ID: {task.id}")
    
    print("Julep client initialized successfully")
except ImportError:
    print("Official Julep SDK not found. Falling back to custom implementation.")
    julep_sdk = None
    task = None
except Exception as e:
    print(f"Error initializing Julep SDK: {e}")
    julep_sdk = None
    task = None

# Custom implementation as fallback
class JulepClient:
    """Custom client for interacting with the Julep AI API"""
    
    def __init__(self):
        self.api_key = os.getenv("JULEP_API_KEY")
        self.agent_id = os.getenv("JULEP_AGENT_ID")
        self.base_url = "https://api.julep.ai"
        
        if not self.api_key or not self.agent_id:
            raise ValueError("JULEP_API_KEY and JULEP_AGENT_ID environment variables must be set")
        
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    async def get_research(self, topic: str, output_format: str) -> str:
        """Get research information on a topic in the specified format"""
        try:
            prompt = self._format_research_prompt(topic, output_format)
            print(f"Sending request to Julep API with prompt: {prompt}")
            print(f"Using Agent ID: {self.agent_id}")
            print(f"API Key (first 5 chars): {self.api_key[:5] if self.api_key else 'None'}...")
            
            # Try different API endpoints to handle possible changes in their API structure
            endpoints = [
                f"{self.base_url}/v1/agents/{self.agent_id}/completions",
                f"{self.base_url}/agents/{self.agent_id}/completions",
                f"{self.base_url}/v1/completions",
                f"{self.base_url}/v1/agents/{self.agent_id}/generate"
            ]
            
            async with httpx.AsyncClient() as client:
                for endpoint in endpoints:
                    try:
                        print(f"Trying endpoint: {endpoint}")
                        payload = {"prompt": prompt, "max_tokens": 1000}
                        if "completions" not in endpoint and "generate" not in endpoint:
                            # Adjust payload for different endpoint structures
                            payload["agent_id"] = self.agent_id
                            
                        response = await client.post(
                            endpoint,
                            headers=self.headers,
                            json=payload,
                            timeout=30.0
                        )
                        
                        print(f"Response status code: {response.status_code}")
                        
                        if response.status_code == 200:
                            result = response.json()
                            print(f"Successful response received")
                            return result.get("completion", "")
                        else:
                            print(f"Error response body: {response.text}")
                            # Continue to next endpoint if this one failed
                    except httpx.RequestError as e:
                        print(f"Request error with endpoint {endpoint}: {e}")
                        # Continue to next endpoint if this one failed
                
                # If we get here, all endpoints failed
                raise Exception("All API endpoints failed. Check Julep API documentation for the correct endpoint.")
        except Exception as e:
            print(f"Exception in get_research: {type(e).__name__}: {e}")
            raise
    
    def _format_research_prompt(self, topic: str, output_format: str) -> str:
        """Format the prompt for the Julep AI agent"""
        return f"Please research the topic '{topic}' and provide {output_format}."

# Initialize fallback client if SDK initialization failed
if not julep_sdk or not task:
    try:
        print("Initializing custom Julep client...")
        print(f"JULEP_API_KEY available: {'Yes' if os.getenv('JULEP_API_KEY') else 'No'}")
        print(f"JULEP_AGENT_ID available: {'Yes' if os.getenv('JULEP_AGENT_ID') else 'No'}")
        julep_client = JulepClient()
        print("Custom Julep client initialized successfully")
    except Exception as e:
        print(f"Error initializing custom Julep client: {e}")
        raise

@app.get("/")
def home():
    """Root endpoint with API information"""
    return {
        "message": "Welcome to the Julep Research Assistant API!",
        "usage": "POST /api/research or /research with {'topic': '...', 'format': 'summary|bullet_points|short_report|custom_format'}",
        "docs": "/docs for Swagger UI",
        "health": "/api/health for API health check"
    }

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "ok",
        "julep_credentials": {
            "api_key_available": bool(os.getenv("JULEP_API_KEY")),
            "agent_id_available": bool(os.getenv("JULEP_AGENT_ID")),
            "sdk_available": julep_sdk is not None,
            "task_available": task is not None
        }
    }

@app.post("/api/research", response_model=ResearchResponse)
@app.post("/research")  # Adding compatibility with the second code's endpoint
async def perform_research(request: ResearchRequest):
    """Perform research on the specified topic and return results in the requested format"""
    topic = request.topic
    format_type = request.format
    
    print(f"Processing research request for topic: {topic}, format: {format_type}")
    
    # Try using the official SDK method first if available
    if julep_sdk and task:
        try:
            print(f"Using official Julep SDK for research")
            execution = julep_sdk.executions.create(
                task_id=task.id,
                input={"topic": topic, "output_format": format_type}
            )
            
            # Poll for completion
            while (result := julep_sdk.executions.get(execution.id)).status not in ['succeeded', 'failed']:
                time.sleep(1)
                
            if result.status == 'succeeded':
                output_text = result.output["choices"][0]["message"]["content"]
                return ResearchResponse(
                    result=output_text,
                    success=True
                )
            else:
                return ResearchResponse(
                    result="",
                    success=False,
                    error=f"Julep API error: {result.error}"
                )
        except Exception as e:
            error_detail = traceback.format_exc()
            print(f"Error using Julep SDK: {type(e).__name__}: {str(e)}")
            print(f"Traceback: {error_detail}")
            print("Falling back to custom implementation...")
            
            # Fall back to custom implementation if SDK method fails
            if not julep_client:
                return ResearchResponse(
                    result="",
                    success=False,
                    error=f"Failed to process research request: {str(e)}"
                )
    
    # Use the custom client as fallback
    if not julep_sdk or not task:
        try:
            print(f"Using custom Julep client for research")
            research_result = await julep_client.get_research(topic, format_type)
            
            return ResearchResponse(
                result=research_result,
                success=True
            )
        except Exception as e:
            error_detail = traceback.format_exc()
            print(f"Error in research endpoint: {type(e).__name__}: {str(e)}")
            print(f"Traceback: {error_detail}")
            
            return ResearchResponse(
                result="",
                success=False,
                error=f"Failed to process research request: {str(e) or 'Unknown error'}"
            )

@app.get("/api/test")
async def test_endpoint():
    """Simple test endpoint to verify API functionality"""
    return {
        "status": "ok",
        "julep_credentials": {
            "api_key_available": bool(os.getenv("JULEP_API_KEY")),
            "agent_id_available": bool(os.getenv("JULEP_AGENT_ID")),
            "sdk_available": julep_sdk is not None,
            "task_available": task is not None
        }
    }

# For local development
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
