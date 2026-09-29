# SaaS UI: The Checklist That Makes Software Look Like a Product People Pay For

Oliver (formerly of Response AI and other software tools he has since exited) on the SaaS UI concepts you need so you do not build software that looks garbage.

---

## Why this matters

The gap between a vibe-coded app and a product people pay for is never really the code.

You can now vibe-code pretty good, well-functioning apps. The difference is **interface decisions** and **design decisions**. You do not need taste. You need a checklist so your apps do not look terrible.

Bad UI has a long lineage: Salesforce and SAP were powerful tools that looked awful. New software ships every hour. Around **88% of users abandon the app and do not pay after one poor experience**.

Every vague icon and every design decision that does not work is a thorn in their side. They leave. People are even more picky nowadays.

---

## Users are not tourists in your maze

You have built the maze. They have never seen it.

That is why tools like **Hotjar** or **PostHog** are recommended. You spend months in the app and know exactly where everything is. Users are not tourists wandering your interface. They buy what you build so they can create something or **get a job done**.

Just because you love the app and think it is cool does not mean people care about it. **All they care about is the result.**

Hold their hand far more than it feels necessary. Guide them down the right routes.

---

# Part 1 — Undoing what the AI gave you as a UI

Cursor, Lovable, Bolt, and similar tools will build something functional in an afternoon. They will also apply **the same defaults every single time**.

It is getting better. First-glance output is not as bad as it used to be. People who look at software all day still recognize those defaults instantly. That is when you realize it is vibe-coded slop.

These are also **the cheapest fixes in the whole deck**. Most take under an hour.

### An intentionally bad landing page (what “slop” looks like)

A dreadful vibe-coded landing page might include:

- Emojis as decorations
- Glow shadows
- Clashing gradients
- Differing font sizes
- Differing **border radii** on buttons (some circular, some square)
- Things that are not centered (for example, “Watch demo” not centered inside its button)
- Feature boxes of different sizes with different radii (one square, one circular)
- Clashing images and clashing text
- Loads of emojis

This example is a joke. Real vibe-coded work does not usually look *this* bad. It still looks pretty bad.

---

## Kill emojis. Use a real icon set.

The fastest ~30 minutes — and some of the most important time you will spend on the UI — is the design and the **packages you use to build the app**.

Install **Phosphor** or **Lucide** (also **Feather**). Both Phosphor and Lucide are free. There are thousands of icons that look nice and **hold the line**: sizing, shape, and color mix in with the rest of the app if you do not completely lose touch of the design and start doing random stuff.

Icons are small and not a huge part of the screen. They are still one of the **most tasteful** aspects of the app.

### Icons versus emojis

Swap emoji-as-icon decisions for a real icon set (Lucide, Phosphor, or Feather).

- Same meaning
- Instead of a garbage emoji for “delete,” use a simple icon
- Reduces clashes
- Reduces friction
- Makes the app look more grown up and more palatable for the user

---

## Never let the AI choose your colors

AI will pick bright and clashing. Every AI tool defaults to a **saturated blue or purple**, then adds a **second bright accent that fights it**. It reads as a template because it is one. It looks dreadful.

**Pick a restrained base and one accent. Muted works.**

Stripe’s palette is so boring, and it is one of the most trusted interfaces in software. With simplicity, grayscale, whitespace, less detail, and less color comes **trust**. People trust simplicity. They do not trust glowing buttons, purple gradients, and everything fighting for attention like a PowerPoint from when you were 10 years old.

### Let data carry the color

- A dashboard full of colored buttons looks cheap.
- The same dashboard with **muted chrome** and color reserved for **charts and statuses** looks expensive.
- **Only reserve color for things that are trying to show something.**

### Two feature-section examples

**Left (bad):** Thick, challenging text with a rocket emoji: “Supercharge your workflow,” “blazing fast,” “smart targeting,” and so on. This looks great if you are 5 years old.

**Right (good):** Muted and minimal version of the same landing / feature section.

To some people the right looks boring. **We are not here to excite people with the design of our software.** We are looking to **guide them down the path to getting the result they want**.

