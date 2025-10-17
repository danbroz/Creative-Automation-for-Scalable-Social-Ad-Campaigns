"""
Campaign Queue Manager
======================

Queue management system for campaign processing jobs. Provides status tracking,
priority queuing, and job state management for batch campaign processing.

This module implements a simple yet effective queuing system that can be extended
to use Redis, RabbitMQ, or other message queue systems for distributed processing.
"""

from typing import List, Dict, Optional
from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime
import json
from pathlib import Path


class CampaignStatus(Enum):
    """
    Enum representing possible campaign processing statuses.
    
    Status Flow:
        PENDING → IN_PROGRESS → COMPLETED
                            → FAILED
                            → CANCELLED
    """
    PENDING = "pending"       # Campaign queued, not yet started
    IN_PROGRESS = "in_progress"  # Currently being processed
    COMPLETED = "completed"    # Successfully completed
    FAILED = "failed"          # Processing failed
    CANCELLED = "cancelled"    # Manually cancelled


@dataclass
class CampaignJob:
    """
    Represents a single campaign processing job.
    
    Attributes:
        job_id (str): Unique identifier for this job
        brief_path (str): Path to campaign brief JSON file
        status (CampaignStatus): Current job status
        priority (int): Job priority (higher = processed first)
        created_at (datetime): When the job was created
        started_at (Optional[datetime]): When processing started
        completed_at (Optional[datetime]): When processing finished
        error_message (Optional[str]): Error message if failed
        result (Optional[Dict]): Processing result data
    """
    job_id: str
    brief_path: str
    status: CampaignStatus = CampaignStatus.PENDING
    priority: int = 0
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    result: Optional[Dict] = None
    
    def to_dict(self) -> Dict:
        """Convert job to dictionary for serialization."""
        return {
            'job_id': self.job_id,
            'brief_path': self.brief_path,
            'status': self.status.value,
            'priority': self.priority,
            'created_at': self.created_at.isoformat(),
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'error_message': self.error_message,
            'result': self.result
        }


