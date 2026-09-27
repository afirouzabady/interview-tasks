**Subject:** Technical task — senior Python role

Dear candidate,

Thanks again for your time. Here's the technical task.

**The short version.** Inside is a small internal service that listens for payment
events from our payment provider and keeps track of how much money each seller is owed.
It runs, its tests pass, and its numbers are wrong — our finance colleague can't pay
sellers because our totals don't match the provider's official report. Nobody currently
on the team wrote this service.

Your job is to work out why the numbers are wrong, fix what matters most, and tell us
what you found. We haven't told you what the bugs are — figuring that out is the task.
You'll find the real event stream from the day in question and the provider's report
showing what the totals should be, so you can check your own work.

**Two hours.** Start whenever suits you. We'd genuinely rather see what you do with two
hours than have you spend a weekend on it.

**Please use AI tools.** Cursor, Claude Code, Copilot, whatever you normally reach for.
We use them daily and we're not testing whether you can work without them. We do ask for
a few bullets on where you used them and where you overrode them — there's a file for it.

**One important thing:** the task is deliberately bigger than two hours. Nobody fixes
everything, and you're not expected to. Fixing two things properly and clearly explaining
what you'd do about the rest scores better with us than touching everything
superficially. If you decide to skip something on purpose, just say so — that reads as a
finding, not a gap.

**What to send back** (zip this folder again, or send a git bundle):

1. Your code changes, with `pytest` passing.
2. `DECISIONS.md` — what you found, what you fixed, what you left and why. Two pages
   max. This is the part we read first.
3. Tests for whatever you judged critical. We're not counting coverage.
4. `REVIEW_ME.md` — there's an open pull request from a colleague in there. Add your
   review at the bottom and say whether you'd approve it.
5. `AI_LOG.md` — a handful of bullets.

Everything you need, including setup instructions, is in `README.md` next to this file.
Start there, and read `CONTEXT.md` before you touch the code.

If anything is unclear or the setup won't run, message me — that's on us, not a test.

Best,
Aidin Firouzabadi

