// API Configuration
const API_BASE_URL = 'http://127.0.0.1:8000/api/tasks';

// Global state
let tasks = [];
let taskIdCounter = 1;

// DOM Elements
const singleTaskForm = document.getElementById('singleTaskForm');
const jsonInput = document.getElementById('jsonInput');
const loadJsonBtn = document.getElementById('loadJsonBtn');
const analyzeBtn = document.getElementById('analyzeBtn');
const clearTasksBtn = document.getElementById('clearTasksBtn');
const taskList = document.getElementById('taskList');
const taskCount = document.getElementById('taskCount');
const outputSection = document.getElementById('outputSection');
const resultsContainer = document.getElementById('resultsContainer');
const loadingIndicator = document.getElementById('loadingIndicator');
const errorMessage = document.getElementById('errorMessage');
const strategySelect = document.getElementById('strategy');
const strategyUsed = document.getElementById('strategyUsed');
const totalTasks = document.getElementById('totalTasks');

// Event Listeners
singleTaskForm.addEventListener('submit', handleAddTask);
loadJsonBtn.addEventListener('click', handleLoadJson);
analyzeBtn.addEventListener('click', handleAnalyze);
clearTasksBtn.addEventListener('click', handleClearTasks);

// Add single task
function handleAddTask(e) {
    e.preventDefault();
    
    const title = document.getElementById('taskTitle').value.trim();
    const dueDate = document.getElementById('dueDate').value;
    const estimatedHours = parseFloat(document.getElementById('estimatedHours').value);
    const importance = parseInt(document.getElementById('importance').value);
    
    // Validation
    if (!title || !dueDate || !estimatedHours || !importance) {
        showError('Please fill in all required fields');
        return;
    }
    
    if (estimatedHours < 0.1) {
        showError('Estimated hours must be at least 0.1');
        return;
    }
    
    if (importance < 1 || importance > 10) {
        showError('Importance must be between 1 and 10');
        return;
    }
    
    const task = {
        id: taskIdCounter++,
        title,
        due_date: dueDate,
        estimated_hours: estimatedHours,
        importance,
        dependencies: []
    };
    
    tasks.push(task);
    updateTaskList();
    singleTaskForm.reset();
    hideError();
}

// Load tasks from JSON
function handleLoadJson() {
    try {
        const jsonData = jsonInput.value.trim();
        if (!jsonData) {
            showError('Please enter JSON data');
            return;
        }
        
        const parsedTasks = JSON.parse(jsonData);
        
        if (!Array.isArray(parsedTasks)) {
            showError('JSON must be an array of tasks');
            return;
        }
        
        // Validate and add IDs if missing
        parsedTasks.forEach((task, index) => {
            if (!task.id) {
                task.id = taskIdCounter++;
            }
            if (!task.dependencies) {
                task.dependencies = [];
            }
            
            // Basic validation
            if (!task.title || !task.due_date || !task.estimated_hours || !task.importance) {
                throw new Error(`Task at index ${index} is missing required fields`);
            }
        });
        
        tasks = [...tasks, ...parsedTasks];
        updateTaskList();
        jsonInput.value = '';
        hideError();
        
    } catch (error) {
        showError(`Invalid JSON: ${error.message}`);
    }
}

// Update task list display
function updateTaskList() {
    taskCount.textContent = tasks.length;
    
    if (tasks.length === 0) {
        taskList.innerHTML = '<p style="text-align: center; color: #666;">No tasks added yet</p>';
        analyzeBtn.disabled = true;
    } else {
        taskList.innerHTML = tasks.map((task, index) => `
            <div class="task-preview-item">
                <span><strong>${task.title}</strong> - Due: ${task.due_date} (${task.estimated_hours}h, Priority: ${task.importance}/10)</span>
                <button onclick="removeTask(${index})">Remove</button>
            </div>
        `).join('');
        analyzeBtn.disabled = false;
    }
}

// Remove task
function removeTask(index) {
    tasks.splice(index, 1);
    updateTaskList();
}

// Clear all tasks
function handleClearTasks() {
    if (tasks.length === 0) return;
    
    if (confirm('Are you sure you want to clear all tasks?')) {
        tasks = [];
        taskIdCounter = 1;
        updateTaskList();
        outputSection.style.display = 'none';
    }
}

// Analyze tasks
async function handleAnalyze() {
    if (tasks.length === 0) return;
    
    const strategy = strategySelect.value;
    
    // Show loading
    loadingIndicator.style.display = 'block';
    outputSection.style.display = 'none';
    hideError();
    
    try {
        const response = await fetch(`${API_BASE_URL}/analyze/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                tasks: tasks,
                strategy: strategy
            })
        });
        
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.error || 'Failed to analyze tasks');
        }
        
        displayResults(data);
        
    } catch (error) {
        showError(`Error: ${error.message}`);
    } finally {
        loadingIndicator.style.display = 'none';
    }
}

// Display results
function displayResults(data) {
    strategyUsed.textContent = data.strategy_used.replace('_', ' ').toUpperCase();
    totalTasks.textContent = data.total_tasks;
    
    resultsContainer.innerHTML = data.tasks.map((task, index) => {
        const priorityLevel = getPriorityLevel(task.priority_score);
        
        return `
            <div class="task-card priority-${priorityLevel}">
                <div class="task-header">
                    <div class="task-title">
                        #${index + 1} ${task.title}
                    </div>
                    <div class="priority-badge ${priorityLevel}">
                        ${task.priority_score.toFixed(2)}
                    </div>
                </div>
                
                <div class="task-details">
                    <div class="detail-item">
                        <div class="detail-label">Due Date</div>
                        <div class="detail-value">${formatDate(task.due_date)}</div>
                    </div>
                    <div class="detail-item">
                        <div class="detail-label">Estimated Time</div>
                        <div class="detail-value">${task.estimated_hours}h</div>
                    </div>
                    <div class="detail-item">
                        <div class="detail-label">Importance</div>
                        <div class="detail-value">${task.importance}/10</div>
                    </div>
                </div>
                
                <div class="task-explanation">
                    💡 ${task.explanation}
                </div>
                
                ${task.dependencies && task.dependencies.length > 0 ? `
                    <div style="margin-top: 10px; padding: 10px; background: #fff3cd; border-radius: 5px;">
                        ⚠️ Depends on tasks: ${task.dependencies.join(', ')}
                    </div>
                ` : ''}
            </div>
        `;
    }).join('');
    
    outputSection.style.display = 'block';
    outputSection.scrollIntoView({ behavior: 'smooth' });
}

// Helper functions
function getPriorityLevel(score) {
    if (score >= 75) return 'high';
    if (score >= 50) return 'medium';
    return 'low';
}

function formatDate(dateString) {
    const date = new Date(dateString);
    const today = new Date();
    today.setHours(0, 0, 0, 0);
    const taskDate = new Date(date);
    taskDate.setHours(0, 0, 0, 0);
    
    const diffTime = taskDate - today;
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    
    if (diffDays < 0) return `${Math.abs(diffDays)} days overdue`;
    if (diffDays === 0) return 'Due today';
    if (diffDays === 1) return 'Due tomorrow';
    return `${diffDays} days left`;
}

function showError(message) {
    errorMessage.textContent = message;
    errorMessage.style.display = 'block';
    setTimeout(() => {
        hideError();
    }, 5000);
}

function hideError() {
    errorMessage.style.display = 'none';
}

// Initialize
updateTaskList();