class CampaignQueue:
    """
    Queue manager for campaign processing jobs.
    
    Provides a simple in-memory queue with status tracking and priority support.
    Can be extended to use external queue systems like Redis or RabbitMQ.
    
    Example:
        queue = CampaignQueue()
        
        # Add jobs
        job_id = queue.add_job("campaigns/brief1.json", priority=1)
        
        # Get next job
        job = queue.get_next_job()
        
        # Update status
        queue.update_status(job_id, CampaignStatus.COMPLETED)
    """
    
    def __init__(self):
        """Initialize empty campaign queue."""
        self.jobs: Dict[str, CampaignJob] = {}  # job_id -> CampaignJob
        self.job_counter = 0
    
    def add_job(self, brief_path: str, priority: int = 0) -> str:
        """
        Add a new campaign job to the queue.
        
        Args:
            brief_path (str): Path to campaign brief JSON file
            priority (int): Job priority (higher = processed first, default: 0)
        
        Returns:
            str: Unique job ID
        
        Example:
            job_id = queue.add_job("campaigns/summer_sale.json", priority=10)
        """
        self.job_counter += 1
        job_id = f"job_{self.job_counter:06d}"
        
        job = CampaignJob(
            job_id=job_id,
            brief_path=brief_path,
            priority=priority
        )
        
        self.jobs[job_id] = job
        return job_id
    
    def get_next_job(self) -> Optional[CampaignJob]:
        """
        Get the next pending job with highest priority.
        
        Returns:
            Optional[CampaignJob]: Next job to process, or None if queue is empty
        
        Example:
            job = queue.get_next_job()
            if job:
                process_campaign(job.brief_path)
        """
        # Filter pending jobs
        pending_jobs = [
            job for job in self.jobs.values()
            if job.status == CampaignStatus.PENDING
        ]
        
        if not pending_jobs:
            return None
        
        # Sort by priority (descending) and then by created_at (ascending)
        pending_jobs.sort(key=lambda j: (-j.priority, j.created_at))
        
        return pending_jobs[0]
    
    def update_status(
        self,
        job_id: str,
        status: CampaignStatus,
        error_message: Optional[str] = None,
        result: Optional[Dict] = None
    ) -> bool:
        """
        Update the status of a job.
        
        Args:
            job_id (str): Job ID to update
            status (CampaignStatus): New status
            error_message (Optional[str]): Error message if failed
            result (Optional[Dict]): Result data if completed
        
        Returns:
            bool: True if updated successfully, False if job not found
        
        Example:
            queue.update_status(
                job_id,
                CampaignStatus.COMPLETED,
                result={'assets_generated': 12}
            )
        """
        if job_id not in self.jobs:
            return False
        
        job = self.jobs[job_id]
        job.status = status
        
        if status == CampaignStatus.IN_PROGRESS and job.started_at is None:
            job.started_at = datetime.now()
        
        if status in [CampaignStatus.COMPLETED, CampaignStatus.FAILED]:
            job.completed_at = datetime.now()
        
        if error_message:
            job.error_message = error_message
        
        if result:
            job.result = result
        
        return True
    
    def get_job(self, job_id: str) -> Optional[CampaignJob]:
        """
        Get a specific job by ID.
        
        Args:
            job_id (str): Job ID
        
        Returns:
            Optional[CampaignJob]: Job object or None if not found
        """
        return self.jobs.get(job_id)
    
    def get_all_jobs(self, status_filter: Optional[CampaignStatus] = None) -> List[CampaignJob]:
        """
        Get all jobs, optionally filtered by status.
        
        Args:
            status_filter (Optional[CampaignStatus]): Filter by status
        
        Returns:
            List[CampaignJob]: List of jobs
        
        Example:
            # Get all completed jobs
            completed = queue.get_all_jobs(CampaignStatus.COMPLETED)
        """
        jobs = list(self.jobs.values())
        
        if status_filter:
            jobs = [j for j in jobs if j.status == status_filter]
        
        return jobs
    
    def get_statistics(self) -> Dict:
        """
        Get queue statistics.
        
        Returns:
            Dict: Statistics including counts by status, average processing time, etc.
        
        Example:
            stats = queue.get_statistics()
            print(f"Completed: {stats['completed']}")
            print(f"Avg time: {stats['avg_processing_time']:.2f}s")
        """
        jobs = list(self.jobs.values())
        
        stats = {
            'total': len(jobs),
            'pending': sum(1 for j in jobs if j.status == CampaignStatus.PENDING),
            'in_progress': sum(1 for j in jobs if j.status == CampaignStatus.IN_PROGRESS),
            'completed': sum(1 for j in jobs if j.status == CampaignStatus.COMPLETED),
            'failed': sum(1 for j in jobs if j.status == CampaignStatus.FAILED),
            'cancelled': sum(1 for j in jobs if j.status == CampaignStatus.CANCELLED)
        }
        
        # Calculate average processing time for completed jobs
        completed_jobs = [j for j in jobs if j.status == CampaignStatus.COMPLETED and j.started_at and j.completed_at]
        if completed_jobs:
            total_time = sum((j.completed_at - j.started_at).total_seconds() for j in completed_jobs)
            stats['avg_processing_time'] = total_time / len(completed_jobs)
        else:
            stats['avg_processing_time'] = 0
        
        return stats
    
    def save_state(self, file_path: str = "campaign_queue_state.json") -> None:
        """
        Save queue state to a file for persistence.
        
        Args:
            file_path (str): Path to save file
        
        Example:
            queue.save_state("queue_backup.json")
        """
        state = {
            'job_counter': self.job_counter,
            'jobs': [job.to_dict() for job in self.jobs.values()]
        }
        
        with open(file_path, 'w') as f:
            json.dump(state, f, indent=2)
    
    def load_state(self, file_path: str = "campaign_queue_state.json") -> bool:
        """
        Load queue state from a file.
        
        Args:
            file_path (str): Path to state file
        
        Returns:
            bool: True if loaded successfully
        
        Example:
            if queue.load_state("queue_backup.json"):
                print("Queue state restored")
        """
        try:
            with open(file_path, 'r') as f:
                state = json.load(f)
            
            self.job_counter = state['job_counter']
            self.jobs = {}
            
            for job_dict in state['jobs']:
                job = CampaignJob(
                    job_id=job_dict['job_id'],
                    brief_path=job_dict['brief_path'],
                    status=CampaignStatus(job_dict['status']),
                    priority=job_dict['priority'],
                    created_at=datetime.fromisoformat(job_dict['created_at']),
                    started_at=datetime.fromisoformat(job_dict['started_at']) if job_dict['started_at'] else None,
                    completed_at=datetime.fromisoformat(job_dict['completed_at']) if job_dict['completed_at'] else None,
                    error_message=job_dict['error_message'],
                    result=job_dict['result']
                )
                self.jobs[job.job_id] = job
            
            return True
            
        except Exception as e:
            print(f"Error loading queue state: {e}")
            return False