- Left screams that you do not know how to code, do not know how to build software, and what they are about to buy is going to be terrible.
- Right: “boring” typically means the product will speak for itself. It does not mean boring. It means **muted and minimal**.

The right is a muted **Attio** or **Airtable**-style palette:

- Near white
- Thin borders
- No shadows

Attio is described as one of the favorite websites in this talk. Example copy: “Welcome to Agentic Revenue.” Attio is the CRM that builds pipeline, and so on. Ignore the animations (this is a very successful company). Notice:

- Pretty much **mostly grayscale**
- Color only on important things, such as **ICP score** (green, but very muted, with a very thin green border)
- **All button radii the same** — not square versus circular. Always the same square-ish / circular-ish button
- Logos in color (enterprise-grade feel)
- Simple blue and simple white for “Send email”
- Things that are not super important but still a feature: **white** (for example, “Save draft”)
- Decisions you do *not* want them to take: **less visible** (for example, “Discard”)

With an email to Maya White:

- You are looking to **send** the email
- Far less looking to **discard**
- Middle ground: **save as draft**

That leads the user down the path of completing the task.

On the landing / product UI:

- Simple colors that are not clashing
- Muted, pastel-y colors for different things
- No additional colors
- **Icons** to say what something is

Example: instead of “Company Lumio AI,” a little icon. Same for the date (September 30th — when Lumio AI came into this pipeline). A dollar sign for dollars. A simple old-school Facebook-style icon.

These are design choices. They make the app look far more beautiful than a harsh layout that tries to do too much in too little time.

---

## Never let the AI choose your layout either

On a shoddy dashboard of different tools you get a chunky background shadow. The **clearest tell of a generated app is repetition**.

AI will put the **same four KPI cards** on your dashboard, your analytics page, *and* your billing page, because it typically has **no memory of what it already built**.

**Each page should answer one question.**

- If you are on the teams page, you do not need analytics.
- If you want analytics, go to the analytics page or the dashboard.

**Audit every page.** Ask: what is the *one thing* someone would go to that page for? **Delete anything that is not that.**

---

## Fix the cards first

Biggest visible change for the least work. AI is worst at **dense, repeated components**. A list of cards is where it dumps every button, chip, timestamp, and so on.

Compress:

- Collapse the row of buttons into a **triple-dot (kebab) menu**
- Turn text chips into **icons** instead
- Push the **number that actually matters** to the right
- Move everything else out of the way

Same information, about a **third of the noise**. Match what contains the data with what the person is looking for. Do not put random stuff on a page.

Example: a **guests list**. It does not say how many guests have come in in X period of time. It does not tell you total guests over the last year. It is a list of guests because it is a tab called **Guests list**.

If your form has four fields and the slide-out panel is empty, a **centered modal** is probably the better choice.

Figure out **what the user is there for** inside that tab, then design around that.

---

## Density and repetition (worked example)

**Left (too much always visible):** Sarah Chen, product designer, the project she is running, in progress, high priority, a bug that needs sorting on the front end. Marcus, web, already done, medium, backend, and so on. Too much color and too much stuff.

Strike the balance: **only use color when it symbolizes something or helps with an action.** Do not use color everywhere for every action or every symbol in the app.

Yes, it is important that Sarah Chen’s project and bug is high priority. You do **not** need that among four other buttons with different colors.

**Right:** Collapsed, quiet. A three-dot menu if you want more. We still know Sarah Chen is in progress and high priority.

A middle-ground option: a tiny dot for “in progress” (blue or yellow) and high priority as a red dot — or something like that. Maybe do not mix the two: **progress as the words “in progress,” priority colored.** That is much different.

---

## AI decorates. Your job is to inform.

Look at what every one of those fixes has in common:

- Emojis
- Bright colors
- Repeated KPIs
- Overloaded cards
- Empty panels
- Random colors

Each one is the tool adding **visual material where information should be**.

AI optimizes for a screen that **looks finished**. You need a screen that **helps someone finish something**.

Ask of every element (including when you ask AI): **Does this help the user complete the job they came here for?** If it is just decoration, get rid of it.

