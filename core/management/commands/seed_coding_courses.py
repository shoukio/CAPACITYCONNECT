from django.core.management.base import BaseCommand

from core.models import Course, CourseLesson


SAMPLE_COURSES = (
    {
        "slug": "python-programming-foundations",
        "title": "Python Programming Foundations",
        "category": "Programming",
        "summary": "Learn Python basics, write clean code, and build your first programs.",
        "description": (
            "Start programming with Python. Learn variables, data types, conditions, "
            "loops, functions, and how to break a problem into manageable steps. "
            "Finish by building a small command-line project."
        ),
        "level": Course.Level.BEGINNER,
        "duration_hours": 8,
        "lessons": (
            (
                "Meet Python: values and variables",
                """Python instructions are written as readable statements. A variable gives a value a useful name so you can use it later.

Example:
name = "Asha"
hours = 3
print(f"{name} studied for {hours} hours")

Text values are strings, whole numbers are integers, and decimal numbers are floats. Choose names that explain what the value represents.

Try it: create variables for a course title and the number of lessons, then print a sentence using both.""",
                20,
            ),
            (
                "Make decisions and repeat work",
                """A condition lets a program choose what to do. Indentation marks which statements belong to the condition.

Example:
score = 72
if score >= 60:
    print("You passed")
else:
    print("Keep practicing")

Use a for loop when you want to repeat an action for each item:
for topic in ["variables", "conditions", "loops"]:
    print(topic)

Try it: loop over three learner names and print a welcome message for each one.""",
                25,
            ),
            (
                "Write functions and build a mini program",
                """Functions package a useful task under a name. Parameters are the inputs and return sends a result back to the caller.

Example:
def course_message(title):
    return f"Welcome to {title}!"

print(course_message("Python Foundations"))

Mini project: write a function that accepts a list of quiz scores and returns the average. Test it with at least three scores, including a score of zero.""",
                30,
            ),
        ),
    },
    {
        "slug": "html-css-responsive-websites",
        "title": "HTML and CSS: Responsive Websites",
        "category": "Web Development",
        "summary": "Create accessible web pages that work across screen sizes.",
        "description": (
            "Learn semantic HTML, modern CSS, layout with Flexbox and Grid, "
            "responsive design, and accessibility essentials. Build a polished "
            "multi-page website as a practical project."
        ),
        "level": Course.Level.BEGINNER,
        "duration_hours": 7,
        "lessons": (
            (
                "Give a page meaningful structure",
                """HTML describes the meaning and structure of a web page. Use headings in order, paragraphs for text, and links for navigation.

Example:
<main>
  <h1>My learning journal</h1>
  <p>Notes from my first web project.</p>
  <a href="/courses/">Browse courses</a>
</main>

Prefer semantic elements such as header, nav, main, article, and footer. They help assistive technologies and make code easier to understand.

Try it: make a page with a heading, an introduction, and a list of three skills you want to learn.""",
                20,
            ),
            (
                "Style a page with CSS",
                """CSS controls how HTML looks. A rule selects elements and gives them style properties.

Example:
.learning-card {
  padding: 1rem;
  border: 1px solid #d8ded1;
  border-radius: 8px;
}

Use spacing, readable color contrast, and a small set of consistent text sizes. Keep content and presentation separate: HTML for meaning, CSS for appearance.

Try it: add a background color and comfortable padding to your journal page.""",
                25,
            ),
            (
                "Make layouts responsive and accessible",
                """A responsive layout adapts to different screen widths. CSS Grid and Flexbox help arrange content without fixed pixel positioning.

Example:
.cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 1rem;
}

Add descriptive alternative text to meaningful images, label form controls, and ensure links describe their destination. Test by narrowing the browser window and navigating with a keyboard.

Try it: show your cards in two columns on a wide screen and one column on a narrow screen.""",
                25,
            ),
        ),
    },
    {
        "slug": "javascript-essentials",
        "title": "JavaScript Essentials",
        "category": "Web Development",
        "summary": "Add interaction to web pages with modern JavaScript.",
        "description": (
            "Practice JavaScript values, functions, arrays, objects, events, and "
            "DOM updates. Build interactive page features and learn how to debug "
            "common browser-side issues."
        ),
        "level": Course.Level.BEGINNER,
        "duration_hours": 9,
        "lessons": (
            (
                "JavaScript values and variables",
                """JavaScript runs in the browser and can respond to user actions. Use const for values that will not be reassigned and let when reassignment is needed.

Example:
const learner = "Asha";
let completedLessons = 0;
completedLessons = completedLessons + 1;

Strings, numbers, booleans, arrays, and objects are common data types. Clear names make code easier to maintain.

Try it: create an array of three topics and print the first topic.""",
                20,
            ),
            (
                "Functions, arrays, and objects",
                """A function describes a reusable action. Arrays hold ordered items; objects group related named values.

Example:
const course = { title: "JavaScript Essentials", lessons: 3 };
function courseLabel(item) {
  return `${item.title}: ${item.lessons} lessons`;
}

Use array methods such as map to transform items and filter to select matching items.

Try it: store three course objects in an array, then create a list of their titles.""",
                25,
            ),
            (
                "Respond to events and update a page",
                """The Document Object Model (DOM) represents a page that JavaScript can inspect and update. An event listener runs a function when an event happens.

Example:
const button = document.querySelector("#welcome-button");
button.addEventListener("click", () => {
  document.querySelector("#message").textContent = "Welcome!";
});

Make sure the selected elements exist before using them. Keep browser interactions small and explain what happens after each action.

Try it: add a button that reveals a short learning tip when clicked.""",
                30,
            ),
        ),
    },
    {
        "slug": "django-web-development",
        "title": "Django Web Development",
        "category": "Web Development",
        "summary": "Build a database-backed web application using Django.",
        "description": (
            "Create a Django project and learn URL routing, views, templates, "
            "models, forms, migrations, and the built-in admin. Apply the concepts "
            "in a small, secure web application."
        ),
        "level": Course.Level.INTERMEDIATE,
        "duration_hours": 12,
        "lessons": (
            (
                "Start a Django project",
                """Django is a Python framework for building web applications. A project holds site-wide configuration; an app groups a feature.

Useful commands:
python -m pip install Django
django-admin startproject config .
python manage.py startapp courses
python manage.py runserver

The development server is for local work. Create an app for a coherent feature and add it to INSTALLED_APPS before using its models and templates.

Try it: run the server and open its local address in your browser.""",
                25,
            ),
            (
                "Connect URLs, views, and templates",
                """A URL pattern routes a browser path to a view. A view prepares data and returns a response, often by rendering a template.

Example:
from django.shortcuts import render

def course_home(request):
    return render(request, "courses/home.html", {"title": "My courses"})

In the template:
<h1>{{ title }}</h1>

Use named URL patterns and Django's url template tag instead of hard-coding internal links.

Try it: add a named /about/ route and render a template with a heading.""",
                30,
            ),
            (
                "Models, migrations, and the admin",
                """Django models describe database tables using Python classes. A migration records a safe database schema change.

Example:
class LearningTopic(models.Model):
    title = models.CharField(max_length=120)
    summary = models.TextField()

After editing a model, run:
python manage.py makemigrations
python manage.py migrate

Register models in admin.py to manage records through Django's protected administration site. Review generated migrations before applying them.

Try it: add a topic model, create its migration, and add one record through the admin.""",
                30,
            ),
        ),
    },
    {
        "slug": "sql-database-design",
        "title": "SQL and Database Design",
        "category": "Data and Databases",
        "summary": "Query relational data and design reliable database tables.",
        "description": (
            "Learn relational database concepts, table design, keys, constraints, "
            "and practical SQL. Write SELECT queries with filtering, joins, and "
            "aggregations, then model a small application database."
        ),
        "level": Course.Level.BEGINNER,
        "duration_hours": 8,
        "lessons": (
            (
                "Tables, keys, and relationships",
                """A relational database stores records in tables. Each row has a primary key; a foreign key points to a related row.

Example schema:
Learner(id, name)
Course(id, title)
Enrollment(id, learner_id, course_id)

An enrollment table represents a many-to-many relationship between learners and courses. Constraints help prevent invalid or duplicate records.

Try it: sketch tables for books and authors, including how you would represent a book with multiple authors.""",
                20,
            ),
            (
                "Read and filter data with SELECT",
                """SELECT retrieves columns from a table. WHERE filters rows and ORDER BY sorts the result.

Example:
SELECT title, level
FROM Course
WHERE level = 'beginner'
ORDER BY title;

Use explicit column names instead of selecting every field when you only need a few. A clear filter makes the intended result easier to check.

Try it: write a query to list learners whose names begin with the letter A.""",
                25,
            ),
            (
                "Join and summarize related records",
                """A JOIN combines related rows using a key. GROUP BY collects rows so aggregate functions can summarize them.

Example:
SELECT Course.title, COUNT(Enrollment.id) AS learner_count
FROM Course
LEFT JOIN Enrollment ON Enrollment.course_id = Course.id
GROUP BY Course.id, Course.title;

LEFT JOIN keeps courses even when no learner has enrolled. COUNT, SUM, and AVG are common aggregate functions.

Try it: adapt the query to show only courses with at least one learner.""",
                25,
            ),
        ),
    },
    {
        "slug": "git-github-for-developers",
        "title": "Git and GitHub for Developers",
        "category": "Developer Tools",
        "summary": "Track code changes and collaborate confidently with Git.",
        "description": (
            "Learn repositories, commits, branches, merges, and resolving conflicts. "
            "Practice a safe team workflow and use GitHub to share work and review "
            "changes."
        ),
        "level": Course.Level.BEGINNER,
        "duration_hours": 5,
        "lessons": (
            (
                "Track changes with Git",
                """Git records project changes so you can review work and safely return to earlier versions.

Common commands:
git status
git add README.md
git commit -m "Add project introduction"

Review git status before committing so you know which files are staged. A commit should capture one understandable change.

Try it: make a small edit in a practice folder, inspect the status, and commit the change.""",
                20,
            ),
            (
                "Work with branches",
                """A branch gives you a separate line of work. It lets you develop a feature without changing the main branch until it is ready.

Common commands:
git switch -c add-course-list
git status
git switch main

Commit your branch in small steps. Before merging, review the differences and run the project's tests.

Try it: create a branch, make a harmless documentation change, and compare it with main.""",
                20,
            ),
            (
                "Share work on GitHub",
                """GitHub hosts Git repositories and supports collaboration through pull requests. A pull request describes a change and invites review before it is merged.

Common commands:
git remote -v
git push -u origin add-course-list

Never put passwords, API keys, or private tokens in a repository. Review changed files before pushing and use environment variables for secrets.

Try it: open a pull request for your practice branch and write a short summary of the change.""",
                20,
            ),
        ),
    },
    {
        "slug": "everyday-leadership",
        "title": "Everyday Leadership",
        "category": "Leadership",
        "summary": "Build trust, set clear goals, and support your team’s growth.",
        "description": (
            "Practice the everyday habits of effective leadership: listening "
            "carefully, communicating expectations, giving useful feedback, "
            "and helping a team learn from challenges."
        ),
        "level": Course.Level.BEGINNER,
        "duration_hours": 4,
        "lessons": (
            (
                "Lead with trust and clear expectations",
                """Leadership starts with making it easier for people to do good work. Explain the goal, the reason it matters, and what a successful result looks like.

Agree on responsibilities and how the team will share progress. Invite questions early so misunderstandings can be resolved while they are small.

Try it: write a short team goal and list two signs that would show the team is making progress.""",
                20,
            ),
            (
                "Listen and give helpful feedback",
                """Active listening means giving someone your attention, asking open questions, and checking that you understood their point before responding.

Useful feedback is timely, specific, and focused on an action or outcome. Describe what you observed, explain its effect, and discuss a practical next step.

Try it: prepare one example of feedback using the pattern “I noticed…, the impact was…, next time we could…”.""",
                20,
            ),
            (
                "Support growth through regular check-ins",
                """A short, regular check-in can help a colleague share progress, obstacles, and learning goals. Ask what is going well, where they need support, and what they want to try next.

Agree on one achievable action and follow up when you said you would. Consistent support builds confidence and accountability.

Try it: plan a 15-minute check-in with three questions and one clear follow-up action.""",
                20,
            ),
        ),
    },
    {
        "slug": "digital-confidence-at-work",
        "title": "Digital Confidence at Work",
        "category": "Digital skills",
        "summary": "Work confidently with online files, collaboration tools, and digital safety.",
        "description": (
            "Build practical digital habits for everyday work. Organize files, "
            "collaborate in shared spaces, communicate clearly online, and protect "
            "your accounts and information."
        ),
        "level": Course.Level.BEGINNER,
        "duration_hours": 4,
        "lessons": (
            (
                "Organize files and work in the cloud",
                """Use a consistent folder structure and descriptive file names so you and your colleagues can find the latest work. Shared cloud documents can support collaboration, but check who has access before sharing.

Use version history when you need to review or restore earlier changes. Avoid keeping important work only in a personal downloads folder.

Try it: create a simple folder structure for a project and agree on a naming pattern for shared files.""",
                20,
            ),
            (
                "Collaborate and communicate online",
                """Choose a communication channel that fits the task: a shared document for joint editing, a message for a quick update, and a meeting when discussion is needed.

Keep messages clear by stating the context, the action needed, and the deadline if there is one. Use comments and mentions thoughtfully so teammates can focus.

Try it: rewrite a vague message as a concise update with context and one clear request.""",
                20,
            ),
            (
                "Protect your accounts and information",
                """Use a unique password for each important account and enable multi-factor authentication where available. A password manager can help you store strong passwords safely.

Be cautious with unexpected links or requests for sensitive information. Confirm unusual requests through a trusted channel, and share documents only with people who need access.

Try it: review the sharing permissions on one practice document and remove access that is no longer needed.""",
                20,
            ),
        ),
    },
    {
        "slug": "clear-and-confident-communication",
        "title": "Clear and Confident Communication",
        "category": "Communication",
        "summary": "Share ideas clearly, listen actively, and make meetings more useful.",
        "description": (
            "Develop practical communication skills for everyday teamwork. "
            "Structure a clear message, listen for understanding, and contribute "
            "to focused, inclusive conversations."
        ),
        "level": Course.Level.BEGINNER,
        "duration_hours": 4,
        "lessons": (
            (
                "Structure a clear message",
                """A clear message starts with its purpose. Decide what your audience needs to know or do, then put the most important information first.

Use plain language, short paragraphs, and concrete details. For a request, explain the context, the action needed, and when it is needed.

Try it: turn a long update into three points: what happened, why it matters, and what should happen next.""",
                20,
            ),
            (
                "Listen to understand",
                """Listening well is an active skill. Give the speaker time to finish, notice the key points, and ask a question if something is unclear.

You can check your understanding by briefly reflecting back what you heard. This gives the other person a chance to correct or add context.

Try it: practice summarizing a colleague’s idea in one sentence before offering your own view.""",
                20,
            ),
            (
                "Make meetings focused and inclusive",
                """A useful meeting has a purpose, an agenda, and a clear outcome. Share background information in advance when people need time to prepare.

Invite input from everyone, make space for different perspectives, and finish by confirming decisions, owners, and next steps.

Try it: draft a 20-minute meeting agenda with one goal, two discussion points, and a decision to record.""",
                20,
            ),
        ),
    },
    {
        "slug": "everyday-wellbeing-and-resilience",
        "title": "Everyday Wellbeing and Resilience",
        "category": "Wellbeing",
        "summary": "Build healthy work habits, manage pressure, and support sustainable routines.",
        "description": (
            "Explore practical habits that support wellbeing at work. Notice "
            "sources of pressure, create helpful boundaries, and identify "
            "constructive ways to ask for support."
        ),
        "level": Course.Level.BEGINNER,
        "duration_hours": 4,
        "lessons": (
            (
                "Notice your energy and working patterns",
                """Wellbeing can be supported by noticing which activities help or drain your energy. A simple reflection at the end of the day can help you spot patterns.

Plan focused work around your priorities and allow short pauses between demanding tasks. Small, realistic adjustments are easier to sustain than a complete routine overhaul.

Try it: for three days, note one activity that gave you energy and one change that could make your workday more manageable.""",
                20,
            ),
            (
                "Manage pressure with healthy boundaries",
                """When priorities compete, clarify what is most important and discuss trade-offs early. Communicate your capacity honestly instead of silently accepting more work than you can complete.

Boundaries can include focus time, regular breaks, and an agreed time to stop work. Teams can support each other by making expectations explicit.

Try it: write a respectful sentence you could use to ask which of two urgent tasks should take priority.""",
                20,
            ),
            (
                "Build resilience and find support",
                """Resilience is not about ignoring difficulties. It can mean taking a moment to pause, identifying what is within your control, and choosing one useful next action.

Talk with a trusted colleague or manager when you need work-related support. If you are experiencing ongoing distress, consider reaching out to an appropriate health professional or support service.

Try it: identify one trusted person or workplace resource you could contact if you needed support.""",
                20,
            ),
        ),
    },
)


