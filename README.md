#  Smart Task Analyzer

A web application that helps you prioritize your tasks intelligently. Instead of staring at your to-do list wondering "what should I do first?", this app does the thinking for you by analyzing multiple factors and giving each task a priority score.

**Built for:** Singularium Software Development Internship Assignment 2025

---

##  The Problem This Solves

We've all been there - you have 10 tasks on your plate, everything feels urgent, and you don't know where to start. Should you tackle that important project due next week, or knock out those quick tasks first? What about that task that's blocking your teammate?

This app takes the guesswork out by looking at your tasks from multiple angles and telling you exactly what deserves your attention right now.

---

### What It Does

**Input:** You give it your tasks with:
- What the task is
- When it's due
- How long it'll take
- How important you think it is
- What other tasks depend on it

**Output:** The app analyzes everything and gives you:
- A priority score for each task (0-100, higher = more urgent)
- Tasks sorted from "do this NOW" to "this can wait"
- An explanation for why each task got its score

Plus, you can switch between different prioritization strategies depending on your situation!

---

##  Getting Started

### What You Need
- Python 3.8 or newer
- A web browser
- 10 minutes to set it up

### Installation (Step by Step)

**1. Get the code**
```bash
git clone https://github.com/KeerthisreeJ/task-analyzer.git
cd task-analyzer
```

**2. Set up a clean Python environment**
```bash
# Create a virtual environment (keeps this project's stuff separate)
python -m venv venv

# Activate it
# On Windows:
venv\Scripts\activate
# On Mac/Linux:
source venv/bin/activate
```

**3. Install the required packages**
```bash
pip install -r requirements.txt
```

**4. Set up the database**
```bash
python manage.py makemigrations
python manage.py migrate
```

**5. Make sure everything works**
```bash
python manage.py test
```
You should see: "Ran 8 tests" with "OK" at the end.

**6. Start the server**
```bash
python manage.py runserver
```
The backend is now running at http://127.0.0.1:8000

**7. Open the frontend**

Option A (easiest): Just double-click `frontend/index.html`

Option B (better): Open a new terminal and run:
```bash
cd frontend
python -m http.server 8080
```
Then go to http://localhost:8080 in your browser.

---

##  How The Algorithm Works (The Interesting Part!)

Think of the algorithm as a hiring manager reviewing job candidates. Each candidate (task) gets evaluated on multiple criteria, each criterion gets a score, and then everything is weighted to produce a final ranking.

The default "Smart Balance" strategy looks at **four things**:

1. **How urgent is it?** (35% of the final score)
2. **How important is it?** (30% of the final score)
3. **How much effort does it take?** (20% of the final score)
4. **Is it blocking other tasks?** (15% of the final score)

Let me break down each one:

---

### 1. Urgency Score (35% weight)

**What it measures:** How soon is this task due?

**The thinking:** Time doesn't stop. A task due tomorrow is objectively more urgent than one due next month, regardless of how important it is.

**How it's calculated:**

- **Overdue tasks** → Get the maximum urgency score (100+)
  - The logic: If it's already late, it needed to be done yesterday. For every day it's overdue, we add even more urgency.
  - Example: A task that's 3 days overdue gets a score of 115 (100 + 3×5)

- **Due today** → 95/100
  - The logic: If it's not done by end of day, it becomes overdue. Super urgent.

- **Due within a week** → Starts at 90, drops by 5 points per day
  - Day 1: 90, Day 2: 85, Day 3: 80, etc.
  - The logic: There's still urgency, but each extra day gives a little breathing room.

- **Due within two weeks** → 60-39 range
  - The logic: It's on the horizon but not immediate. You need to start thinking about it.

- **Due within a month** → 40-16 range
  - The logic: It's coming up but there's time to plan.

- **Due more than a month away** → Below 16, gradually decreasing
  - The logic: It's far enough that other things should probably come first, but it doesn't completely disappear from consideration.