---

# Part 2 — The laws that do not change

Interface trends turn over every few years: skeuomorphic, flat, neomorphic, glass, the newer age of whitespace and tabled stuff like Attio.

Underneath the fashion sits a **small set of principles**. Get those right and the app looks competent and people will trust it.

**When there is nothing left to remove, that is when things are perfect.**

### Example: Capern

Capern was basically just a table. The table showed you **investors** and that is it. You could filter by investor stage, by how much they had invested, and so on. As simple as that.

The instinct with a front end is to see **how much you can fit on it**. That instinct is wrong.

The real question is: **how little can you get away with while still helping the user complete the job?**

Before you add anything else, **try deleting stuff**.

---

## Write the rules down or you will break them

If a button says **Delete** on one screen and **Remove** on another, you have created friction. Users will never report this. They will just find the app annoying as hell. You will never see why people are quitting when it is little things that make it look amateur.

Write **one page**. Give it to AI. A markdown document covering:

- Text sizes
- Button height
- Spacing steps
- The **verb you use for actions** (so it does not say “remove” in one place and “delete” in another)

The AI changes things up because it sometimes **forgets**. Paste the document into your AI tool and say: **these are the rules.**

---

## Consistency and friction

Humans like to **pattern match**.

Naming the same action Delete in one place and Remove in another **forces a reread**. Over time it looks awful. You literally get **Remove, Delete, and Trash**. Consistently, it should all be **Delete**.

Random font sizes and the like, without consistency, create friction.

### Bad vs consistent scale

**Awful:** Different fonts. Some in capital letters, some not. Some muted in gray. This is what many apps look like.

**Consistent scale (which AI sometimes gets wrong):**

- “Welcome back” in bold — that is just a message
- “Here’s what’s happening today”
- Underneath: one capital-letters title for the section — “Recent activity”
- “Three tasks completed this week”
- “Updated 2 minutes ago”

**Hierarchy tells the user where to look:** size, weight, color, space, and so on.

Every screen is a **sentence**. Something has to be the **subject**. If everything is the same size and weight, the user has to read all of it to find the thing they want.

**Basecamp** does this with almost nothing: bold titles for projects, muted secondary text. That is the entire system. It is like reading a simple document.

**Airtable** took spreadsheets — the most boring thing on Earth — and made rows scannable with color-coded statuses.

**Practical version:** pick the **one element per screen that matters** and turn the volume down on everything around it.

---

## Start with intent

Most people open a blank page and start thinking about cards, icons, where the sidebar goes. That is starting at the **end**.

Start here instead: **What did the person arrive to do?**

### Capern example

When they log in:

- Here is the database
- Here is how you can filter by the leads you need
- It shows how many contacts
- It asks you to export them
- There is a sidebar with stuff
- **Credits in the bottom left** so you know exactly how many leads are left that you can export
- Filters above with specific filters
- A **key / legend** that says what the specific filters do

As simple as that.

### When a second intent appears

Someone who wants a holiday but does not know where is **browsing, not searching**. That is what **filters** are for.

**Functionality expands when intent expands — never because you had space to fill.**

You only add stuff when you realize the user needs to do more stuff. You do **not** think “this could be cool for the user” and add a random thing. That is putting words in their mouth.

---

## Design for the ugly data, not the demo data

Your app looks great because you filled it with tidy example data: short names, neat numbers. You need to put **real data** in the app to see how bad it looks.

Decide the rules now:

- Truncate long strings with an **ellipsis** after, say, **15 characters**
- Put icons on a **solid circle** so they survive any background
- Design **empty states** deliberately
- Have **loading states**
- Have **error messages**

All of these are things a **new user** is going to see. You are not seeing them because you are in a perfect bubble while designing the app.

---

## Onboarding

The moment after someone starts a trial is when they are **least patient** and **most critical**. You have **minutes, sometimes seconds**, as opposed to days. You used to have days because people were more patient.

**Do not force tutorials.** Forced tutorials feel like a lecture. People click through them without reading just to get to the app itself.

