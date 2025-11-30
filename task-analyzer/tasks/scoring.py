from datetime import datetime, date
from typing import List, Dict, Any, Set

class TaskScorer:
    """
    Priority scoring algorithm that balances multiple factors.
    
    The algorithm considers:
    - Urgency (days until due)
    - Importance (user rating)
    - Effort (estimated hours)
    - Dependencies (blocking other tasks)
    """
    
    def __init__(self, strategy='smart_balance'):
        self.strategy = strategy
        
    def calculate_priority_score(self, task: Dict[str, Any], 
                                 all_tasks: List[Dict[str, Any]] = None) -> float:
        """
        Calculate a priority score for a single task.
        Returns a score between 0-100 (higher = more urgent/important)
        """
        if self.strategy == 'fastest_wins':
            return self._fastest_wins_score(task)
        elif self.strategy == 'high_impact':
            return self._high_impact_score(task)
        elif self.strategy == 'deadline_driven':
            return self._deadline_driven_score(task)
        else:  # smart_balance
            return self._smart_balance_score(task, all_tasks or [])
    
    def _smart_balance_score(self, task: Dict[str, Any], 
                            all_tasks: List[Dict[str, Any]]) -> float:
        """
        Main algorithm that balances all factors intelligently.
        
        Scoring breakdown:
        - Urgency: 35% weight
        - Importance: 30% weight
        - Effort (inverse): 20% weight
        - Dependencies: 15% weight
        """
        urgency_score = self._calculate_urgency(task)
        importance_score = self._calculate_importance(task)
        effort_score = self._calculate_effort_score(task)
        dependency_score = self._calculate_dependency_score(task, all_tasks)
        
        # Weighted combination
        total_score = (
            urgency_score * 0.35 +
            importance_score * 0.30 +
            effort_score * 0.20 +
            dependency_score * 0.15
        )
        
        return round(total_score, 2)
    
    def _calculate_urgency(self, task: Dict[str, Any]) -> float:
        """
        Calculate urgency based on due date.
        Overdue tasks get maximum urgency.
        """
        due_date_str = task.get('due_date')
        if not due_date_str:
            return 50.0  # Neutral score for missing date
        
        try:
            if isinstance(due_date_str, str):
                due_date = datetime.strptime(due_date_str, '%Y-%m-%d').date()
            else:
                due_date = due_date_str
            
            today = date.today()
            days_until_due = (due_date - today).days
            
            # Overdue tasks
            if days_until_due < 0:
                # More overdue = higher urgency (caps at 100)
                return min(100.0, 100 + abs(days_until_due) * 5)
            
            # Due today
            if days_until_due == 0:
                return 95.0
            
            # Due within a week - high urgency
            if days_until_due <= 7:
                return 90 - (days_until_due * 5)
            
            # Due within 2 weeks - moderate urgency
            if days_until_due <= 14:
                return 60 - ((days_until_due - 7) * 3)
            
            # Due within a month - lower urgency
            if days_until_due <= 30:
                return 40 - ((days_until_due - 14) * 1.5)
            
            # Far future - minimal urgency
            return max(10.0, 40 - (days_until_due - 30) * 0.5)
            
        except (ValueError, TypeError):
            return 50.0  # Neutral score for invalid dates
    
    def _calculate_importance(self, task: Dict[str, Any]) -> float:
        """
        Convert importance (1-10) to 0-100 scale.
        """
        importance = task.get('importance', 5)
        
        # Validate importance
        if not isinstance(importance, (int, float)):
            return 50.0
        
        importance = max(1, min(10, importance))
        
        # Convert to 0-100 scale with slight curve favoring high importance
        return (importance ** 1.2) * 7.5
    
    def _calculate_effort_score(self, task: Dict[str, Any]) -> float:
        """
        Lower effort = higher score (quick wins).
        But not too aggressive - we don't want to ignore big important tasks.
        """
        estimated_hours = task.get('estimated_hours', 5)
        
        if not isinstance(estimated_hours, (int, float)) or estimated_hours <= 0:
            return 50.0
        
        # Quick tasks (< 2 hours) get a boost
        if estimated_hours <= 2:
            return 80.0
        
        # Medium tasks (2-8 hours)
        if estimated_hours <= 8:
            return 70 - (estimated_hours - 2) * 3
        
        # Longer tasks get lower scores but not too low
        return max(30.0, 50 - (estimated_hours - 8) * 2)
    
    def _calculate_dependency_score(self, task: Dict[str, Any], 
                                    all_tasks: List[Dict[str, Any]]) -> float:
        """
        Tasks that block other tasks should be prioritized.
        """
        task_id = task.get('id')
        if not task_id:
            return 50.0
        
        # Count how many other tasks depend on this one
        blocked_count = 0
        for other_task in all_tasks:
            dependencies = other_task.get('dependencies', [])
            if task_id in dependencies:
                blocked_count += 1
        
        # Score based on number of blocked tasks
        if blocked_count == 0:
            return 40.0
        elif blocked_count == 1:
            return 60.0
        elif blocked_count == 2:
            return 75.0
        else:
            return min(100.0, 75 + (blocked_count - 2) * 10)
    
    # Alternative scoring strategies
    
    def _fastest_wins_score(self, task: Dict[str, Any]) -> float:
        """Prioritize low-effort tasks."""
        effort = task.get('estimated_hours', 5)
        importance = task.get('importance', 5)
        
        # Heavy weight on low effort, but still consider importance
        effort_score = self._calculate_effort_score(task)
        importance_score = self._calculate_importance(task)
        
        return effort_score * 0.70 + importance_score * 0.30
    
    def _high_impact_score(self, task: Dict[str, Any]) -> float:
        """Prioritize importance above all."""
        importance_score = self._calculate_importance(task)
        urgency_score = self._calculate_urgency(task)
        
        return importance_score * 0.75 + urgency_score * 0.25
    
    def _deadline_driven_score(self, task: Dict[str, Any]) -> float:
        """Prioritize based on due dates."""
        urgency_score = self._calculate_urgency(task)
        importance_score = self._calculate_importance(task)
        
        return urgency_score * 0.80 + importance_score * 0.20
    
    def detect_circular_dependencies(self, tasks: List[Dict[str, Any]]) -> List[List[int]]:
        """
        Detect circular dependencies using depth-first search.
        Returns list of cycles found.
        """
        # Build dependency graph
        graph = {}
        for task in tasks:
            task_id = task.get('id')
            if task_id:
                graph[task_id] = task.get('dependencies', [])
        
        def dfs(node, visited, rec_stack, path):
            visited.add(node)
            rec_stack.add(node)
            path.append(node)
            
            for neighbor in graph.get(node, []):
                if neighbor not in visited:
                    cycle = dfs(neighbor, visited, rec_stack, path[:])
                    if cycle:
                        return cycle
                elif neighbor in rec_stack:
                    # Found a cycle
                    cycle_start = path.index(neighbor)
                    return path[cycle_start:] + [neighbor]
            
            rec_stack.remove(node)
            return None
        
        cycles = []
        visited = set()
        
        for task_id in graph.keys():
            if task_id not in visited:
                cycle = dfs(task_id, visited, set(), [])
                if cycle and cycle not in cycles:
                    cycles.append(cycle)
        
        return cycles
    
    def generate_explanation(self, task: Dict[str, Any], score: float) -> str:
        """Generate human-readable explanation for the score."""
        reasons = []
        
        # Check urgency
        due_date_str = task.get('due_date')
        if due_date_str:
            try:
                if isinstance(due_date_str, str):
                    due_date = datetime.strptime(due_date_str, '%Y-%m-%d').date()
                else:
                    due_date = due_date_str
                days_until = (due_date - date.today()).days
                
                if days_until < 0:
                    reasons.append(f"Overdue by {abs(days_until)} days")
                elif days_until == 0:
                    reasons.append("Due today")
                elif days_until <= 3:
                    reasons.append(f"Due in {days_until} days")
            except:
                pass
        
        # Check importance
        importance = task.get('importance', 5)
        if importance >= 8:
            reasons.append("High importance")
        
        # Check effort
        effort = task.get('estimated_hours', 0)
        if effort <= 2:
            reasons.append("Quick win")
        elif effort >= 10:
            reasons.append("Large task")
        
        if not reasons:
            reasons.append("Balanced priority")
        
        return " • ".join(reasons)