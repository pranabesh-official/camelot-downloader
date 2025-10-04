"""
Download Queue Manager for handling multiple concurrent downloads efficiently.
This module provides a centralized queue system with proper resource management,
priority support, and error handling for the download manager.
"""

import asyncio
import threading
import time
import queue
import logging
from typing import Dict, List, Optional, Callable, Any
from dataclasses import dataclass, field
from enum import Enum
import uuid
from concurrent.futures import ThreadPoolExecutor
import psutil
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DownloadPriority(Enum):
    """Download priority levels"""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    URGENT = 4

class DownloadStatus(Enum):
    """Download status states"""
    QUEUED = "queued"
    DOWNLOADING = "downloading"
    CONVERTING = "converting"
    METADATA = "metadata"
    ANALYZING = "analyzing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    PAUSED = "paused"

@dataclass
class DownloadTask:
    """Represents a download task in the queue"""
    id: str
    url: str
    title: str
    artist: str
    album: Optional[str] = None
    download_path: str = ""
    priority: DownloadPriority = DownloadPriority.NORMAL
    status: DownloadStatus = DownloadStatus.QUEUED
    progress: float = 0.0
    stage: str = "queued"
    message: str = "Added to download queue"
    file_size: int = 0
    downloaded_size: int = 0
    start_time: Optional[float] = None
    end_time: Optional[float] = None
    error: Optional[str] = None
    retry_count: int = 0
    max_retries: int = 3
    can_cancel: bool = True
    can_retry: bool = False
    quality: str = "320kbps"
    format: str = "mp3"
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: float = field(default_factory=time.time)
    
    def __post_init__(self):
        if not self.id:
            self.id = str(uuid.uuid4())