**Why 35%?** Urgency is the most objective factor - deadlines don't care about your opinion. But it's not everything (that would just make you a deadline-driven robot).

---

### 2. Importance Score (30% weight)

**What it measures:** How much does this task actually matter?

**The thinking:** Some tasks are just more important than others. Fixing a critical bug that's crashing your app matters more than updating documentation (even if both are due tomorrow).

**How it's calculated:**

You rate each task on a scale of 1-10 based on your judgment. The algorithm takes that rating and converts it to a 0-100 scale, but with a twist - it uses an exponential curve.

Here's what that means in plain English:
- A task rated 5/10 gets about 42 points
- A task rated 8/10 gets about 69 points  
- A task rated 10/10 gets about 75 points

**The formula:** `(importance^1.2) × 7.5`

**Why the curve?** Without it, a task rated 8 would be literally twice as important as one rated 4. But in real life, that 8/10 task might be *significantly* more critical than a 7/10 task. The exponential curve captures that - the difference between 9 and 10 matters more than the difference between 4 and 5.

**Why 30%?** This is where your human judgment comes in. You know your work better than any algorithm. But we balance it with other factors because humans can be biased (we might overestimate importance of things we enjoy).

---

### 3. Effort Score (20% weight)

**What it measures:** How long will this take?

**The thinking:** Quick wins are valuable. Sometimes the best task to do right now is the one you can finish in an hour, because:
- You'll get it off your plate
- You'll build momentum
- You won't have it hanging over your head

But we can't *only* focus on quick tasks, or you'd never tackle the big important projects.

**How it's calculated:**

- **Quick tasks (under 2 hours)** → 80/100
  - The logic: These are your quick wins. Do a few of these and you'll clear your backlog fast.

- **Medium tasks (2-8 hours)** → 70 down to 46
  - The logic: Substantial but doable. Not too scary to start.
  - A 2-hour task gets 70, a 5-hour task gets about 61, an 8-hour task gets 46.

