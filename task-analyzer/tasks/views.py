from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .scoring import TaskScorer
from .serializers import TaskAnalysisSerializer, TaskWithScoreSerializer

@api_view(['POST'])
def analyze_tasks(request):
    """
    Analyze and sort tasks by priority score.
    
    Expected input:
    {
        "tasks": [...],
        "strategy": "smart_balance"  // optional
    }
    """
    try:
        serializer = TaskAnalysisSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        tasks_data = serializer.validated_data['tasks']
        strategy = serializer.validated_data.get('strategy', 'smart_balance')
        
        # Convert to list of dicts for scoring
        tasks_list = []
        for i, task_data in enumerate(tasks_data):
            task_dict = {
                'id': task_data.get('id', i + 1),
                'title': task_data['title'],
                'due_date': task_data['due_date'],
                'estimated_hours': task_data['estimated_hours'],
                'importance': task_data['importance'],
                'dependencies': task_data.get('dependencies', [])
            }
            tasks_list.append(task_dict)
        
        # Initialize scorer with strategy
        scorer = TaskScorer(strategy=strategy)
        
        # Check for circular dependencies
        cycles = scorer.detect_circular_dependencies(tasks_list)
        if cycles:
            return Response({
                'error': 'Circular dependencies detected',
                'cycles': cycles
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Calculate scores
        scored_tasks = []
        for task in tasks_list:
            score = scorer.calculate_priority_score(task, tasks_list)
            explanation = scorer.generate_explanation(task, score)
            
            scored_tasks.append({
                **task,
                'priority_score': score,
                'explanation': explanation
            })
        
        # Sort by score (highest first)
        scored_tasks.sort(key=lambda x: x['priority_score'], reverse=True)
        
        return Response({
            'tasks': scored_tasks,
            'strategy_used': strategy,
            'total_tasks': len(scored_tasks)
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def suggest_tasks(request):
    """
    Suggest top 3 tasks to work on today.
    
    Can optionally accept a strategy query parameter.
    """
    try:
        # For this demo, we'll accept tasks via query params or use sample data
        strategy = request.query_params.get('strategy', 'smart_balance')
        
        # In a real app, you'd fetch from database
        # For now, return helpful message
        return Response({
            'message': 'Submit tasks via POST to /api/tasks/analyze/ to get suggestions',
            'strategy': strategy
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# Create your views here.
