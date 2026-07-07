Project Vision

The project is a daily Hacker News companion that helps me stay connected to software engineering culture without spending an hour reading Hacker News every day.

It is not trying to replace Hacker News, personalize recommendations, or become a web app. It simply helps me decide which discussions are worth my time and summarizes the ones I don't want to read in full.

The philosophy is:

Use Python for deterministic work (fetching, cleaning, organizing data).
Use ChatGPT for judgment (understanding discussions, synthesizing opinions, identifying important insights).

Because I already pay for ChatGPT Pro and don't want to pay separately for the OpenAI API, the workflow intentionally includes one manual step: uploading files into ChatGPT.

Daily Workflow

Every morning I run:

python -m src.daily

The script should:

Fetch recent Hacker News stories using the official Hacker News Firebase API.
Look back a configurable number of days (default: 1).
Ignore jobs, polls, deleted stories, and dead stories.
Include Ask HN and Show HN posts.
Filter stories based on popularity (points). The threshold should be configurable (e.g. top 10% by score or minimum score).
Download the complete recursive comment tree for each selected story.
Ignore deleted/dead comments.
Preserve reply hierarchy.
Cache downloaded items locally.
Remember which stories have already been processed so they aren't processed again on future runs.
Output Structure

The script should generate an output folder similar to:

output/
index.html

    sqlite-release/
        context.md
        prompt.md

    ai-coding/
        context.md
        prompt.md

    redis/
        context.md
        prompt.md

index.html

This should be a simple static HTML page.

No backend.

No React.

No JavaScript framework.

Just clean HTML/CSS.

Each story should display:

Title
Points
Number of comments
Original article link
Hacker News discussion link
A button or obvious link to open the story folder

The goal is to quickly browse yesterday's important discussions.

context.md

This file contains all the context ChatGPT needs.

It should include:

Story title
Story URL
Hacker News URL
Story score
Number of comments
Story text (if present)
Complete comment tree
Nested replies preserved
Cleaned HTML
No deleted/dead comments

This file contains no summaries or AI-generated content.

It is simply well-organized context.

prompt.md

This file contains the reusable prompt I'll paste into ChatGPT alongside context.md.

The prompt should instruct ChatGPT to act as my personal Hacker News editor.

Its goal is not to summarize mechanically.

Its goal is to make me feel like I spent an hour reading the discussion.

For each thread I want ChatGPT to explain:

What happened?
Why was this story popular?
What was the discussion actually about?
What were the strongest arguments?
What were the strongest counterarguments?
What interesting technical insights came from experienced engineers?
What was the overall community sentiment?
Which comments are genuinely worth reading (3–5 comments, with reasons)?
Should I spend another 20–30 minutes reading the original thread, or have I already gotten most of the value?

The output should prioritize explaining what software engineers collectively learned, not simply summarizing every individual comment.

Design Goals

The project should optimize for staying informed about software engineering culture.

Specifically, I want to know:

What happened yesterday?
Why was it important?
What did experienced software engineers think?
Where did people disagree?
What are the important technical takeaways?
Which discussions are actually worth my limited time?

I care much more about the discussion than the linked article itself.

In practice, I usually read the headline and comments first, and only read the article if I'm especially interested.

The only manual step should be uploading context.md and prompt.md into ChatGPT Pro.