- **Large tasks (over 8 hours)** → 30 and above
  - The logic: These are your big projects. They still matter (hence why they don't score zero), but they're not as tempting to start right now.

**Why 20%?** Effort matters, but it shouldn't dominate. If we weighted this too highly, you'd become a "quick task junkie" and never do deep work.

---

### 4. Dependency Score (15% weight)

**What it measures:** How many other tasks are waiting on this one?

**The thinking:** If three people are blocked waiting for you to finish something, that something just became way more important. You're the bottleneck.

**How it's calculated:**

The algorithm looks at all your tasks and asks: "How many tasks list THIS task as a dependency?"

- **Blocks 0 tasks** → 40/100 (baseline score)
  - The logic: It's standalone. Important, but not urgent from a workflow perspective.

- **Blocks 1 task** → 60/100
  - The logic: Someone's waiting on you. You should probably prioritize this.

- **Blocks 2 tasks** → 75/100
  - The logic: Multiple people/tasks are stuck. This is becoming a real bottleneck.

- **Blocks 3+ tasks** → 75-100
  - The logic: Critical blocker. Everything's waiting on this. Drop what you're doing.

**Bonus feature:** The algorithm also *detects circular dependencies*. If Task A depends on Task B, and Task B depends on Task A, that's impossible! The app will catch this and tell you before trying to score anything.

**Why 15%?** Dependencies matter for team workflow, but not everyone works on a team, and not all tasks have dependencies. So it's the smallest weight, but still significant when it applies.

---

### Putting It All Together

Here's an example with actual numbers:

**Task:** "Fix critical login bug"
- Due: 2 days ago (overdue!)
- Importance: 9/10
- Estimated effort: 3 hours
- Blocks: 2 other tasks

**The calculation:**

1. **Urgency:** Overdue by 2 days → Score = 110 (maxed out)
2. **Importance:** 9/10 → Score = 72 (using the exponential curve)
3. **Effort:** 3 hours → Score = 67 (in the "medium" range)
4. **Dependencies:** Blocks 2 tasks → Score = 75

**Final Score:**
```
(110 × 0.35) + (72 × 0.30) + (67 × 0.20) + (75 × 0.15)
= 38.5 + 21.6 + 13.4 + 11.25
= 84.75
```

**Result:** This task scores 84.75/100 - definitely something you should be working on right now!

---

##  Different Strategies (Because One Size Doesn't Fit All)

The "Smart Balance" approach works great most of the time, but sometimes your situation calls for a different strategy. That's why the app lets you switch between four different approaches:

### Strategy 1: Smart Balance (Default)
**Weights:** Urgency 35% | Importance 30% | Effort 20% | Dependencies 15%

**Use this when:** You want a well-rounded approach that considers everything.

**Best for:** Day-to-day work, normal circumstances.

---

### Strategy 2: Fastest Wins
**Weights:** Effort 70% | Importance 30%

**Use this when:** 
- You're feeling overwhelmed and need to build momentum
- Your to-do list is getting really long
- You want to clear your backlog
- It's Friday afternoon and you want to finish strong

**What it does:** Heavily favors quick tasks. A 1-hour task will almost always rank higher than a 5-hour task, even if the 5-hour task is more important.

**The psychology:** Checking things off feels good. Sometimes you need that psychological boost of completing tasks to get your motivation back.

---

### Strategy 3: High Impact
**Weights:** Importance 75% | Urgency 25%

**Use this when:**
- You have flexible deadlines
- You're doing strategic work
- Quality matters more than speed
- You want to focus on what truly matters

**What it does:** Almost completely ignores effort and dependencies. If you rated something 10/10 importance, it's going to the top, period.

**The philosophy:** "First things first." Do the important stuff, and everything else will fall into place.

---

### Strategy 4: Deadline Driven
**Weights:** Urgency 80% | Importance 20%

**Use this when:**
- You're in crunch time
- Everything has hard deadlines
- You're working on client projects with contracts
- Missing deadlines has serious consequences

**What it does:** Basically sorts by due date. If it's due sooner, it ranks higher. Importance gets a small say, but not much.

**The reality:** Sometimes you just need to hit deadlines, even if it means doing less important tasks first.

---

##  How It Handles Edge Cases

Good software doesn't break when you give it weird input. Here's what happens when things go wrong:

### Missing Information
**Problem:** What if a task doesn't have a due date?
**Solution:** The algorithm gives it a neutral urgency score (50/100). It won't be first, but it won't be last either.

**Problem:** What if estimated hours is missing or zero?
**Solution:** Defaults to a neutral effort score (50/100).

### Invalid Data
**Problem:** What if someone enters importance as 15 (but max is 10)?
**Solution:** The algorithm clamps it to 10. Same for negative numbers - they get bumped up to 1.

**Problem:** What if the due date format is wrong?
**Solution:** Catches the error gracefully and uses neutral scores instead of crashing.

### Circular Dependencies
**Problem:** Task A depends on Task B, Task B depends on Task C, Task C depends on Task A. This is impossible!
**Solution:** Before calculating any scores, the algorithm runs a check using depth-first search. If it finds a cycle, it stops and shows you exactly which tasks are in the loop.

**Example error message:**
```json
{
  "error": "Circular dependencies detected",
  "cycles": [[1, 2, 3, 1]]
}
```
Translation: Tasks 1 → 2 → 3 → 1 form an impossible loop.

---

##  Design Decisions I Made (And Why)

### Backend: Why Django?

I chose Django because:
- **It's batteries-included:** Built-in validation, ORM, testing framework
- **Django REST Framework:** Makes building APIs incredibly easy
- **It's production-ready:** If this were a real product, Django could scale

**Trade-off:** It's a bit heavyweight for a simple app like this. But the time saved on setup and validation made it worth it.

### Frontend: Why Vanilla JavaScript?

I didn't use React, Vue, or any framework because:
- **It's simpler:** For an app this size, a framework would be overkill
- **It's faster to build:** No setup, no build process, just write code
- **It's more transparent:** Easy to see exactly what's happening

**Trade-off:** If this app grew to 20+ features, I'd refactor to React. But for now, vanilla JS is cleaner.

### Algorithm: Why Weighted Linear Combination?

I could have used machine learning to learn user preferences. But I chose a transparent mathematical formula because:
- **It's explainable:** You can see exactly why a task got its score
- **It's predictable:** Same inputs always give same outputs
- **It doesn't need training data:** Works immediately

**Trade-off:** It doesn't learn from your behavior. A more advanced version could adjust weights based on which suggestions you actually follow.

### No Database Persistence

Currently, tasks aren't saved between sessions. Everything's in memory.

**Why I did this:** The assignment focused on the algorithm, not building a full CRUD app. Adding persistence would have taken time away from perfecting the scoring logic.

**What I'd add with more time:** User accounts, task history, ability to mark tasks complete, and the algorithm could learn from your patterns.

---

##  Testing

I wrote 8 unit tests covering:

 **Overdue tasks get high urgency** - Verified that overdue tasks score 95+  
 **High importance tasks score well** - Importance 10/10 gives 80+ points  
 **Quick wins are identified** - Tasks under 2 hours get 70+ effort score  
 **Circular dependencies are caught** - A→B→C→A triggers an error  
 **Invalid data doesn't crash** - Missing fields default to neutral scores  
 **Blocking tasks get boosted** - Tasks blocking 2+ others score 75+  
 **Strategies work differently** - Same task scores differently in each strategy  
 **All scoring components work** - Each factor (urgency, importance, etc.) calculates correctly  

**Run the tests:**
```bash
python manage.py test
```

**Expected output:**
```
Ran 8 tests in 0.015s
OK
```

---

##  API Documentation (For Technical Users)

### Endpoint 1: Analyze Tasks

**POST** `/api/tasks/analyze/`

Sends your tasks, gets back sorted results with scores.

**Request:**
```json
{
  "tasks": [
    {
      "title": "Fix login bug",
      "due_date": "2025-12-01",
      "estimated_hours": 3,
      "importance": 8,
      "dependencies": []
    },
    {
      "title": "Write docs",
      "due_date": "2025-12-10",
      "estimated_hours": 1,
      "importance": 5,
      "dependencies": [1]
    }
  ],
  "strategy": "smart_balance"
}
```

**Response:**
```json
{
  "tasks": [
    {
      "id": 1,
      "title": "Fix login bug",
      "due_date": "2025-12-01",
      "estimated_hours": 3,
      "importance": 8,
      "dependencies": [],
      "priority_score": 78.45,
      "explanation": "Due in 1 days • High importance"
    },
    {
      "id": 2,
      "title": "Write docs",
      "due_date": "2025-12-10",
      "estimated_hours": 1,
      "importance": 5,
      "dependencies": [1],
      "priority_score": 65.20,
      "explanation": "Quick win"
    }
  ],
  "strategy_used": "smart_balance",
  "total_tasks": 2
}
```

### Endpoint 2: Get Suggestions

**GET** `/api/tasks/suggest/`

Currently a placeholder - would return top 3 tasks with detailed reasoning.

---

##  Time Breakdown

**Total time:** ~4.5 hours

- **Backend (2.5 hours)**
  - Django setup & configuration: 20 min
  - Task model & serializers: 25 min
  - Scoring algorithm: 1 hour (the core logic)
  - API views & error handling: 30 min
  - Writing tests: 35 min

- **Frontend (1.5 hours)**
  - HTML structure: 25 min
  - CSS styling (responsive design): 40 min
  - JavaScript (API calls, UI updates): 25 min

- **Documentation (30 min)**
  - README (this file): 30 min

---


##  Project Structure
```
task-analyzer/
│
├── manage.py                    # Django management script
├── requirements.txt             # Python dependencies
├── README.md                    # You are here!
│
├── task_analyzer/               # Django project settings
│   ├── settings.py              # Configuration (database, apps, etc.)
│   ├── urls.py                  # Main URL routing
│   └── wsgi.py                  # Web server interface
│
├── tasks/                       # Main application
│   ├── models.py                # Task data model (structure)
│   ├── views.py                 # API endpoints (analyze, suggest)
│   ├── serializers.py           # Data validation & conversion
│   ├── scoring.py               # THE HEART: Priority algorithm
│   ├── urls.py                  # App-specific URL routing
│   ├── tests.py                 # Unit tests (8 tests)
│   └── migrations/              # Database version control
│
└── frontend/                    # User interface
    ├── index.html               # Main page structure
    ├── styles.css               # All the styling
    └── script.js                # Frontend logic & API calls
```

---

##  Tech Stack

**Backend:**
- Python 3.8+ (the brain)
- Django 4.2+ (the framework)
- Django REST Framework (API magic)
- django-cors-headers (lets frontend talk to backend)

**Frontend:**
- HTML5 (structure)
- CSS3 (makes it pretty - Flexbox & Grid)
- Vanilla JavaScript (no frameworks, just pure JS)
- Fetch API (talks to backend)

**Testing:**
- Django's built-in test framework
- Python unittest library

---

##  Known Limitations

**1. No data persistence:** Tasks disappear when you refresh the page. This was intentional to focus on the algorithm, but obviously a real app would need to save data.

**2. No authentication:** Anyone can use the app. No user accounts, no privacy, no security. Fine for a demo, not for production.

**3. Limited error messages:** Some errors could be more user-friendly. For example, if the API is down, it just says "Error" instead of "Can't connect to server."

**4. No task editing:** You can add tasks and analyze them, but you can't edit or delete individual tasks (except clearing everything).

**5. Strategies are hardcoded:** The four strategies have fixed weights. In a real product, users might want to customize the weights themselves.

---

##  Lessons Learned

### What Went Well
- **Algorithm design:** Starting with the math on paper before coding made implementation smooth
- **Testing first:** Writing tests as I built features caught bugs early
- **Separation of concerns:** Keeping scoring.py separate from Django made it super testable
- **Multiple strategies:** This was a late addition but it really showcases the algorithm's flexibility

### What I'd Do Differently
- **More visual feedback:** The results could use charts or graphs
- **Better mobile experience:** It works on mobile, but it could be better optimized
- **Weighted example calculator:** A tool showing "if you change this weight, here's what happens"

### Biggest Challenge
Getting the dependency detection right. Circular dependencies are tricky! I initially tried a simple approach that missed edge cases, then switched to proper depth-first search which works reliably.

---

##  Contributing (Hypothetically)

If this were an open-source project, here's how I'd want contributions:

1. **Fork the repo**
2. **Create a feature branch:** `git checkout -b feature/amazing-feature`
3. **Write tests for your feature**
4. **Make your changes**
5. **Ensure all tests pass:** `python manage.py test`
6. **Commit:** `git commit -m "Add amazing feature"`
7. **Push:** `git push origin feature/amazing-feature`
8. **Open a Pull Request**

---

##  Contact

**Built by:** Keerthisree J  
**For:** Singularium Internship Assignment 2025  
**GitHub:** https://github.com/KeerthisreeJ/task-analyzer

---

## 📄 License

This project was created as part of an internship assignment. Feel free to learn from it, but please don't submit it as your own work for the same assignment! 

---

##  Acknowledgments

- Thanks to the Singularium team for a thoughtful assignment that tests real problem-solving skills
- The Django and DRF communities for excellent documentation

---

**Final thought:** Priority is not about doing everything. It's about doing the right things at the right time. I hope this tool helps you figure out what "right" means for you. 🎯

---

*Last updated: November 30, 2025*
