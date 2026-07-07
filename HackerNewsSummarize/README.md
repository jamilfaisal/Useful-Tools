# Hacker News Daily Companion

A daily Hacker News companion that helps you stay connected to software engineering culture without spending an hour reading Hacker News every day.

## Overview

This project fetches recent Hacker News stories, filters them by popularity, downloads complete comment trees, and generates organized context files for ChatGPT analysis. The goal is to quickly identify which discussions are worth your time and get meaningful summaries of the ones you don't want to read in full.

## Philosophy

- **Python** for deterministic work (fetching, cleaning, organizing data)
- **ChatGPT** for judgment (understanding discussions, synthesizing opinions, identifying important insights)

## Daily Workflow

Every morning, run:

```bash
python -m src.daily
```

The script will:

1. Fetch recent Hacker News stories using the official Firebase API
2. Look back a configurable number of days (default: 1)
3. Ignore jobs, polls, deleted stories, and dead stories
4. Filter stories based on popularity (configurable threshold)
5. Download complete recursive comment trees
6. Cache downloaded items locally
7. Remember which stories have been processed
8. Generate output folders with context and prompts

## Output Structure

```

output/
├── index.html
├── sqlite-release/
│ ├── context.md
│ └── prompt.md
├── ai-coding/
│ ├── context.md
│ └── prompt.md
└── redis/
├── context.md
└── prompt.md

```

### index.html

A simple static HTML page (no backend, no React, no JavaScript framework) that displays:

- Story title
- Points
- Number of comments
- Original article link
- Hacker News discussion link
- Link to open the story folder

### context.md

Contains all the context ChatGPT needs:

- Story title, URL, Hacker News URL
- Story score and comment count
- Story text (if present)
- Complete comment tree with nested replies
- Cleaned HTML (no deleted/dead comments)

### prompt.md

Reusable prompt for ChatGPT that instructs it to act as your personal Hacker News editor, explaining:

- What happened?
- Why was this story popular?
- What was the discussion actually about?
- What were the strongest arguments?
- What were the strongest counterarguments?
- What interesting technical insights came from experienced engineers?
- What was the overall community sentiment?
- Which comments are genuinely worth reading?
- Should you spend more time reading the original thread?

## Design Goals

Optimize for staying informed about software engineering culture:

- What happened yesterday?
- Why was it important?
- What did experienced software engineers think?
- Where did people disagree?
- What are the important technical takeaways?
- Which discussions are actually worth your limited time?

## Requirements

- Python 3.10+
- `requests` library

## Installation

```bash
pip install requests
```

## Configuration

Edit the configuration variables in `daily.py`:

- `DAYS_TO_LOOK_BACK`: Number of days to look back (default: 1)
- `MINIMUM_SCORE`: Minimum points threshold (default: 100)
- Or use percentage-based filtering (top 10% by score)

## License

MIT License