class Command(BaseCommand):
    help = "Create or update sample coding, leadership, digital skills, communication, and wellbeing courses."

    def handle(self, *args, **options):
        created_count = 0
        updated_count = 0
        for course_data in SAMPLE_COURSES:
            course_data = dict(course_data)
            lesson_data = course_data.pop("lessons")
            _, created = Course.objects.update_or_create(
                slug=course_data["slug"],
                defaults={
                    **course_data,
                    "enrollment_limit": 100,
                    "is_featured": course_data["slug"]
                    in {
                        "python-programming-foundations",
                        "django-web-development",
                        "everyday-leadership",
                        "digital-confidence-at-work",
                        "clear-and-confident-communication",
                        "everyday-wellbeing-and-resilience",
                    },
                    "is_published": True,
                },
            )
            if created:
                created_count += 1
            else:
                updated_count += 1

            course = Course.objects.get(slug=course_data["slug"])
            for order, (title, content, duration_minutes) in enumerate(
                lesson_data,
                start=1,
            ):
                CourseLesson.objects.update_or_create(
                    course=course,
                    order=order,
                    defaults={
                        "title": title,
                        "content": content,
                        "duration_minutes": duration_minutes,
                    },
                )

        self.stdout.write(
            self.style.SUCCESS(
                f"{len(SAMPLE_COURSES)} sample courses with lessons ready: "
                f"{created_count} created, {updated_count} updated."
            )
        )
