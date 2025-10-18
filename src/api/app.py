"""
FastAPI Application - Main API Server
======================================

Main FastAPI application providing REST API endpoints for the Creative Automation Pipeline.

Endpoints:
    POST /api/v1/campaigns/create - Create new campaign
    POST /api/v1/campaigns/batch - Batch campaign creation
    GET /api/v1/campaigns/{id} - Get campaign status
    GET /api/v1/campaigns/{id}/assets - List campaign assets
    GET /api/v1/health - Health check
    GET / - API documentation (Swagger UI)

Authentication:
    Optional API key authentication via X-API-Key header
    Enable in config/features.json

Example Usage:
    # Start server
    uvicorn src.api.app:app --reload
    
    # Create campaign
    curl -X POST http://localhost:8000/api/v1/campaigns/create \
         -H "Content-Type: application/json" \
         -d @campaign_brief.json
"""

from fastapi import FastAPI, HTTPException, File, UploadFile, Depends, Header
from fastapi.responses import JSONResponse, FileResponse, RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from typing import List, Optional, Dict
import json
import uuid
from pathlib import Path
import asyncio
from datetime import datetime

# Import pipeline components
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from src.main import CreativeAutomationPipeline
from src.batch import BatchProcessor, CampaignQueue, CampaignStatus

