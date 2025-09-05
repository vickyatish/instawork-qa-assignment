import time
import json
import os
from typing import Dict, Any, List, Optional
from datetime import datetime
from .config import Config

class ObservabilityManager:
    """Manages observability metrics and logging for the AI Test Copilot."""
    
    def __init__(self):
        """Initialize the observability manager."""
        self.metrics_file = os.path.join(Config.REPORTS_DIR, "metrics.json")
        self.metrics = self._load_metrics()
    
    def _load_metrics(self) -> Dict[str, Any]:
        """Load existing metrics from file."""
        if os.path.exists(self.metrics_file):
            try:
                with open(self.metrics_file, 'r') as f:
                    return json.load(f)
            except Exception:
                pass
        
        return {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "total_tokens_used": 0,
            "total_cost": 0.0,
            "average_response_time": 0.0,
            "schema_validation_failures": 0,
            "retry_attempts": 0,
            "test_cases_generated": 0,
            "test_cases_updated": 0,
            "sessions": []
        }
    
    def _save_metrics(self) -> None:
        """Save metrics to file."""
        try:
            with open(self.metrics_file, 'w') as f:
                json.dump(self.metrics, f, indent=2)
        except Exception as e:
            print(f"Warning: Failed to save metrics: {str(e)}")
    
    def start_session(self, session_id: str, change_request_path: str) -> None:
        """Start a new processing session."""
        session = {
            "session_id": session_id,
            "change_request_path": change_request_path,
            "start_time": datetime.now().isoformat(),
            "end_time": None,
            "status": "running",
            "tokens_used": 0,
            "cost": 0.0,
            "test_cases_generated": 0,
            "test_cases_updated": 0,
            "retry_attempts": 0,
            "schema_validation_failures": 0,
            "errors": []
        }
        
        self.metrics["sessions"].append(session)
        self._save_metrics()
    
    def end_session(self, session_id: str, status: str, **kwargs) -> None:
        """End a processing session."""
        session = self._get_current_session(session_id)
        if not session:
            return
        
        session["end_time"] = datetime.now().isoformat()
        session["status"] = status
        
        # Update session with provided metrics
        for key, value in kwargs.items():
            if key in session:
                session[key] = value
        
        # Update global metrics
        self.metrics["total_requests"] += 1
        if status == "success":
            self.metrics["successful_requests"] += 1
        else:
            self.metrics["failed_requests"] += 1
        
        self.metrics["total_tokens_used"] += session.get("tokens_used", 0)
        self.metrics["total_cost"] += session.get("cost", 0.0)
        self.metrics["test_cases_generated"] += session.get("test_cases_generated", 0)
        self.metrics["test_cases_updated"] += session.get("test_cases_updated", 0)
        self.metrics["retry_attempts"] += session.get("retry_attempts", 0)
        self.metrics["schema_validation_failures"] += session.get("schema_validation_failures", 0)
        
        # Calculate average response time
        if session["start_time"] and session["end_time"]:
            start_time = datetime.fromisoformat(session["start_time"])
            end_time = datetime.fromisoformat(session["end_time"])
            response_time = (end_time - start_time).total_seconds()
            
            # Update running average
            total_sessions = len([s for s in self.metrics["sessions"] if s.get("end_time")])
            if total_sessions > 0:
                current_avg = self.metrics["average_response_time"]
                self.metrics["average_response_time"] = (
                    (current_avg * (total_sessions - 1) + response_time) / total_sessions
                )
        
        self._save_metrics()
    
    def _get_current_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get the current session by ID."""
        for session in reversed(self.metrics["sessions"]):
            if session.get("session_id") == session_id:
                return session
        return None
    
    def log_llm_call(self, session_id: str, model: str, tokens_used: int, cost: float) -> None:
        """Log an LLM API call."""
        session = self._get_current_session(session_id)
        if session:
            session["tokens_used"] = session.get("tokens_used", 0) + tokens_used
            session["cost"] = session.get("cost", 0.0) + cost
            self._save_metrics()
    
    def log_schema_validation_failure(self, session_id: str, error: str) -> None:
        """Log a schema validation failure."""
        session = self._get_current_session(session_id)
        if session:
            session["schema_validation_failures"] = session.get("schema_validation_failures", 0) + 1
            session["errors"].append(f"Schema validation failure: {error}")
            self._save_metrics()
    
    def log_retry_attempt(self, session_id: str, reason: str) -> None:
        """Log a retry attempt."""
        session = self._get_current_session(session_id)
        if session:
            session["retry_attempts"] = session.get("retry_attempts", 0) + 1
            session["errors"].append(f"Retry attempt: {reason}")
            self._save_metrics()
    
    def log_test_case_operation(self, session_id: str, operation: str, count: int = 1) -> None:
        """Log test case generation or update."""
        session = self._get_current_session(session_id)
        if session:
            if operation == "generated":
                session["test_cases_generated"] = session.get("test_cases_generated", 0) + count
            elif operation == "updated":
                session["test_cases_updated"] = session.get("test_cases_updated", 0) + count
            self._save_metrics()
    
    def get_metrics_summary(self) -> Dict[str, Any]:
        """Get a summary of current metrics."""
        total_sessions = len(self.metrics["sessions"])
        successful_sessions = len([s for s in self.metrics["sessions"] if s.get("status") == "success"])
        
        success_rate = (successful_sessions / total_sessions * 100) if total_sessions > 0 else 0
        
        return {
            "total_requests": self.metrics["total_requests"],
            "success_rate": round(success_rate, 2),
            "total_tokens_used": self.metrics["total_tokens_used"],
            "total_cost": round(self.metrics["total_cost"], 4),
            "average_response_time": round(self.metrics["average_response_time"], 2),
            "test_cases_generated": self.metrics["test_cases_generated"],
            "test_cases_updated": self.metrics["test_cases_updated"],
            "schema_validation_failures": self.metrics["schema_validation_failures"],
            "retry_attempts": self.metrics["retry_attempts"]
        }
    
    def get_recent_sessions(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent processing sessions."""
        return self.metrics["sessions"][-limit:]
    
    def reset_metrics(self) -> None:
        """Reset all metrics (use with caution)."""
        self.metrics = {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "total_tokens_used": 0,
            "total_cost": 0.0,
            "average_response_time": 0.0,
            "schema_validation_failures": 0,
            "retry_attempts": 0,
            "test_cases_generated": 0,
            "test_cases_updated": 0,
            "sessions": []
        }
        self._save_metrics()