class DownloadQueueManager:
    """Manages download queue with proper resource management and prioritization"""
    
    def __init__(self, max_concurrent_downloads: int = 3, max_retries: int = 3):
        self.max_concurrent_downloads = max_concurrent_downloads
        self.max_retries = max_retries
        self.download_queue = queue.PriorityQueue()
        self.active_downloads: Dict[str, DownloadTask] = {}
        self.completed_downloads: Dict[str, DownloadTask] = {}
        self.failed_downloads: Dict[str, DownloadTask] = {}
        self.download_lock = threading.Lock()
        self.executor = ThreadPoolExecutor(max_workers=max_concurrent_downloads)
        self.is_running = False
        self.queue_thread: Optional[threading.Thread] = None
        self.progress_callbacks: List[Callable] = []
        self.completion_callbacks: List[Callable] = []
        self.error_callbacks: List[Callable] = []
        
        # Resource monitoring
        self.cpu_threshold = 80.0  # CPU usage threshold
        self.memory_threshold = 80.0  # Memory usage threshold
        self.disk_threshold = 90.0  # Disk usage threshold
        
        logger.info(f"DownloadQueueManager initialized with max_concurrent_downloads={max_concurrent_downloads}")
    
    def add_progress_callback(self, callback: Callable):
        """Add a progress callback function"""
        self.progress_callbacks.append(callback)
    
    def add_completion_callback(self, callback: Callable):
        """Add a completion callback function"""
        self.completion_callbacks.append(callback)
    
    def add_error_callback(self, callback: Callable):
        """Add an error callback function"""
        self.error_callbacks.append(callback)
    
    def _emit_progress(self, task: DownloadTask):
        """Emit progress update to all registered callbacks"""
        for callback in self.progress_callbacks:
            try:
                callback(task)
            except Exception as e:
                logger.error(f"Error in progress callback: {e}")
    
    def _emit_completion(self, task: DownloadTask):
        """Emit completion update to all registered callbacks"""
        for callback in self.completion_callbacks:
            try:
                callback(task)
            except Exception as e:
                logger.error(f"Error in completion callback: {e}")
    
    def _emit_error(self, task: DownloadTask):
        """Emit error update to all registered callbacks"""
        for callback in self.error_callbacks:
            try:
                callback(task)
            except Exception as e:
                logger.error(f"Error in error callback: {e}")
    
    def _check_system_resources(self) -> bool:
        """Check if system resources are available for new downloads"""
        try:
            # Check CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            if cpu_percent > self.cpu_threshold:
                logger.warning(f"CPU usage too high: {cpu_percent}%")
                return False
            
            # Check memory usage
            memory = psutil.virtual_memory()
            if memory.percent > self.memory_threshold:
                logger.warning(f"Memory usage too high: {memory.percent}%")
                return False
            
            # Check disk usage for download path
            if hasattr(self, 'download_path') and self.download_path:
                disk_usage = psutil.disk_usage(self.download_path)
                disk_percent = (disk_usage.used / disk_usage.total) * 100
                if disk_percent > self.disk_threshold:
                    logger.warning(f"Disk usage too high: {disk_percent}%")
                    return False
            
            return True
        except Exception as e:
            logger.error(f"Error checking system resources: {e}")
            return True  # Allow download if we can't check resources
    
    def add_download(self, task: DownloadTask) -> str:
        """Add a download task to the queue"""
        with self.download_lock:
            # Check if task already exists
            if task.id in self.active_downloads:
                logger.warning(f"Download task {task.id} already exists")
                return task.id
            
            # Set priority for queue ordering (higher priority = lower number)
            priority_value = (5 - task.priority.value, task.created_at)
            
            # Add to priority queue
            self.download_queue.put((priority_value, task))
            
            logger.info(f"Added download task {task.id} to queue: {task.title} by {task.artist}")
            
            # Start queue processor if not running
            if not self.is_running:
                self.start()
            
            return task.id
    
    def start(self):
        """Start the download queue processor"""
        if self.is_running:
            return
        
        self.is_running = True
        self.queue_thread = threading.Thread(target=self._process_queue, daemon=True)
        self.queue_thread.start()
        logger.info("Download queue processor started")
    
    def stop(self):
        """Stop the download queue processor"""
        self.is_running = False
        if self.queue_thread:
            self.queue_thread.join(timeout=5)
        self.executor.shutdown(wait=True)
        logger.info("Download queue processor stopped")
    
    def _process_queue(self):
        """Main queue processing loop"""
        while self.is_running:
            try:
                # Check if we can start more downloads
                if len(self.active_downloads) < self.max_concurrent_downloads:
                    # Check system resources
                    if not self._check_system_resources():
                        time.sleep(2)  # Wait before checking again
                        continue
                    
                    # Get next task from queue
                    try:
                        priority_value, task = self.download_queue.get(timeout=1)
                        
                        # Check if task is still valid
                        if task.status == DownloadStatus.CANCELLED:
                            continue
                        
                        # Start download
                        self._start_download(task)
                        
                    except queue.Empty:
                        continue
                
                time.sleep(0.5)  # Small delay to prevent busy waiting
                
            except Exception as e:
                logger.error(f"Error in queue processor: {e}")
                time.sleep(1)
    
    def _start_download(self, task: DownloadTask):
        """Start a download task"""
        with self.download_lock:
            task.status = DownloadStatus.DOWNLOADING
            task.start_time = time.time()
            task.stage = "initializing"
            task.message = "Starting download..."
            self.active_downloads[task.id] = task
        
        # Submit to thread pool
        future = self.executor.submit(self._execute_download, task)
        
        # Add callback for completion
        future.add_done_callback(lambda f: self._handle_download_completion(task, f))
        
        logger.info(f"Started download task {task.id}: {task.title}")
        self._emit_progress(task)
    
    def _execute_download(self, task: DownloadTask):
        """Execute the actual download using the main application's download function"""
        try:
            # Import the download function from the main API module
            import sys
            import os
            sys.path.append(os.path.dirname(os.path.abspath(__file__)))
            
            # We'll need to call the actual download function from api.py
            # For now, we'll implement a simplified version that calls the existing download logic
            
            # Update progress
            task.stage = "downloading"
            task.message = "Downloading audio..."
            task.progress = 10.0
            self._emit_progress(task)
            
            # Create safe filename
            safe_title = "".join(c for c in f"{task.artist} - {task.title}" if c.isalnum() or c in (' ', '-', '_')).rstrip()
            if len(safe_title) > 200:
                safe_title = safe_title[:200]
            if not safe_title:  # Fallback if title becomes empty
                safe_title = f"download_{int(time.time())}"
            
            final_filename = f"{safe_title}.mp3"
            
            # Ensure download path exists and is valid
            if not task.download_path or not os.path.exists(task.download_path):
                # Use a default download path
                import os
                home_dir = os.path.expanduser("~")
                default_path = os.path.join(home_dir, "Music", "CAMELOTDJ")
                os.makedirs(default_path, exist_ok=True)
                task.download_path = default_path
                logger.warning(f"Using default download path: {default_path}")
            
            final_path = os.path.join(task.download_path, final_filename)
            
            # Check if file already exists
            if os.path.exists(final_path):
                timestamp = int(time.time())
                final_filename = f"{safe_title}_{timestamp}.mp3"
                final_path = os.path.join(task.download_path, final_filename)
            
            logger.info(f"📁 Download path: {task.download_path}")
            logger.info(f"📄 Final filename: {final_filename}")
            logger.info(f"🎯 Full path: {final_path}")
            
            # Update progress
            task.stage = "downloading"
            task.message = "Downloading with yt-dlp..."
            task.progress = 30.0
            self._emit_progress(task)
            
            # Call the actual download function
            success = self._perform_actual_download(task, final_path)
            
            if not success:
                raise Exception("Download failed")
            
            # Complete
            task.status = DownloadStatus.COMPLETED
            task.stage = "complete"
            task.message = "Download complete!"
            task.progress = 100.0
            task.end_time = time.time()
            task.file_size = os.path.getsize(final_path) if os.path.exists(final_path) else 0
            
            return task
            
        except Exception as e:
            task.status = DownloadStatus.FAILED
            task.stage = "error"
            task.message = f"Download failed: {str(e)}"
            task.error = str(e)
            task.end_time = time.time()
            raise e
    
    def _perform_actual_download(self, task: DownloadTask, final_path: str) -> bool:
        """Perform the actual download using a simplified, direct approach"""
        try:
            import yt_dlp
            import os
            import tempfile
            
            # Create output directory if it doesn't exist
            os.makedirs(os.path.dirname(final_path), exist_ok=True)
            
            # Update progress
            task.stage = "downloading"
            task.message = "Downloading with yt-dlp..."
            task.progress = 30.0
            self._emit_progress(task)
            
            # Progress hook for yt-dlp
            def progress_hook(d):
                if d['status'] == 'downloading':
                    total_bytes = d.get('total_bytes') or d.get('total_bytes_estimate', 0)
                    downloaded_bytes = d.get('downloaded_bytes', 0)
                    
                    if total_bytes > 0:
                        progress = min(int((downloaded_bytes / total_bytes) * 60) + 30, 90)  # 30-90%
                        task.progress = progress
                        task.message = f'Downloading... {progress}%'
                        self._emit_progress(task)
                elif d['status'] == 'finished':
                    task.progress = 90
                    task.message = 'Download complete, processing...'
                    self._emit_progress(task)
            
            # Simplified yt-dlp options that work with current YouTube
            ydl_opts = {
                'format': 'bestaudio[acodec!=none]/best[acodec!=none]/bestaudio/best',
                'outtmpl': final_path.replace('.mp3', '.%(ext)s'),
                'noplaylist': True,
                'extractaudio': True,
                'audioformat': 'mp3',
                'audioquality': '320',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '320',
                }],
                'quiet': False,
                'no_warnings': False,
                'progress_hooks': [progress_hook],
                'extractor_args': {
                    'youtube': {
                        'player_client': ['android', 'web'],
                        'player_skip': ['webpage'],
                    }
                }
            }
            
            # Perform download
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                logger.info(f"🎵 Enhanced yt-dlp downloading: {task.url}")
                
                try:
                    ydl.download([task.url])
                except Exception as download_exception:
                    logger.error(f"❌ Download failed: {str(download_exception)}")
                    
                    # Try with Android client only if format error
                    if 'Requested format is not available' in str(download_exception):
                        logger.info("🔄 Retrying with Android client only...")
                        ydl_opts['extractor_args']['youtube']['player_client'] = ['android']
                        
                        try:
                            with yt_dlp.YoutubeDL(ydl_opts) as ydl_retry:
                                ydl_retry.download([task.url])
                        except Exception as retry_exception:
                            logger.error(f"❌ Retry also failed: {str(retry_exception)}")
                            raise retry_exception
                    else:
                        raise download_exception
            
            # Check if file was created (yt-dlp might add .mp3 extension)
            if os.path.exists(final_path):
                logger.info(f"✅ Download successful: {final_path}")
                return True
            elif os.path.exists(final_path.replace('.mp3', '.mp3.mp3')):
                # Sometimes yt-dlp adds double extension
                os.rename(final_path.replace('.mp3', '.mp3.mp3'), final_path)
                logger.info(f"✅ Download successful (renamed): {final_path}")
                return True
            else:
                # Look for any file with similar name
                base_name = os.path.splitext(final_path)[0]
                dir_name = os.path.dirname(final_path)
                
                if os.path.exists(dir_name):
                    for file in os.listdir(dir_name):
                        if file.startswith(os.path.basename(base_name)) and file.endswith('.mp3'):
                            old_path = os.path.join(dir_name, file)
                            os.rename(old_path, final_path)
                            logger.info(f"✅ Download successful (found and renamed): {final_path}")
                            return True
                
                logger.error(f"❌ Download failed: File not found at {final_path}")
                return False
            
        except Exception as e:
            logger.error(f"Download execution failed: {e}")
            return False
    
    def _handle_download_completion(self, task: DownloadTask, future):
        """Handle download completion"""
        with self.download_lock:
            # Remove from active downloads
            if task.id in self.active_downloads:
                del self.active_downloads[task.id]
            
            try:
                # Check if download was successful
                if future.exception() is None:
                    task.status = DownloadStatus.COMPLETED
                    self.completed_downloads[task.id] = task
                    logger.info(f"Download completed successfully: {task.title}")
                    self._emit_completion(task)
                else:
                    # Handle retry logic
                    if task.retry_count < task.max_retries:
                        task.retry_count += 1
                        task.status = DownloadStatus.QUEUED
                        task.stage = "queued"
                        task.message = f"Retrying download (attempt {task.retry_count + 1}/{task.max_retries + 1})..."
                        task.progress = 0.0
                        task.error = None
                        
                        # Re-add to queue with higher priority
                        priority_value = (5 - task.priority.value, task.created_at)
                        self.download_queue.put((priority_value, task))
                        
                        logger.info(f"Retrying download {task.id} (attempt {task.retry_count})")
                    else:
                        task.status = DownloadStatus.FAILED
                        self.failed_downloads[task.id] = task
                        logger.error(f"Download failed after {task.max_retries} retries: {task.title}")
                        self._emit_error(task)
                        
            except Exception as e:
                logger.error(f"Error handling download completion: {e}")
                task.status = DownloadStatus.FAILED
                task.error = str(e)
                self.failed_downloads[task.id] = task
                self._emit_error(task)
    
    def cancel_download(self, task_id: str) -> bool:
        """Cancel a download task"""
        with self.download_lock:
            # Check active downloads
            if task_id in self.active_downloads:
                task = self.active_downloads[task_id]
                task.status = DownloadStatus.CANCELLED
                task.stage = "cancelled"
                task.message = "Download cancelled"
                task.can_cancel = False
                task.can_retry = True
                del self.active_downloads[task_id]
                logger.info(f"Cancelled download: {task.title}")
                self._emit_progress(task)
                return True
            
            # Check queued downloads
            # Note: This is a simplified approach. In a real implementation,
            # you'd need to remove the task from the priority queue
            logger.warning(f"Could not cancel download {task_id}: not found in active downloads")
            return False
    
    def retry_download(self, task_id: str) -> bool:
        """Retry a failed download"""
        with self.download_lock:
            if task_id in self.failed_downloads:
                task = self.failed_downloads[task_id]
                task.status = DownloadStatus.QUEUED
                task.stage = "queued"
                task.message = "Retrying download..."
                task.progress = 0.0
                task.retry_count = 0
                task.error = None
                task.can_retry = False
                task.can_cancel = True
                
                # Remove from failed downloads
                del self.failed_downloads[task_id]
                
                # Re-add to queue
                priority_value = (5 - task.priority.value, task.created_at)
                self.download_queue.put((priority_value, task))
                
                logger.info(f"Retrying download: {task.title}")
                return True
            
            return False
    
    def get_download_status(self, task_id: str) -> Optional[DownloadTask]:
        """Get the status of a download task"""
        with self.download_lock:
            # Check all dictionaries
            for download_dict in [self.active_downloads, self.completed_downloads, self.failed_downloads]:
                if task_id in download_dict:
                    return download_dict[task_id]
            return None
    
    def get_all_downloads(self) -> Dict[str, DownloadTask]:
        """Get all download tasks"""
        with self.download_lock:
            all_downloads = {}
            all_downloads.update(self.active_downloads)
            all_downloads.update(self.completed_downloads)
            all_downloads.update(self.failed_downloads)
            return all_downloads
    
    def get_queue_stats(self) -> Dict[str, int]:
        """Get queue statistics"""
        with self.download_lock:
            return {
                'queued': self.download_queue.qsize(),
                'active': len(self.active_downloads),
                'completed': len(self.completed_downloads),
                'failed': len(self.failed_downloads),
                'total': self.download_queue.qsize() + len(self.active_downloads) + 
                        len(self.completed_downloads) + len(self.failed_downloads)
            }
    
    def clear_completed_downloads(self):
        """Clear completed downloads from memory"""
        with self.download_lock:
            self.completed_downloads.clear()
            logger.info("Cleared completed downloads")
    
    def clear_failed_downloads(self):
        """Clear failed downloads from memory"""
        with self.download_lock:
            self.failed_downloads.clear()
            logger.info("Cleared failed downloads")
    
    def update_max_concurrent_downloads(self, new_max: int):
        """Update the maximum number of concurrent downloads"""
        with self.download_lock:
            self.max_concurrent_downloads = new_max
            # Update thread pool executor
            self.executor.shutdown(wait=True)
            self.executor = ThreadPoolExecutor(max_workers=new_max)
            logger.info(f"Updated max concurrent downloads to {new_max}")

# Global instance
download_queue_manager = DownloadQueueManager()