**Progressive onboarding wins:**

1. One obvious action that gets the job done
2. Then reveal the next when they finish it

Make the first step **impossible to miss**.

On one of Oliver’s apps:

- The primary card has a drop shadow
- It is greener than everything else around it
- It would say **Start here**
- Add a **progress bar** so they can see the finish line
- When they have finished it, make it a game: “well done,” confetti, that kind of thing

It works with **Paper Schedule**. When you connect your first account (X, Facebook, Instagram):

- Confetti comes up
- You get an email: “Well done. You connected your first account. Connect the next one.”

It is celebrating simple things and celebrating the user **doing the job**.

---

## Speed is also an aesthetic

A **1-second delay costs 7% of conversions**.

Showing something **immediately** is the fix — not always faster code.

Open LinkedIn and search a name. For a split second you get **gray skeleton bars**. Nothing loaded faster. It just **felt** like it did.

If it is blank, people think it looks awful.

A related trick on iOS / iPhone apps: some people use the **Apple spinner** immediately instead of their own design spinner. When it is Apple’s spinner, the user thinks it is Apple / the iPhone being slow, but it is actually **your** app. These kinds of details make the app **feel** faster.

Add:

- Skeleton screens
- Skeleton buttons
- Skeleton blurs
- Wherever you fetch data

A **progress indicator** for anything over a second.

Something **playful** for genuinely long jobs — for example an animation of a dog juggling. PostHog does this well: a hog / hedgehog walking around the screen when you are doing stuff. Little things that are funny.

**Users do not need speed. They need evidence that something is happening.** People are okay to wait two seconds for something. They are **not** okay to wait two seconds when it is blank.

---

## Show them value in numbers

The most underused retention feature in B2B is just **showing people what they are achieving**.

**Value tracker.** B2B buyers (business buyers) must justify the subscription to a boss or to themselves. If the app does not show what you are achieving for them, they will **guess they are not achieving much**. They do not guess higher. They do not think “I reckon I’m doing loads of good stuff with this app.” They always think they are doing nothing.

It is a **scoreboard**, not just a tool. Example: “Your impact this month”

- You’ve saved 30 hours
- You’ve automated 100 tasks
- You’ve found 26 leads
- You’ve generated 18K in revenue

Show what they have done and what they have won **on the dashboard** instead of leaving it to guesswork.

This is easy. In Paper Schedule: “You’ve posted 25 times and saved 10 hours.” Simple. People always look at that. People get confetti when they hit a certain milestone. So simple, so effective.

---

## Some buttons should be hard to press

There is **ethical friction** and the **Zeigarnik effect**.

If a user clicks Delete and something vanishes, two bad things happen:

1. They cannot undo the mistake
2. They are not certain it worked because it happened too fast — so they refresh to check, and it is gone

For anything **destructive, expensive, or final**, add a confirmation: “Are you sure?”

You think this is friction. Think about **certainty for the user** instead.

**Type the name to confirm** for the truly serious ones. Example: “Are you sure you want to delete this server?” That is big. Yes, Delete — type the name of the server.

**Supabase** does this: you cannot delete a database without typing the name of the database. It is tedious. It is made to be tedious because it is the **danger zone**.

Show a **clear completion state**: confetti, or a tick. On Paper Schedule there is a spinner and then a tick or a thumbs up.

That is the Zeigarnik effect: **unfinished actions nag at people**. The task may have finished, but if people think “what just happened?” they will be bugged by it.

---

## Animation has to earn its place

No animation inside the app unless you are doing confetti and the like for things that are **completed**.

Everything else is cheesy:

- Scrolljacking
- Elements flying in from the edges
- Parallax
- Fading in

The only fade-in used here is **skeleton loaders**, so people know things are happening.

Choose a **Load more** button over **infinite scroll** if it gives the user control. It lets them actually **reach your footer**, which infinite scroll makes impossible. People scroll forever. It looks really bad. It can make their computer slow.

**The test is simple: does this motion tell the user something? If it does not, do not add it.**

---

## Confirm, then complete (example)