# Initialize FastAPI app
app = FastAPI(
    title="Creative Automation Pipeline API",
    description="AI-powered creative automation for scalable social ad campaigns",
    version="2.0.0",
    docs_url="/docs",  # Swagger UI at /docs
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# CORS middleware - configure for production
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global campaign queue
campaign_queue = CampaignQueue()

# Pydantic models for API requests/responses
class ProductModel(BaseModel):
    """Product model for campaign briefs."""
    name: str = Field(..., description="Product name")
    description: Optional[str] = Field(None, description="Product description")

class CampaignBriefModel(BaseModel):
    """Campaign brief model."""
    campaign_name: Optional[str] = Field(None, description="Campaign name")
    products: List[ProductModel] = Field(..., min_items=1, description="List of products (minimum 1)")
    target_region: str = Field(..., description="Target region")
    target_audience: str = Field(..., description="Target audience")
    campaign_message: str = Field(..., max_length=500, description="Campaign message")
    language: Optional[str] = Field("en", description="Target language code")

class CampaignResponse(BaseModel):
    """Campaign creation response."""
    campaign_id: str
    status: str
    message: str

class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    version: str
    timestamp: str

# Optional API key authentication
async def verify_api_key(x_api_key: Optional[str] = Header(None)):
    """
    Verify API key if authentication is enabled.
    
    Args:
        x_api_key: API key from X-API-Key header
    
    Raises:
        HTTPException: If API key is invalid
    """
    # Load features config to check if auth is required
    try:
        features_path = Path("config/features.json")
        if features_path.exists():
            with open(features_path) as f:
                features = json.load(f)
                if features.get('security', {}).get('require_api_key', False):
                    # TODO: Implement proper API key validation
                    if not x_api_key:
                        raise HTTPException(status_code=401, detail="API key required")
    except Exception:
        pass  # Continue if config not found

# ============================================================================
# Web UI Routes
# ============================================================================

@app.get("/dashboard", response_class=FileResponse)
async def serve_dashboard():
    """Serve the main dashboard page."""
    return FileResponse("web/index.html")

@app.get("/")
async def root():
    """Redirect root to dashboard."""
    return RedirectResponse(url="/dashboard")

@app.get("/create-campaign.html", response_class=FileResponse)
async def serve_create_campaign():
    """Serve the campaign creation page."""
    return FileResponse("web/create-campaign.html")

@app.get("/campaigns.html", response_class=FileResponse)
async def serve_campaigns():
    """Serve the campaigns list page."""
    return FileResponse("web/campaigns.html")

@app.get("/campaign-detail.html", response_class=FileResponse)
async def serve_campaign_detail():
    """Serve the campaign detail page."""
    return FileResponse("web/campaign-detail.html")

# ============================================================================
# API Endpoints
# ============================================================================

@app.get("/api/v1/health", response_model=HealthResponse)
async def health_check():
    """
    Health check endpoint.
    
    Returns service status and version information.
    
    Returns:
        HealthResponse: Service health status
    """
    return HealthResponse(
        status="healthy",
        version="2.0.0",
        timestamp=datetime.now().isoformat()
    )

@app.post("/api/v1/campaigns/create", response_model=CampaignResponse, dependencies=[Depends(verify_api_key)])
async def create_campaign(brief: CampaignBriefModel):
    """
    Create a new campaign from a brief.
    
    This endpoint processes a single campaign brief and returns a campaign ID
    for status tracking.
    
    Args:
        brief: Campaign brief with products and targeting information
    
    Returns:
        CampaignResponse: Campaign ID and initial status
    
    Example:
        POST /api/v1/campaigns/create
        {
            "products": [
                {"name": "Product A", "description": "Description"},
                {"name": "Product B"}
            ],
            "target_region": "North America",
            "target_audience": "Young adults",
            "campaign_message": "Buy now!",
            "language": "en"
        }
    """
    try:
        # Generate campaign ID
        campaign_id = str(uuid.uuid4())
        
        # Save brief to temporary file
        temp_dir = Path("temp/campaigns")
        temp_dir.mkdir(parents=True, exist_ok=True)
        
        brief_path = temp_dir / f"{campaign_id}.json"
        brief_dict = brief.dict()
        
        with open(brief_path, 'w') as f:
            json.dump(brief_dict, f, indent=2)
        
        # Add to queue
        job_id = campaign_queue.add_job(str(brief_path))
        
        # Process in background
        asyncio.create_task(process_campaign_async(job_id, str(brief_path)))
        
        return CampaignResponse(
            campaign_id=job_id,
            status="queued",
            message="Campaign queued for processing"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/campaigns/batch", dependencies=[Depends(verify_api_key)])
async def create_batch_campaigns(files: List[UploadFile] = File(...)):
    """
    Create multiple campaigns from uploaded brief files.
    
    Args:
        files: List of campaign brief JSON files
    
    Returns:
        Dict: Batch processing status with campaign IDs
    
    Example:
        POST /api/v1/campaigns/batch
        Files: campaign1.json, campaign2.json, campaign3.json
    """
    try:
        campaign_ids = []
        
        for file in files:
            # Read and validate JSON
            content = await file.read()
            brief_data = json.loads(content)
            
            # Generate campaign ID
            campaign_id = str(uuid.uuid4())
            
            # Save brief
            temp_dir = Path("temp/campaigns")
            temp_dir.mkdir(parents=True, exist_ok=True)
            
            brief_path = temp_dir / f"{campaign_id}.json"
            with open(brief_path, 'w') as f:
                json.dump(brief_data, f, indent=2)
            
            # Add to queue
            job_id = campaign_queue.add_job(str(brief_path))
            campaign_ids.append(job_id)
        
        # Process batch in background
        asyncio.create_task(process_batch_async(campaign_ids))
        
        return {
            "campaign_ids": campaign_ids,
            "status": "queued",
            "count": len(campaign_ids)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/campaigns/{campaign_id}", dependencies=[Depends(verify_api_key)])
async def get_campaign_status(campaign_id: str):
    """
    Get campaign processing status.
    
    Args:
        campaign_id: Campaign ID from creation response
    
    Returns:
        Dict: Campaign status and details
    
    Example:
        GET /api/v1/campaigns/12345-67890
    """
    job = campaign_queue.get_job(campaign_id)
    
    if not job:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    return {
        "campaign_id": job.job_id,
        "status": job.status.value,
        "brief_path": job.brief_path,
        "created_at": job.created_at.isoformat(),
        "started_at": job.started_at.isoformat() if job.started_at else None,
        "completed_at": job.completed_at.isoformat() if job.completed_at else None,
        "error": job.error_message,
        "result": job.result
    }

@app.get("/api/v1/campaigns/{campaign_id}/assets", dependencies=[Depends(verify_api_key)])
async def list_campaign_assets(campaign_id: str):
    """
    List all generated assets for a campaign.
    
    Args:
        campaign_id: Campaign ID
    
    Returns:
        Dict: List of asset URLs/paths
    """
    job = campaign_queue.get_job(campaign_id)
    
    if not job:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    if job.status != CampaignStatus.COMPLETED:
        return {
            "campaign_id": campaign_id,
            "status": job.status.value,
            "assets": [],
            "message": "Campaign not yet completed"
        }
    
    # Find assets in output directory
    # This is a simplified implementation
    output_dir = Path("output")
    assets = []
    
    # TODO: Implement proper asset discovery based on campaign name
    
    return {
        "campaign_id": campaign_id,
        "status": "completed",
        "assets": assets
    }

@app.get("/api/v1/stats", dependencies=[Depends(verify_api_key)])
async def get_statistics():
    """
    Get queue and processing statistics combined with filesystem campaigns.
    
    Returns:
        Dict: Statistics including queue size, success rate, etc.
    """
    # Get in-memory queue stats
    queue_stats = campaign_queue.get_statistics()
    
    # Scan output directory for completed campaigns
    from pathlib import Path as PathLib
    import os
    
    output_dir = PathLib("output")
    filesystem_campaigns = []
    
    if output_dir.exists():
        for item in output_dir.iterdir():
            if item.is_dir() and not item.name.startswith('.') and item.name != 'index.html':
                # Check if campaign has summary file (indicates completion)
                summary_file = item / "campaign_summary.json"
                execution_file = item / "execution_report.json"
                
                if summary_file.exists() or execution_file.exists():
                    import json
                    campaign_data = {
                        'job_id': f'fs_{item.name}',
                        'campaign_name': item.name,
                        'status': 'completed',
                        'created_at': datetime.fromtimestamp(item.stat().st_ctime).isoformat(),
                        'started_at': datetime.fromtimestamp(item.stat().st_ctime).isoformat(),
                        'completed_at': datetime.fromtimestamp(item.stat().st_mtime).isoformat(),
                        'brief_path': f'output/{item.name}/campaign_summary.json',
                        'source': 'filesystem'
                    }
                    
                    # Try to read summary for more details
                    try:
                        if summary_file.exists():
                            with open(summary_file, 'r') as f:
                                summary = json.load(f)
                                campaign_data['campaign_name'] = summary.get('campaign_name', item.name)
                    except:
                        pass
                    
                    filesystem_campaigns.append(campaign_data)
    
    # Combine queue campaigns and filesystem campaigns
    all_campaigns = list(queue_stats.get('recent_campaigns', []))
    
    # Add filesystem campaigns that aren't in the queue
    queue_ids = {c.get('job_id') for c in all_campaigns}
    for fs_campaign in filesystem_campaigns:
        if fs_campaign['job_id'] not in queue_ids:
            all_campaigns.append(fs_campaign)
    
    # Sort by completed time (most recent first)
    all_campaigns.sort(key=lambda x: x.get('completed_at', x.get('created_at', '')), reverse=True)
    
    # Recalculate totals
    filesystem_completed = len(filesystem_campaigns)
    total_completed = queue_stats.get('completed', 0) + filesystem_completed
    total_campaigns = queue_stats.get('total', 0) + filesystem_completed
    
    # Update stats
    combined_stats = {
        'total': total_campaigns,
        'pending': queue_stats.get('pending', 0),
        'in_progress': queue_stats.get('in_progress', 0),
        'completed': total_completed,
        'failed': queue_stats.get('failed', 0),
        'recent_campaigns': all_campaigns[:10],  # Limit to 10 most recent
        'filesystem_campaigns': filesystem_completed,
        'queue_campaigns': queue_stats.get('total', 0)
    }
    
    return combined_stats

@app.get("/api/v1/output/folders")
async def list_output_folders():
    """
    List all campaign folders in the output directory.
    
    Returns:
        Dict: List of campaign folders with metadata
    """
    try:
        import os
        from pathlib import Path as PathLib
        
        output_dir = PathLib("output")
        folders = []
        
        if output_dir.exists():
            for item in output_dir.iterdir():
                if item.is_dir() and not item.name.startswith('.'):
                    # Get folder stats
                    folder_info = {
                        'name': item.name,
                        'path': f'/api/v1/browse/output/{item.name}',
                        'modified': datetime.fromtimestamp(item.stat().st_mtime).isoformat(),
                        'size_mb': sum(f.stat().st_size for f in item.rglob('*') if f.is_file()) / (1024*1024)
                    }
                    folders.append(folder_info)
        
        # Sort by modified date (newest first)
        folders.sort(key=lambda x: x['modified'], reverse=True)
        
        return {
            'folders': folders,
            'count': len(folders)
        }
        
    except Exception as e:
        return {
            'folders': [],
            'count': 0,
            'error': str(e)
        }

@app.get("/api/v1/browse/output/{path:path}")
async def browse_output_directory(path: str = ""):
    """
    Browse files and directories in the output folder.
    Serves files and generates directory listings.
    
    Args:
        path: Relative path within output directory
        
    Returns:
        HTML directory listing or file content
    """
    from pathlib import Path as PathLib
    from fastapi.responses import FileResponse, HTMLResponse
    import mimetypes
    
    try:
        # Sanitize and resolve path
        output_dir = PathLib("output").resolve()
        if path:
            target_path = (output_dir / path).resolve()
        else:
            target_path = output_dir
            
        # Security check: ensure path is within output directory
        if not str(target_path).startswith(str(output_dir)):
            raise HTTPException(status_code=403, detail="Access denied")
            
        if not target_path.exists():
            raise HTTPException(status_code=404, detail="Path not found")
            
        # If it's a file, serve it
        if target_path.is_file():
            return FileResponse(target_path)
            
        # If it's a directory, generate listing
        if target_path.is_dir():
            items = []
            for item in sorted(target_path.iterdir()):
                if item.name.startswith('.'):
                    continue
                    
                item_info = {
                    'name': item.name,
                    'is_dir': item.is_dir(),
                    'size': item.stat().st_size if item.is_file() else 0,
                    'modified': datetime.fromtimestamp(item.stat().st_mtime).strftime('%Y-%m-%d %H:%M:%S')
                }
                items.append(item_info)
            
            # Generate HTML directory listing
            breadcrumbs = path.split('/') if path else []
            breadcrumb_html = '<a href="/api/v1/browse/output">output</a>'
            current_path = ""
            for crumb in breadcrumbs:
                if crumb:
                    current_path += f"/{crumb}" if current_path else crumb
                    breadcrumb_html += f' / <a href="/api/v1/browse/output/{current_path}">{crumb}</a>'
            
            items_html = ""
            for item in items:
                icon = "📁" if item['is_dir'] else "📄"
                size_str = f"{item['size'] / 1024:.1f} KB" if not item['is_dir'] else "-"
                item_path = f"{path}/{item['name']}" if path else item['name']
                items_html += f"""
                <tr class="hover:bg-gray-50">
                    <td class="px-6 py-3">
                        <a href="/api/v1/browse/output/{item_path}" class="text-blue-600 hover:text-blue-800 flex items-center">
                            <span class="mr-2">{icon}</span> {item['name']}
                        </a>
                    </td>
                    <td class="px-6 py-3 text-gray-600">{size_str}</td>
                    <td class="px-6 py-3 text-gray-500">{item['modified']}</td>
                </tr>
                """
            
            html_content = f"""
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Browse: {path or 'output'}</title>
                <script src="https://cdn.tailwindcss.com"></script>
            </head>
            <body class="bg-gray-50">
                <div class="max-w-7xl mx-auto px-4 py-8">
                    <div class="bg-white rounded-lg shadow-sm border border-gray-200">
                        <div class="px-6 py-4 border-b border-gray-200">
                            <h1 class="text-2xl font-bold text-gray-900">📁 {breadcrumb_html}</h1>
                            <p class="text-sm text-gray-500 mt-1">{len(items)} items</p>
                        </div>
                        <div class="overflow-x-auto">
                            <table class="w-full">
                                <thead class="bg-gray-50 border-b border-gray-200">
                                    <tr>
                                        <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Name</th>
                                        <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Size</th>
                                        <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Modified</th>
                                    </tr>
                                </thead>
                                <tbody class="divide-y divide-gray-200">
                                    {items_html}
                                </tbody>
                            </table>
                        </div>
                        <div class="px-6 py-4 border-t border-gray-200 bg-gray-50">
                            <a href="/output" class="text-blue-600 hover:text-blue-800">← Back to Asset Browser</a>
                            <span class="mx-3 text-gray-300">|</span>
                            <a href="/dashboard" class="text-blue-600 hover:text-blue-800">Dashboard</a>
                        </div>
                    </div>
                </div>
            </body>
            </html>
            """
            
            return HTMLResponse(content=html_content)
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Background processing functions

async def process_campaign_async(job_id: str, brief_path: str):
    """
    Process a campaign in the background.
    
    Args:
        job_id: Campaign job ID
        brief_path: Path to campaign brief file
    """
    try:
        # Update status to in_progress
        campaign_queue.update_status(job_id, CampaignStatus.IN_PROGRESS)
        
        # Run pipeline in thread pool to avoid blocking
        loop = asyncio.get_event_loop()
        pipeline = CreativeAutomationPipeline()
        success = await loop.run_in_executor(None, pipeline.run, brief_path)
        
        if success:
            campaign_queue.update_status(
                job_id,
                CampaignStatus.COMPLETED,
                result={"success": True}
            )
        else:
            campaign_queue.update_status(
                job_id,
                CampaignStatus.FAILED,
                error_message="Pipeline execution failed"
            )
            
    except Exception as e:
        campaign_queue.update_status(
            job_id,
            CampaignStatus.FAILED,
            error_message=str(e)
        )

async def process_batch_async(campaign_ids: List[str]):
    """
    Process multiple campaigns in batch.
    
    Args:
        campaign_ids: List of campaign job IDs
    """
    # Process each campaign
    for campaign_id in campaign_ids:
        job = campaign_queue.get_job(campaign_id)
        if job:
            await process_campaign_async(campaign_id, job.brief_path)

# Mount static files and directories at the end (after all routes)
# This prevents route conflicts
from pathlib import Path as PathLib

# Ensure output directory exists
PathLib("output").mkdir(parents=True, exist_ok=True)

# Mount static files
app.mount("/static", StaticFiles(directory="web/static"), name="static")
app.mount("/output", StaticFiles(directory="output", html=True), name="output")

# Run server if executed directly
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

