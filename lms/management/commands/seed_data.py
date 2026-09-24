"""
UnivLMS Comprehensive Database Seeder
Produces a rich, realistic dataset: 10+ users, 4 courses, 
complete curriculum, graded submissions, and audit trail.
"""
import os
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from accounts.models import User
from lms.models import Course, Module, Lesson, Enrollment, Assignment, Submission, AuditLog


class Command(BaseCommand):
    help = "Seed UnivLMS with a full, realistic production-like dataset."

    def handle(self, *args, **options):
        # Configure stdout for utf-8 on Windows
        import sys
        if hasattr(sys.stdout, 'reconfigure'):
            sys.stdout.reconfigure(encoding='utf-8', errors='replace')

        self.stdout.write(self.style.NOTICE("=" * 60))
        self.stdout.write(self.style.NOTICE("  Seeding UnivLMS - Full Production Dataset"))
        self.stdout.write(self.style.NOTICE("=" * 60))

        now = timezone.now()

        # =========================================================
        # 1. USERS  ─ admin + 3 faculty + 10 students
        # =========================================================
        self.stdout.write(self.style.HTTP_INFO("\n[1/7] Creating Users..."))

        admin, _ = User.objects.get_or_create(
            username='admin_root',
            defaults={
                'email': 'admin@univ.edu', 'first_name': 'Eleanor', 'last_name': 'Vance',
                'role': User.Role.ADMIN, 'academic_id': 'ADM-001',
                'is_staff': True, 'is_superuser': True,
            }
        )
        admin.set_password('Admin@12345'); admin.save()

        fac_smith, _ = User.objects.get_or_create(
            username='prof_smith',
            defaults={
                'email': 'smith@univ.edu', 'first_name': 'Alan', 'last_name': 'Smith',
                'role': User.Role.INSTRUCTOR, 'academic_id': 'FAC-101', 'is_staff': True,
            }
        )
        fac_smith.set_password('Faculty@12345'); fac_smith.save()

        fac_chen, _ = User.objects.get_or_create(
            username='dr_chen',
            defaults={
                'email': 'chen@univ.edu', 'first_name': 'Elena', 'last_name': 'Chen',
                'role': User.Role.INSTRUCTOR, 'academic_id': 'FAC-102', 'is_staff': True,
            }
        )
        fac_chen.set_password('Faculty@12345'); fac_chen.save()

        fac_morgan, _ = User.objects.get_or_create(
            username='prof_morgan',
            defaults={
                'email': 'morgan@univ.edu', 'first_name': 'James', 'last_name': 'Morgan',
                'role': User.Role.INSTRUCTOR, 'academic_id': 'FAC-103', 'is_staff': True,
            }
        )
        fac_morgan.set_password('Faculty@12345'); fac_morgan.save()

        # 10 Students
        student_data = [
            ('john_doe',     'john@univ.edu',    'John',    'Doe',       'STU-901'),
            ('sarah_connor', 'sarah@univ.edu',   'Sarah',   'Connor',    'STU-902'),
            ('mike_ross',    'mike@univ.edu',    'Mike',    'Ross',      'STU-903'),
            ('alice_wu',     'alice@univ.edu',   'Alice',   'Wu',        'STU-904'),
            ('bob_miller',   'bob@univ.edu',     'Bob',     'Miller',    'STU-905'),
            ('priya_sharma', 'priya@univ.edu',   'Priya',   'Sharma',    'STU-906'),
            ('liam_nguyen',  'liam@univ.edu',    'Liam',    'Nguyen',    'STU-907'),
            ('emma_jones',   'emma@univ.edu',    'Emma',    'Jones',     'STU-908'),
            ('carlos_perez', 'carlos@univ.edu',  'Carlos',  'Perez',     'STU-909'),
            ('nina_patel',   'nina@univ.edu',    'Nina',    'Patel',     'STU-910'),
        ]
        students = []
        for uname, email, fn, ln, aid in student_data:
            s, _ = User.objects.get_or_create(
                username=uname,
                defaults={'email': email, 'first_name': fn, 'last_name': ln,
                          'role': User.Role.STUDENT, 'academic_id': aid}
            )
            s.set_password('Student@12345'); s.save()
            students.append(s)

        self.stdout.write(self.style.SUCCESS(
            f"  ✓ {2 + len(students) + 3} users ready (1 admin, 3 faculty, {len(students)} students)"
        ))

        # =========================================================
        # 2. COURSES
        # =========================================================
        self.stdout.write(self.style.HTTP_INFO("\n[2/7] Creating Courses..."))

        cs101, _ = Course.objects.get_or_create(
            course_code='CS-101',
            defaults={
                'title': 'Introduction to Computer Science',
                'department': 'Computer Science Department',
                'credit_count': 3,
                'instructor': fac_smith,
                'syllabus_outline': (
                    "# CS-101: Introduction to Computer Science\n\n"
                    "**Semester:** Fall 2026 · **Credits:** 3 · **Format:** Hybrid\n\n"
                    "This foundational course equips students with algorithmic thinking, "
                    "structured programming in Python, object-oriented design patterns, "
                    "and foundational data structures.\n\n"
                    "## Learning Outcomes\n"
                    "1. Write, test, and debug Python programs up to 1,000 LOC\n"
                    "2. Analyse time and space complexity using Big-O notation\n"
                    "3. Design class hierarchies using OOP principles\n"
                    "4. Implement linear and non-linear data structures from scratch\n\n"
                    "## Grading Breakdown\n"
                    "| Component | Weight |\n"
                    "|-----------|--------|\n"
                    "| Programming Labs (×4) | 30% |\n"
                    "| Midterm Examination | 30% |\n"
                    "| Capstone Project | 40% |\n\n"
                    "**Office Hours:** Mon/Wed 2–4 PM · Room CS-307\n"
                    "**Prerequisite:** None (introductory course)"
                ),
                'is_active': True,
            }
        )

        ds201, _ = Course.objects.get_or_create(
            course_code='DS-201',
            defaults={
                'title': 'Applied Data Science & Machine Learning',
                'department': 'Artificial Intelligence & Data Systems',
                'credit_count': 4,
                'instructor': fac_smith,
                'syllabus_outline': (
                    "# DS-201: Applied Data Science & Machine Learning\n\n"
                    "**Semester:** Fall 2026 · **Credits:** 4 · **Format:** In-person\n\n"
                    "From raw data pipelines to deployed ML models — master the full "
                    "data science workflow with pandas, scikit-learn, and PyTorch.\n\n"
                    "## Learning Outcomes\n"
                    "1. Build and clean production-grade data pipelines\n"
                    "2. Apply supervised and unsupervised ML algorithms\n"
                    "3. Train, tune, and evaluate neural networks with PyTorch\n"
                    "4. Communicate findings through data visualization\n\n"
                    "## Grading Breakdown\n"
                    "| Component | Weight |\n"
                    "|-----------|--------|\n"
                    "| Weekly Notebooks (×8) | 25% |\n"
                    "| Midterm Project | 25% |\n"
                    "| Kaggle Competition | 20% |\n"
                    "| Final Research Report | 30% |\n\n"
                    "**Prerequisite:** CS-101 or equivalent Python fluency"
                ),
                'is_active': True,
            }
        )

        ux301, _ = Course.objects.get_or_create(
            course_code='UX-301',
            defaults={
                'title': 'Modern UI/UX Design & Human Factors',
                'department': 'Design & Interactive Media',
                'credit_count': 3,
                'instructor': fac_chen,
                'syllabus_outline': (
                    "# UX-301: Modern UI/UX Design & Human Factors\n\n"
                    "**Semester:** Fall 2026 · **Credits:** 3 · **Format:** Studio\n\n"
                    "Master the full design lifecycle from research to prototype to handoff, "
                    "using Figma, design systems, WCAG accessibility, and micro-animation.\n\n"
                    "## Learning Outcomes\n"
                    "1. Conduct user research and synthesise insights into personas\n"
                    "2. Produce high-fidelity prototypes in Figma\n"
                    "3. Apply WCAG 2.1 AA accessibility guidelines\n"
                    "4. Build and document a complete design system\n\n"
                    "## Grading Breakdown\n"
                    "| Component | Weight |\n"
                    "|-----------|--------|\n"
                    "| Weekly Design Crits | 20% |\n"
                    "| Mid-semester Case Study | 30% |\n"
                    "| Final Design System Portfolio | 50% |\n\n"
                    "**Prerequisite:** None (design enthusiasm welcome!)"
                ),
                'is_active': True,
            }
        )

        sec401, _ = Course.objects.get_or_create(
            course_code='SEC-401',
            defaults={
                'title': 'Enterprise Cybersecurity & Threat Defense',
                'department': 'Information Security Department',
                'credit_count': 4,
                'instructor': fac_morgan,
                'syllabus_outline': (
                    "# SEC-401: Enterprise Cybersecurity & Threat Defense\n\n"
                    "**Semester:** Fall 2026 · **Credits:** 4 · **Format:** Lab-intensive\n\n"
                    "Zero-trust architectures, adversarial modelling, penetration testing "
                    "methodologies, cryptography, and the OWASP Top 10 — built for aspiring "
                    "security engineers.\n\n"
                    "## Learning Outcomes\n"
                    "1. Design zero-trust network architectures\n"
                    "2. Perform structured penetration tests using industry tools\n"
                    "3. Implement cryptographic protocols and key management\n"
                    "4. Respond to simulated incident scenarios\n\n"
                    "## Grading Breakdown\n"
                    "| Component | Weight |\n"
                    "|-----------|--------|\n"
                    "| CTF Challenges (×4) | 40% |\n"
                    "| Midterm Pen-Test Report | 25% |\n"
                    "| Final Architecture Presentation | 35% |\n\n"
                    "**Prerequisite:** Networking fundamentals or instructor approval"
                ),
                'is_active': True,
            }
        )

        self.stdout.write(self.style.SUCCESS("  ✓ 4 courses ready (CS-101, DS-201, UX-301, SEC-401)"))

        # =========================================================
        # 3. MODULES & LESSONS
        # =========================================================
        self.stdout.write(self.style.HTTP_INFO("\n[3/7] Building Curriculum (Modules & Lessons)..."))

        # --- CS-101 ---
        m1_cs, _ = Module.objects.get_or_create(
            course=cs101, title='Foundations & Algorithmic Thinking', defaults={'order_index': 1}
        )
        Lesson.objects.get_or_create(
            module=m1_cs, title='Course Orientation & Python Environment Setup', defaults={
                'order_index': 1,
                'content_markdown': (
                    "# Welcome to CS-101\n\n"
                    "In this opening lecture we establish our computational thinking mindset "
                    "and configure our local runtime environment.\n\n"
                    "## What You'll Need\n"
                    "- Python 3.11+ (download from python.org)\n"
                    "- VS Code with the Python extension\n"
                    "- `pip` package manager\n\n"
                    "## Your First Script\n\n"
                    "```python\n"
                    "def greet_scholar(name: str) -> str:\n"
                    "    \"\"\"Return a personalised welcome message.\"\"\"\n"
                    "    return f'Welcome to UnivLMS, {name}! Let the discovery begin.'\n\n"
                    "if __name__ == '__main__':\n"
                    "    print(greet_scholar('Future Engineer'))\n"
                    "```\n\n"
                    "## Setting Up a Virtual Environment\n\n"
                    "```bash\n"
                    "# Create and activate\n"
                    "python -m venv .venv\n"
                    "source .venv/bin/activate   # macOS/Linux\n"
                    ".venv\\Scripts\\activate      # Windows\n\n"
                    "# Install dependencies\n"
                    "pip install -r requirements.txt\n"
                    "```\n\n"
                    "> **Note:** Always activate your virtual environment before working on any project!\n\n"
                    "## Learning Objectives\n"
                    "1. Understand the compiler vs interpreter distinction.\n"
                    "2. Configure virtual environments and manage dependencies.\n"
                    "3. Write, debug, and run your first Python program.\n"
                )
            }
        )
        Lesson.objects.get_or_create(
            module=m1_cs, title='Control Flow, Loops & Invariants', defaults={
                'order_index': 2,
                'content_markdown': (
                    "## Algorithmic Control Flow\n\n"
                    "Structured programming has three fundamental control mechanisms:\n\n"
                    "| Mechanism | Keyword | Purpose |\n"
                    "|-----------|---------|----------|\n"
                    "| Sequence | (none) | Linear instruction ordering |\n"
                    "| Selection | `if / elif / else` | Branch on a boolean condition |\n"
                    "| Iteration | `for / while` | Repeat a block of code |\n\n"
                    "## While Loop Example\n\n"
                    "```python\n"
                    "# Collatz conjecture – demonstrating loop invariants\n"
                    "def collatz(n: int) -> int:\n"
                    "    steps = 0\n"
                    "    while n != 1:   # loop invariant: n > 0\n"
                    "        n = n // 2 if n % 2 == 0 else 3 * n + 1\n"
                    "        steps += 1\n"
                    "    return steps\n\n"
                    "print(f'Steps to 1 from 27: {collatz(27)}')\n"
                    "```\n\n"
                    "## For Loop with Enumerate\n\n"
                    "```python\n"
                    "fruits = ['apple', 'banana', 'cherry']\n"
                    "for i, fruit in enumerate(fruits, start=1):\n"
                    "    print(f'{i}. {fruit.title()}')\n"
                    "```\n\n"
                    "Always monitor your **loop invariant** to guarantee termination!\n"
                )
            }
        )
        Lesson.objects.get_or_create(
            module=m1_cs, title='Functions, Recursion & Big-O Analysis', defaults={
                'order_index': 3,
                'content_markdown': (
                    "## Functions as First-Class Citizens\n\n"
                    "In Python, functions are objects — they can be passed as arguments, "
                    "returned from other functions, and stored in variables.\n\n"
                    "```python\n"
                    "def factorial(n: int) -> int:\n"
                    "    \"\"\"O(n) time, O(n) stack space (recursive).\"\"\"\n"
                    "    if n <= 1:\n"
                    "        return 1\n"
                    "    return n * factorial(n - 1)\n\n"
                    "# Higher-order function\n"
                    "def apply(func, value):\n"
                    "    return func(value)\n\n"
                    "print(apply(factorial, 6))  # → 720\n"
                    "```\n\n"
                    "## Big-O Complexity\n\n"
                    "| Complexity | Name | Example |\n"
                    "|------------|------|---------|\n"
                    "| O(1) | Constant | Array index lookup |\n"
                    "| O(log n) | Logarithmic | Binary search |\n"
                    "| O(n) | Linear | Linear scan |\n"
                    "| O(n log n) | Linearithmic | Merge sort |\n"
                    "| O(n²) | Quadratic | Bubble sort |\n"
                )
            }
        )

        m2_cs, _ = Module.objects.get_or_create(
            course=cs101, title='Object-Oriented Architecture', defaults={'order_index': 2}
        )
        Lesson.objects.get_or_create(
            module=m2_cs, title='Classes, Encapsulation & Abstraction', defaults={
                'order_index': 1,
                'content_markdown': (
                    "## Designing with Objects\n\n"
                    "Encapsulation groups **state** and **behaviour** together, "
                    "hiding internal representation behind a clean public interface.\n\n"
                    "```python\n"
                    "class BankAccount:\n"
                    "    def __init__(self, owner: str, balance: float = 0.0):\n"
                    "        self.owner = owner\n"
                    "        self._balance = balance  # private by convention\n\n"
                    "    @property\n"
                    "    def balance(self) -> float:\n"
                    "        return self._balance\n\n"
                    "    def deposit(self, amount: float) -> None:\n"
                    "        if amount <= 0:\n"
                    "            raise ValueError('Deposit must be positive')\n"
                    "        self._balance += amount\n\n"
                    "    def withdraw(self, amount: float) -> bool:\n"
                    "        if amount > self._balance:\n"
                    "            return False\n"
                    "        self._balance -= amount\n"
                    "        return True\n\n"
                    "    def __repr__(self) -> str:\n"
                    "        return f'BankAccount({self.owner!r}, ${self._balance:.2f})'\n"
                    "```\n\n"
                    "## The Four Pillars of OOP\n\n"
                    "1. **Encapsulation** – bundle state + behaviour, hide internals\n"
                    "2. **Abstraction** – expose only what's necessary\n"
                    "3. **Inheritance** – share behaviour through class hierarchies\n"
                    "4. **Polymorphism** – same interface, different implementations\n"
                )
            }
        )
        Lesson.objects.get_or_create(
            module=m2_cs, title='Inheritance, Polymorphism & SOLID Principles', defaults={
                'order_index': 2,
                'content_markdown': (
                    "## Inheritance & Method Overriding\n\n"
                    "```python\n"
                    "class Shape:\n"
                    "    def area(self) -> float:\n"
                    "        raise NotImplementedError\n\n"
                    "    def describe(self) -> str:\n"
                    "        return f'{self.__class__.__name__} with area {self.area():.2f}'\n\n"
                    "class Circle(Shape):\n"
                    "    def __init__(self, radius: float):\n"
                    "        self.radius = radius\n\n"
                    "    def area(self) -> float:\n"
                    "        import math\n"
                    "        return math.pi * self.radius ** 2\n\n"
                    "class Rectangle(Shape):\n"
                    "    def __init__(self, w: float, h: float):\n"
                    "        self.w, self.h = w, h\n\n"
                    "    def area(self) -> float:\n"
                    "        return self.w * self.h\n\n"
                    "shapes = [Circle(5), Rectangle(4, 6)]\n"
                    "for s in shapes:\n"
                    "    print(s.describe())\n"
                    "```\n\n"
                    "## SOLID in One Slide\n"
                    "- **S** – Single Responsibility: one class, one job\n"
                    "- **O** – Open/Closed: open for extension, closed for modification\n"
                    "- **L** – Liskov Substitution: subclasses must honour base contracts\n"
                    "- **I** – Interface Segregation: small, focused interfaces\n"
                    "- **D** – Dependency Inversion: depend on abstractions, not concretions\n"
                )
            }
        )

        m3_cs, _ = Module.objects.get_or_create(
            course=cs101, title='Data Structures & Algorithms', defaults={'order_index': 3}
        )
        Lesson.objects.get_or_create(
            module=m3_cs, title='Lists, Stacks & Queues', defaults={
                'order_index': 1,
                'content_markdown': (
                    "## Linear Data Structures\n\n"
                    "### Python List as a Stack (LIFO)\n\n"
                    "```python\n"
                    "stack = []\n"
                    "stack.append('a')   # push\n"
                    "stack.append('b')\n"
                    "top = stack.pop()   # pop → 'b'\n"
                    "```\n\n"
                    "### Deque as a Queue (FIFO)\n\n"
                    "```python\n"
                    "from collections import deque\n"
                    "queue = deque()\n"
                    "queue.append('first')    # enqueue\n"
                    "queue.append('second')\n"
                    "front = queue.popleft()  # dequeue → 'first'\n"
                    "```\n\n"
                    "## Complexity Comparison\n\n"
                    "| Operation | List (as stack) | deque |\n"
                    "|-----------|-----------------|-------|\n"
                    "| Push/Append | O(1) amortized | O(1) |\n"
                    "| Pop right | O(1) | O(1) |\n"
                    "| Pop left | O(n) | O(1) |\n"
                )
            }
        )

        # --- DS-201 ---
        m1_ds, _ = Module.objects.get_or_create(
            course=ds201, title='Data Acquisition & Preprocessing', defaults={'order_index': 1}
        )
        Lesson.objects.get_or_create(
            module=m1_ds, title='Pandas Fundamentals & Data Wrangling', defaults={
                'order_index': 1,
                'content_markdown': (
                    "# Pandas: The Backbone of Data Science\n\n"
                    "Pandas provides two primary data structures: **Series** (1D) and **DataFrame** (2D).\n\n"
                    "```python\n"
                    "import pandas as pd\n"
                    "import numpy as np\n\n"
                    "# Load a CSV dataset\n"
                    "df = pd.read_csv('students.csv')\n"
                    "print(df.head())         # First 5 rows\n"
                    "print(df.describe())     # Statistical summary\n"
                    "print(df.isnull().sum()) # Missing value counts\n\n"
                    "# Data Cleaning Pipeline\n"
                    "df['gpa'] = pd.to_numeric(df['gpa'], errors='coerce')\n"
                    "df.dropna(subset=['gpa'], inplace=True)\n"
                    "df['gpa'] = df['gpa'].clip(0, 4.0)  # Enforce valid range\n"
                    "```\n\n"
                    "## Key Operations\n\n"
                    "| Task | Code |\n"
                    "|------|------|\n"
                    "| Filter rows | `df[df['age'] > 20]` |\n"
                    "| Select cols | `df[['name', 'gpa']]` |\n"
                    "| Group & aggregate | `df.groupby('dept')['gpa'].mean()` |\n"
                    "| Merge tables | `pd.merge(df1, df2, on='id')` |\n"
                )
            }
        )
        Lesson.objects.get_or_create(
            module=m1_ds, title='Exploratory Data Analysis & Visualisation', defaults={
                'order_index': 2,
                'content_markdown': (
                    "## EDA Workflow\n\n"
                    "Exploratory Data Analysis (EDA) is the critical step of understanding "
                    "your dataset before modelling.\n\n"
                    "```python\n"
                    "import matplotlib.pyplot as plt\n"
                    "import seaborn as sns\n\n"
                    "# Distribution of a feature\n"
                    "sns.histplot(df['gpa'], kde=True, color='steelblue')\n"
                    "plt.title('GPA Distribution')\n"
                    "plt.show()\n\n"
                    "# Correlation heatmap\n"
                    "plt.figure(figsize=(10, 8))\n"
                    "sns.heatmap(df.corr(numeric_only=True), annot=True, cmap='coolwarm', fmt='.2f')\n"
                    "plt.title('Feature Correlation Matrix')\n"
                    "plt.show()\n"
                    "```\n\n"
                    "## EDA Checklist\n"
                    "- [ ] Check shape: `df.shape`\n"
                    "- [ ] Inspect dtypes: `df.dtypes`\n"
                    "- [ ] Identify missing values: `df.isnull().sum()`\n"
                    "- [ ] Detect outliers with boxplots\n"
                    "- [ ] Study feature correlations\n"
                )
            }
        )

        m2_ds, _ = Module.objects.get_or_create(
            course=ds201, title='Machine Learning Fundamentals', defaults={'order_index': 2}
        )
        Lesson.objects.get_or_create(
            module=m2_ds, title='Supervised Learning with scikit-learn', defaults={
                'order_index': 1,
                'content_markdown': (
                    "## Train / Validate / Test Split\n\n"
                    "```python\n"
                    "from sklearn.model_selection import train_test_split\n"
                    "from sklearn.preprocessing import StandardScaler\n"
                    "from sklearn.ensemble import RandomForestClassifier\n"
                    "from sklearn.metrics import classification_report\n\n"
                    "X, y = df.drop('target', axis=1), df['target']\n\n"
                    "X_train, X_test, y_train, y_test = train_test_split(\n"
                    "    X, y, test_size=0.2, random_state=42, stratify=y\n"
                    ")\n\n"
                    "# Scale features\n"
                    "scaler = StandardScaler()\n"
                    "X_train = scaler.fit_transform(X_train)\n"
                    "X_test  = scaler.transform(X_test)\n\n"
                    "# Train\n"
                    "clf = RandomForestClassifier(n_estimators=200, random_state=42)\n"
                    "clf.fit(X_train, y_train)\n\n"
                    "# Evaluate\n"
                    "print(classification_report(y_test, clf.predict(X_test)))\n"
                    "```\n\n"
                    "## Key Metrics\n\n"
                    "| Metric | Formula | Use When |\n"
                    "|--------|---------|----------|\n"
                    "| Accuracy | TP+TN / Total | Balanced classes |\n"
                    "| Precision | TP / (TP+FP) | False positives costly |\n"
                    "| Recall | TP / (TP+FN) | False negatives costly |\n"
                    "| F1 | Harmonic mean P&R | Imbalanced datasets |\n"
                )
            }
        )

        # --- UX-301 ---
        m1_ux, _ = Module.objects.get_or_create(
            course=ux301, title='Design Thinking & User Research', defaults={'order_index': 1}
        )
        Lesson.objects.get_or_create(
            module=m1_ux, title='The Double Diamond Design Process', defaults={
                'order_index': 1,
                'content_markdown': (
                    "# The Double Diamond\n\n"
                    "The Double Diamond is the UK Design Council's model for the design process.\n\n"
                    "```\n"
                    "Discover → Define → Develop → Deliver\n"
                    "  (Diverge)  (Converge)  (Diverge)  (Converge)\n"
                    "```\n\n"
                    "## Phase 1: Discover\n"
                    "- User interviews (semi-structured, 45–60 min)\n"
                    "- Contextual observation / shadowing\n"
                    "- Competitive analysis\n"
                    "- Secondary research (academic + industry reports)\n\n"
                    "## Phase 2: Define\n"
                    "- Affinity mapping and insight clustering\n"
                    "- Persona creation (goal-based, not demographic)\n"
                    "- Problem statement: *How Might We...* framing\n\n"
                    "## Phase 3: Develop\n"
                    "- Crazy-8 ideation sprints\n"
                    "- Low-fi paper prototyping\n"
                    "- Usability testing (think-aloud protocol)\n\n"
                    "## Phase 4: Deliver\n"
                    "- High-fidelity Figma prototypes\n"
                    "- Design system documentation\n"
                    "- Developer handoff via Zeplin / Figma Inspect\n"
                )
            }
        )
        Lesson.objects.get_or_create(
            module=m1_ux, title='Building User Personas & Journey Maps', defaults={
                'order_index': 2,
                'content_markdown': (
                    "## What Makes a Great Persona?\n\n"
                    "A persona is a **fictional but research-based** character representing "
                    "a user segment. It should include:\n\n"
                    "- **Name & Photo** – makes the persona feel human\n"
                    "- **Goals** – what they're trying to accomplish\n"
                    "- **Pain Points** – frustrations and blockers\n"
                    "- **Behaviours** – how they interact with technology\n"
                    "- **Quote** – a direct quote from user research\n\n"
                    "## Journey Map Template\n\n"
                    "| Stage | Actions | Thoughts | Emotions | Opportunities |\n"
                    "|-------|---------|----------|----------|---------------|\n"
                    "| Awareness | Sees ad | 'What is this?' | Curious | Clear value prop |\n"
                    "| Consideration | Browses site | 'Is this for me?' | Uncertain | Social proof |\n"
                    "| Purchase | Checkout | 'Will this work?' | Anxious | Reduce friction |\n"
                    "| Retention | Uses product | 'I like this' | Satisfied | Delight moments |\n"
                )
            }
        )

        m2_ux, _ = Module.objects.get_or_create(
            course=ux301, title='Visual Design & Design Systems', defaults={'order_index': 2}
        )
        Lesson.objects.get_or_create(
            module=m2_ux, title='Typography, Colour Theory & Hierarchy', defaults={
                'order_index': 1,
                'content_markdown': (
                    "## Typography Fundamentals\n\n"
                    "Good typography is **80% of design**. Key principles:\n\n"
                    "| Property | Recommendation |\n"
                    "|----------|---------------|\n"
                    "| Body size | 16px minimum for legibility |\n"
                    "| Line height | 1.5–1.7 for body text |\n"
                    "| Line length | 60–80 characters per line |\n"
                    "| Type scale | Modular (ratio 1.25 or 1.333) |\n\n"
                    "## Colour & Contrast\n\n"
                    "WCAG 2.1 minimum contrast ratios:\n"
                    "- **AA normal text:** 4.5:1\n"
                    "- **AA large text:** 3:1\n"
                    "- **AAA normal text:** 7:1\n\n"
                    "## HSL Colour System\n\n"
                    "```css\n"
                    ":root {\n"
                    "  --primary: hsl(220, 90%, 56%);\n"
                    "  --primary-dark: hsl(220, 90%, 40%);\n"
                    "  --neutral-50: hsl(220, 14%, 96%);\n"
                    "  --neutral-900: hsl(220, 14%, 10%);\n"
                    "}\n"
                    "```\n"
                )
            }
        )

        # --- SEC-401 ---
        m1_sec, _ = Module.objects.get_or_create(
            course=sec401, title='Threat Modelling & Attack Surfaces', defaults={'order_index': 1}
        )
        Lesson.objects.get_or_create(
            module=m1_sec, title='STRIDE Threat Modelling Framework', defaults={
                'order_index': 1,
                'content_markdown': (
                    "# STRIDE Threat Modelling\n\n"
                    "STRIDE is Microsoft's systematic framework for identifying security threats:\n\n"
                    "| Letter | Threat | Example |\n"
                    "|--------|--------|---------|\n"
                    "| **S** | Spoofing | Attacker forges authentication tokens |\n"
                    "| **T** | Tampering | Modifying data in transit (MITM) |\n"
                    "| **R** | Repudiation | User denies performing an action |\n"
                    "| **I** | Information Disclosure | Exposing PII via verbose errors |\n"
                    "| **D** | Denial of Service | Resource exhaustion attacks |\n"
                    "| **E** | Elevation of Privilege | Exploiting IDOR to access admin data |\n\n"
                    "## Applying STRIDE: Process\n"
                    "1. Draw a Data Flow Diagram (DFD) of your system\n"
                    "2. Identify trust boundaries (where data crosses privilege levels)\n"
                    "3. Apply each STRIDE category to each DFD element\n"
                    "4. Rate severity using DREAD scoring: `(D+R+E+A+D) / 5`\n"
                    "5. Prioritise mitigations by risk score\n\n"
                    "```python\n"
                    "def dread_score(damage, reproducibility, exploitability, affected, discoverability):\n"
                    "    return (damage + reproducibility + exploitability + affected + discoverability) / 5\n\n"
                    "sql_injection = dread_score(9, 9, 7, 8, 7)\n"
                    "print(f'SQL Injection DREAD: {sql_injection}')  # → 8.0 (Critical)\n"
                    "```\n"
                )
            }
        )
        Lesson.objects.get_or_create(
            module=m1_sec, title='OWASP Top 10 Deep Dive', defaults={
                'order_index': 2,
                'content_markdown': (
                    "# OWASP Top 10 (2021)\n\n"
                    "The OWASP Top 10 is the industry-standard awareness document for web security.\n\n"
                    "## A01: Broken Access Control\n\n"
                    "```python\n"
                    "# ❌ Vulnerable: No authorisation check\n"
                    "def get_report(request, report_id):\n"
                    "    report = Report.objects.get(id=report_id)\n"
                    "    return JsonResponse(report.to_dict())\n\n"
                    "# ✅ Secure: Verify ownership\n"
                    "def get_report(request, report_id):\n"
                    "    report = get_object_or_404(Report, id=report_id, owner=request.user)\n"
                    "    return JsonResponse(report.to_dict())\n"
                    "```\n\n"
                    "## A02: Cryptographic Failures\n"
                    "- Never store passwords in plaintext or with MD5/SHA-1\n"
                    "- Use `bcrypt`, `argon2`, or `pbkdf2` with adequate iterations\n"
                    "- Enforce TLS 1.2+ everywhere; prefer TLS 1.3\n\n"
                    "## A03: Injection\n\n"
                    "```sql\n"
                    "-- ❌ Dangerous: String concatenation\n"
                    "SELECT * FROM users WHERE username = '\" + username + \"';\n\n"
                    "-- ✅ Safe: Parameterised query\n"
                    "SELECT * FROM users WHERE username = ?;\n"
                    "```\n"
                )
            }
        )

        m2_sec, _ = Module.objects.get_or_create(
            course=sec401, title='Cryptography & PKI', defaults={'order_index': 2}
        )
        Lesson.objects.get_or_create(
            module=m2_sec, title='Symmetric & Asymmetric Cryptography', defaults={
                'order_index': 1,
                'content_markdown': (
                    "## Symmetric Key Cryptography\n\n"
                    "Same key for encryption and decryption. Fast but requires secure key exchange.\n\n"
                    "```python\n"
                    "from cryptography.fernet import Fernet\n\n"
                    "# Generate a key\n"
                    "key = Fernet.generate_key()\n"
                    "cipher = Fernet(key)\n\n"
                    "# Encrypt\n"
                    "token = cipher.encrypt(b'Super secret message')\n"
                    "print(token)\n\n"
                    "# Decrypt\n"
                    "plaintext = cipher.decrypt(token)\n"
                    "print(plaintext)  # b'Super secret message'\n"
                    "```\n\n"
                    "## Asymmetric Cryptography (RSA)\n\n"
                    "```python\n"
                    "from cryptography.hazmat.primitives.asymmetric import rsa, padding\n"
                    "from cryptography.hazmat.primitives import hashes\n\n"
                    "# Generate key pair\n"
                    "private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)\n"
                    "public_key  = private_key.public_key()\n\n"
                    "# Encrypt with public key\n"
                    "ciphertext = public_key.encrypt(\n"
                    "    b'Hello RSA',\n"
                    "    padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA256()),\n"
                    "                 algorithm=hashes.SHA256(), label=None)\n"
                    ")\n"
                    "```\n\n"
                    "## Key Comparison\n\n"
                    "| Property | Symmetric | Asymmetric |\n"
                    "|----------|-----------|------------|\n"
                    "| Speed | Fast | Slow |\n"
                    "| Key sharing | Problematic | Safe (public key) |\n"
                    "| Use case | Bulk encryption | Key exchange, signatures |\n"
                    "| Example | AES-256 | RSA-2048, ECC P-256 |\n"
                )
            }
        )

        self.stdout.write(self.style.SUCCESS("  ✓ Curriculum built: 4 courses × 2–3 modules × 2–3 lessons each"))

        # =========================================================
        # 4. ENROLLMENTS – spread students across courses realistically
        # =========================================================
        self.stdout.write(self.style.HTTP_INFO("\n[4/7] Enrolling Students..."))

        enrollment_map = {
            cs101:  students[:8],   # 8 students
            ds201:  students[2:7],  # 5 students
            ux301:  students[3:9],  # 6 students
            sec401: students[5:],   # 5 students
        }
        for course, enrolled_students in enrollment_map.items():
            for student in enrolled_students:
                Enrollment.objects.get_or_create(
                    student=student, course=course, defaults={'is_active': True}
                )

        total_enrolments = Enrollment.objects.count()
        self.stdout.write(self.style.SUCCESS(f"  ✓ {total_enrolments} enrolment records created"))

        # =========================================================
        # 5. ASSIGNMENTS
        # =========================================================
        self.stdout.write(self.style.HTTP_INFO("\n[5/7] Creating Assignments..."))

        # CS-101 Assignments
        asn_cs_diag, _ = Assignment.objects.get_or_create(
            course=cs101, title='Diagnostic: Prerequisite Skills Assessment',
            defaults={
                'instructions': (
                    "# Prerequisite Diagnostic\n\n"
                    "This short diagnostic helps us calibrate your starting point.\n\n"
                    "## Tasks\n"
                    "1. Solve 5 algorithmic puzzles (provided in the PDF template)\n"
                    "2. Brief written reflection on your prior programming experience\n\n"
                    "**Submission:** Single PDF, max 5 pages."
                ),
                'release_at': now - timedelta(days=25),
                'deadline':   now - timedelta(days=18),
                'max_points': Decimal('20.00'),
                'allow_resubmissions': False,
            }
        )
        asn_cs1, _ = Assignment.objects.get_or_create(
            course=cs101, title='Lab 1: Python Basics & Algorithm Design',
            defaults={
                'instructions': (
                    "# Lab 1: Python Basics & Algorithm Design\n\n"
                    "Implement the following algorithms from scratch in Python.\n\n"
                    "## Required Implementations\n"
                    "1. **Bubble Sort** – with step-count instrumentation\n"
                    "2. **Binary Search** – iterative and recursive variants\n"
                    "3. **Fibonacci (memoised)** – compare with naive recursive approach\n\n"
                    "## Deliverables\n"
                    "- `lab1_solution.py` – commented source code\n"
                    "- `lab1_report.pdf` – Big-O analysis and test results\n\n"
                    "## Submission Guidelines\n"
                    "- Package both files in a **ZIP archive** (max 25 MB)\n"
                    "- Name your file: `STU-XXX_Lab1.zip`\n"
                    "- Submissions after the deadline incur a 10% late penalty.\n\n"
                    "> **Tip:** Use `time.perf_counter()` to benchmark your implementations."
                ),
                'release_at': now - timedelta(days=12),
                'deadline':   now + timedelta(days=5),
                'max_points': Decimal('100.00'),
                'allow_resubmissions': True,
            }
        )
        asn_cs2, _ = Assignment.objects.get_or_create(
            course=cs101, title='Lab 2: Object-Oriented Banking Simulator',
            defaults={
                'instructions': (
                    "# Lab 2: OOP Banking System Simulator\n\n"
                    "Design and implement a banking simulator demonstrating "
                    "all four pillars of OOP.\n\n"
                    "## System Requirements\n"
                    "- `Account` base class with `deposit`, `withdraw`, `get_balance`\n"
                    "- `SavingsAccount` subclass with interest rate logic\n"
                    "- `CheckingAccount` subclass with overdraft protection\n"
                    "- `Bank` class that manages a portfolio of accounts\n"
                    "- Full unit tests using `unittest` or `pytest`\n\n"
                    "## Bonus (10 pts)\n"
                    "Persist account data to/from a JSON file.\n\n"
                    "**Deadline:** See above. **Max Points:** 100 (+10 bonus)\n"
                    "**Format:** `.zip` containing all `.py` files"
                ),
                'release_at': now - timedelta(days=3),
                'deadline':   now + timedelta(days=21),
                'max_points': Decimal('100.00'),
                'allow_resubmissions': False,
            }
        )
        asn_cs_midterm, _ = Assignment.objects.get_or_create(
            course=cs101, title='Midterm: Algorithmic Problem Set',
            defaults={
                'instructions': (
                    "# Midterm Examination\n\n"
                    "Open-resource, timed take-home. You have 3 hours once you begin.\n\n"
                    "## Problem Set\n"
                    "1. Implement a balanced BST with insert, search, and in-order traversal\n"
                    "2. Solve the N-Queens problem using backtracking\n"
                    "3. Implement Dijkstra's shortest path on an adjacency list\n\n"
                    "**Academic Integrity:** Individual submission only. Collaboration will result in zero.\n"
                    "**Format:** Single `.pdf` with code screenshots and analysis"
                ),
                'release_at': now - timedelta(days=1),
                'deadline':   now + timedelta(days=10),
                'max_points': Decimal('150.00'),
                'allow_resubmissions': False,
            }
        )

        # DS-201 Assignments
        asn_ds1, _ = Assignment.objects.get_or_create(
            course=ds201, title='Notebook 1: Exploratory Data Analysis',
            defaults={
                'instructions': (
                    "# EDA Notebook Assignment\n\n"
                    "Using the provided `students_dataset.csv`, perform a complete EDA.\n\n"
                    "## Requirements\n"
                    "- Summary statistics for all numeric features\n"
                    "- At least 6 visualisations (histograms, box plots, scatter plots, heatmap)\n"
                    "- Written interpretation of every chart\n"
                    "- Outlier identification and handling strategy\n\n"
                    "**Format:** Jupyter Notebook (`.ipynb`) exported to `.pdf`"
                ),
                'release_at': now - timedelta(days=8),
                'deadline':   now + timedelta(days=6),
                'max_points': Decimal('80.00'),
                'allow_resubmissions': True,
            }
        )
        asn_ds2, _ = Assignment.objects.get_or_create(
            course=ds201, title='Notebook 2: ML Classification Pipeline',
            defaults={
                'instructions': (
                    "# ML Classification Assignment\n\n"
                    "Build and evaluate a full ML pipeline on the Titanic survival dataset.\n\n"
                    "## Required Steps\n"
                    "1. Data cleaning and feature engineering\n"
                    "2. Train/validate/test split (80/10/10)\n"
                    "3. Train at least 3 classifiers (Logistic Regression, Random Forest, XGBoost)\n"
                    "4. Hyperparameter tuning via `GridSearchCV`\n"
                    "5. Report precision, recall, F1, ROC-AUC per model\n"
                    "6. Explain why one model outperforms the others\n\n"
                    "**Bonus:** SHAP feature importance explanation."
                ),
                'release_at': now + timedelta(days=2),
                'deadline':   now + timedelta(days=18),
                'max_points': Decimal('100.00'),
                'allow_resubmissions': False,
            }
        )

        # UX-301 Assignments
        asn_ux1, _ = Assignment.objects.get_or_create(
            course=ux301, title='Design Sprint 1: User Research Report',
            defaults={
                'instructions': (
                    "# User Research Report\n\n"
                    "Conduct 3 user interviews on the topic of **online learning platforms**.\n\n"
                    "## Deliverables\n"
                    "1. Interview guide (semi-structured, 15–20 questions)\n"
                    "2. Interview transcripts (anonymised)\n"
                    "3. Affinity map (photo or digital)\n"
                    "4. 2 user personas derived from research\n"
                    "5. Problem statement using *How Might We* framing\n\n"
                    "**Format:** PDF report, 8–12 pages"
                ),
                'release_at': now - timedelta(days=10),
                'deadline':   now + timedelta(days=4),
                'max_points': Decimal('75.00'),
                'allow_resubmissions': True,
            }
        )

        # SEC-401 Assignments
        asn_sec1, _ = Assignment.objects.get_or_create(
            course=sec401, title='CTF Challenge 1: Web Security Fundamentals',
            defaults={
                'instructions': (
                    "# CTF Challenge 1: Web Security\n\n"
                    "Access the provided CTF sandbox environment and capture all 5 flags.\n\n"
                    "## Challenges\n"
                    "1. **Flag 1** – Exploit an IDOR vulnerability in the user profile API\n"
                    "2. **Flag 2** – Perform a reflected XSS attack on the search parameter\n"
                    "3. **Flag 3** – SQL injection via the login form\n"
                    "4. **Flag 4** – Exploit a weak JWT secret to forge an admin token\n"
                    "5. **Flag 5** – SSRF to read the internal metadata service\n\n"
                    "## Report\n"
                    "For each flag: describe the vulnerability, proof of concept, impact, and remediation.\n\n"
                    "**Sandbox URL:** Provided via secure channel on the day. **Format:** PDF"
                ),
                'release_at': now - timedelta(days=5),
                'deadline':   now + timedelta(days=9),
                'max_points': Decimal('120.00'),
                'allow_resubmissions': False,
            }
        )

        self.stdout.write(self.style.SUCCESS(
            f"  ✓ {Assignment.objects.count()} assignments created across all courses"
        ))

        # =========================================================
        # 6. SUBMISSIONS & GRADING
        # =========================================================
        self.stdout.write(self.style.HTTP_INFO("\n[6/7] Creating Submissions & Grades..."))

        sub_dir = 'media/submissions'
        os.makedirs(sub_dir, exist_ok=True)

        def make_pdf(filename):
            path = os.path.join(sub_dir, filename)
            if not os.path.exists(path):
                with open(path, 'wb') as f:
                    f.write(b"%PDF-1.4 UnivLMS sample submission\n%Content placeholder")
            return f'submissions/{filename}'

        # Diagnostic (past) submissions – all 8 students who enrolled in CS-101
        diag_grades = [
            (students[0], Decimal('18.50'), "Excellent prerequisite knowledge, John! Strong algorithmic intuition.", False),
            (students[1], Decimal('16.00'), "Good foundations, Sarah. Brush up on recursion before Lab 1.", False),
            (students[2], Decimal('19.00'), "Outstanding, Mike! Perfect diagnostic score.", False),
            (students[3], Decimal('14.00'), "Alice, review loop invariants – they'll be critical this semester.", False),
            (students[4], Decimal('15.50'), "Solid effort, Bob. Time management on problem 4 needs work.", False),
            (students[5], Decimal('17.00'), "Great work, Priya. Your Python is clean and readable.", False),
            (students[6], Decimal('12.00'), "Liam, please visit office hours – foundations need strengthening.", True),
            (students[7], Decimal('18.00'), "Excellent, Emma! Ready for Lab 1.", False),
        ]
        for student, score, feedback, is_late in diag_grades:
            sub, _ = Submission.objects.get_or_create(
                assignment=asn_cs_diag, student=student,
                defaults={
                    'file': make_pdf(f'diag_{student.username}.pdf'),
                    'is_late': is_late, 'score': score,
                    'feedback_markdown': f"**{feedback}**",
                    'graded_by': fac_smith,
                    'graded_at': now - timedelta(days=15),
                }
            )

        # Lab 1 submissions – 6 of 8 students submitted
        lab1_subs = [
            (students[0], Decimal('95.00'), "**Outstanding, John!** Your modular design shows excellent grasp of Big-O. The `partition()` edge-case handling could be tightened – see comments inline.", False),
            (students[1], Decimal('82.00'), "**Good work, Sarah.** Binary search is correct and well-tested. Bubble sort lacks the early-exit optimisation discussed in Module 1.", False),
            (students[2], Decimal('98.00'), "**Exceptional submission, Mike.** Perfect Big-O analysis and benchmarks. Extra marks for the visualisation chart comparing all three algorithms.", False),
            (students[3], Decimal('71.00'), "**Adequate, Alice.** The memoisation is missing for Fibonacci – you're computing it naively. Resubmit before final deadline.", False),
            (students[4], None, None, False),   # submitted, not yet graded
            (students[5], Decimal('88.00'), "**Well done, Priya!** Clean code, good test coverage. Improve your report's complexity proofs – they need more rigour.", False),
        ]
        for student, score, feedback, is_late in lab1_subs:
            Submission.objects.get_or_create(
                assignment=asn_cs1, student=student,
                defaults={
                    'file': make_pdf(f'lab1_{student.username}.pdf'),
                    'is_late': is_late,
                    'score': score,
                    'feedback_markdown': feedback,
                    'graded_by': fac_smith if score else None,
                    'graded_at': now - timedelta(days=2) if score else None,
                }
            )

        # DS-201 EDA Notebook submissions
        ds_subs = [
            (students[2], Decimal('76.00'), "**Good EDA, Mike!** Visualisations are professional. The outlier handling section needs a stronger justification.", False),
            (students[3], Decimal('69.00'), "**Passing, Alice.** Missing the correlation heatmap and scatter matrix. Interpretation paragraphs are brief.", True),
            (students[4], Decimal('78.00'), "**Solid notebook, Bob.** Great use of seaborn. Consider adding a final summary section with 3–5 key takeaways.", False),
            (students[5], None, None, False),  # not yet graded
        ]
        for student, score, feedback, is_late in ds_subs:
            Submission.objects.get_or_create(
                assignment=asn_ds1, student=student,
                defaults={
                    'file': make_pdf(f'eda_{student.username}.pdf'),
                    'is_late': is_late,
                    'score': score,
                    'feedback_markdown': feedback,
                    'graded_by': fac_smith if score else None,
                    'graded_at': now - timedelta(days=1) if score else None,
                }
            )

        # UX-301 Research report submissions
        ux_subs = [
            (students[3], Decimal('68.00'), "**Good research, Alice.** Personas feel a bit generic – root them more firmly in your interview data. Journey map is excellent.", False),
            (students[5], Decimal('72.00'), "**Strong effort, Priya!** HMW statements are creative. Interview transcripts could be more comprehensive.", False),
            (students[6], Decimal('60.00'), "**Marginal pass, Liam.** Only 2 interviews conducted (minimum 3). Resubmission encouraged.", False),
        ]
        for student, score, feedback, is_late in ux_subs:
            Submission.objects.get_or_create(
                assignment=asn_ux1, student=student,
                defaults={
                    'file': make_pdf(f'uxresearch_{student.username}.pdf'),
                    'is_late': is_late,
                    'score': score,
                    'feedback_markdown': feedback,
                    'graded_by': fac_chen if score else None,
                    'graded_at': now - timedelta(days=1) if score else None,
                }
            )

        # SEC-401 CTF submission
        Submission.objects.get_or_create(
            assignment=asn_sec1, student=students[5],
            defaults={
                'file': make_pdf(f'ctf1_{students[5].username}.pdf'),
                'is_late': False,
                'score': Decimal('105.00'),
                'feedback_markdown': (
                    "**Exceptional CTF performance, Priya!** All 5 flags captured. "
                    "Your SSRF writeup is particularly strong – publish-worthy quality. "
                    "The JWT secret-cracking explanation could walk the reader through your tooling choices."
                ),
                'graded_by': fac_morgan,
                'graded_at': now - timedelta(hours=6),
            }
        )

        total_subs = Submission.objects.count()
        self.stdout.write(self.style.SUCCESS(f"  ✓ {total_subs} submissions created with realistic grading data"))

        # =========================================================
        # 7. AUDIT LOG
        # =========================================================
        self.stdout.write(self.style.HTTP_INFO("\n[7/7] Writing Audit Trail..."))

        audit_events = [
            (admin,      'SYSTEM_INITIALIZE',    'UnivLMS Academic Platform v2.0',               now - timedelta(days=30)),
            (admin,      'COURSE_CREATE',         f'Course {cs101.course_code}: {cs101.title}',   now - timedelta(days=29)),
            (admin,      'COURSE_CREATE',         f'Course {ds201.course_code}: {ds201.title}',   now - timedelta(days=29)),
            (admin,      'COURSE_CREATE',         f'Course {ux301.course_code}: {ux301.title}',   now - timedelta(days=28)),
            (admin,      'COURSE_CREATE',         f'Course {sec401.course_code}: {sec401.title}', now - timedelta(days=28)),
            (admin,      'COURSE_ASSIGN',         f'{cs101.course_code} → {fac_smith.username}',  now - timedelta(days=27)),
            (admin,      'COURSE_ASSIGN',         f'{ds201.course_code} → {fac_smith.username}',  now - timedelta(days=27)),
            (admin,      'COURSE_ASSIGN',         f'{ux301.course_code} → {fac_chen.username}',   now - timedelta(days=26)),
            (admin,      'COURSE_ASSIGN',         f'{sec401.course_code} → {fac_morgan.username}',now - timedelta(days=26)),
            (admin,      'USER_CREATE',           f'Batch: 10 student accounts created',          now - timedelta(days=25)),
            (fac_smith,  'ASSIGNMENT_PUBLISH',    f'{asn_cs_diag.title}',                         now - timedelta(days=25)),
            (fac_smith,  'ASSIGNMENT_PUBLISH',    f'{asn_cs1.title}',                             now - timedelta(days=12)),
            (fac_smith,  'ASSIGNMENT_PUBLISH',    f'{asn_cs2.title}',                             now - timedelta(days=3)),
            (fac_smith,  'GRADE_SUBMIT',          f'Diagnostic grades posted (8 students)',       now - timedelta(days=15)),
            (fac_smith,  'GRADE_SUBMIT',          f'Lab 1 grades posted (5 students)',            now - timedelta(days=2)),
            (fac_chen,   'ASSIGNMENT_PUBLISH',    f'{asn_ux1.title}',                             now - timedelta(days=10)),
            (fac_chen,   'GRADE_SUBMIT',          f'UX-301 Sprint 1 grades (3 students)',         now - timedelta(days=1)),
            (fac_morgan, 'ASSIGNMENT_PUBLISH',    f'{asn_sec1.title}',                            now - timedelta(days=5)),
            (fac_morgan, 'GRADE_SUBMIT',          f'CTF-1 grade posted for {students[5].username}', now - timedelta(hours=6)),
            (admin,      'REPORT_EXPORT',         'Semester enrollment roster CSV exported',      now - timedelta(days=2)),
            (admin,      'USER_DEACTIVATE',       'Inactive account STU-999 deactivated',         now - timedelta(days=1)),
        ]
        for actor, action_type, target_entity, ts in audit_events:
            if not AuditLog.objects.filter(actor=actor, action_type=action_type, target_entity=target_entity).exists():
                AuditLog.objects.create(
                    actor=actor, action_type=action_type,
                    target_entity=target_entity, timestamp=ts
                )

        self.stdout.write(self.style.SUCCESS(f"  ✓ {AuditLog.objects.count()} audit log entries"))

        # =========================================================
        # SUMMARY
        # =========================================================
        self.stdout.write(self.style.NOTICE("\n" + "=" * 60))
        self.stdout.write(self.style.SUCCESS("  ✅ UnivLMS Database Seeded Successfully!"))
        self.stdout.write(self.style.NOTICE("=" * 60))
        self.stdout.write(f"""
  Demo Credentials:
  ┌─────────────┬──────────────────────┬───────────────┐
  │ Role        │ Username             │ Password      │
  ├─────────────┼──────────────────────┼───────────────┤
  │ Admin       │ admin_root           │ Admin@12345   │
  │ Faculty     │ prof_smith           │ Faculty@12345 │
  │ Faculty     │ dr_chen              │ Faculty@12345 │
  │ Faculty     │ prof_morgan          │ Faculty@12345 │
  │ Student     │ john_doe             │ Student@12345 │
  │ Student     │ sarah_connor         │ Student@12345 │
  │ Student     │ (8 more students...) │ Student@12345 │
  └─────────────┴──────────────────────┴───────────────┘
""")