**Bad:** Click Delete and it disappears. The row is gone. No confirmation, no undo, no proof, no bin to check.

**Better — confirm then complete:**

- Delete the Q3 launch plan
- This removes the project and all of its tasks
- This cannot be undone
- A title and a subtitle that says what it does
- Type **delete** to confirm
- You delete the project
- Then: **Project deleted**
- **5 seconds to undo**

Very simple.

---

# Landing pages

The landing page is super important. It is where a vibe-coded product **loses most of its customers**.

Design landing pages that have:

- A clear-cut reason for you visiting
- A clear-cut reason to buy
- A clear-cut thing that is being sold

There is a quality bar on SaaS landing pages that visitors / readers **trust mostly without noticing**. The jump from generic to professional is a **known path with a couple of moves**.

Landing pages are about **presentation, not complexity**.

### Get out of template territory

**Kill the alternating layout.** Typically: text on the left, image on the right, repeating down the page. That is a signature of vibe-coded slop.

Instead:

- **Stack the hero** and then let it breathe
- Delete every **stock photo**
- Replace it with a **screenshot of your actual product**
- Make sure **all call-to-action buttons say the same thing**

Never mix “Get started” / “Try a demo” / “Get the demo” / “Get started” / “Try a free trial.” They should all be the **same thing**. Same labels mean the same places. That is the mental model you want: **simplicity**.

### Example: Paper Schedule landing page

- Headline: “Your AI GTM distribution agent from content to qualified pipeline”
- Subtitle in a softer font: Paper Schedule content finds you leads
- CTAs: **Start for free** or **Book a demo**
- A tasteful, muted animation to signify this is the main section to pay attention to — the **three big features**
- No silly big designs or videos
- Just three sections that say what will be achieved
- Underneath: more animated stuff that shows each thing you will achieve **in motion**
  - The content agent
  - Then the Paper cold email agent working: leads filling in, enrichments happening, cold email sequences being written (animated)
- Reviews of the app
- Below that: nice watercolor-style designs of the app itself (not muted in the “gray” sense — watercolor)
- You can go through this in **steps 1 to 3** — that is how you are onboarded:
  1. We map your entire pipeline
  2. We give you daily content
  3. We get you leads
- Simple because it is **three steps**. You do not need 20 steps.
- Finally, one more thing that just says here’s what it does
- Then **pricing** (one pricing)
- Then **FAQs**
- Then a demo thing at the bottom

Simple enough. People who want this are going to know what it is. From there they are in the process of: what do I need to do, and how do I sign up?

### Where it starts to look expensive

Curate the visual, then add depth.

- Stop showing the **whole dashboard**
- **Zoom into the one part** that proves the point of that section
- A full screenshot makes the reader **hunt** for what they want on the landing page
- A **cropped** one tells them exactly what to notice
- Swap a row of four identical cards for a **bento grid**, so different content gets a different amount of room
- Add the product-designer touch:
  - A little badge
  - A row of customer logos
  - A **mega menu** on the navbar

A mega menu quietly tells a visitor the product has **depth worth exploring**.

### Copy: good vs great

The difference between good and great is the copy shifting from **what it does** to **how it helps**.

- “Collect and analyze your data quickly” is descriptive and fine
- “Turn your data into decisions” is the same feature **promising an outcome**

That rewrite is the **biggest single jump on the page**.

Then the motion gets precise:

- A blur as one panel transitions to the next
- A menu that stays open and slides sideways instead of closing

None of this needs custom illustration or 3D or paying a freelancer. It is all the **same components you already have**. You already designed your app. You already know what it does.

---

# How to get all this without designing anything

Screenshot the apps you like and the websites you like. Go to **Dribbble** or **Mobbin**. Keep a folder. Every time you are going to build an app, upload all the screenshots to **Cursor / Lovable** and say: **this is exactly what I want. Copy this design.** It is as simple as that.

---

## Resources

If you want the full playbook: **roseorld.dev** — all the UI prompts used to make cute-looking software, the design rules, and the complete idea-to-exit book.

Any problems at all, get in touch. Next video next week.
