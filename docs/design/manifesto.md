# My Design Manifesto: How I Design Software That Feels Like Someone Cared

What I believe about design, and the rules I hold myself to. Most of what I build is web and SaaS, not Apple platforms. I have still taken most of my thinking from Apple, because their principles are about people, not pixels, and those principles work on any screen.

Distilled from:

- **Mike Stern** (Apple Design Evangelism, WWDC17): the timeless design principles: wayfinding, feedback, visibility, consistency, mental models, proximity, grouping, mapping, affordance, progressive disclosure and symmetry.
- **Lauren Strehlow** (WWDC18, *The Qualities of Great Design*): what quality is, why it matters, the four aspirations, and how real designers work.
- **Majo** (WWDC25): from idea to interface through structure, navigation, content and visual design.
- **Linda & Doug** (WWDC26, *Design Principles*): purpose, agency, responsibility, familiarity, flexibility, simplicity, craft and delight.
- **Chan, Shubham & Bruno** (WWDC25, *Liquid Glass*): materials, layering, adaptivity, tinting, legibility.
- **Oliver** (*SaaS UI*): the practical checklist that stops software from looking like vibe-coded slop.

Where these sources disagree, I show both views and say when each one applies. When it's a close call, I lean Apple's way.

---

## My creed

1. **I design for humans, not users.** "User" is clinical. It defines a person only by how they relate to my interface. "Human" reminds me that they're tired, distracted, stressed, imperfect, and also capable of kindness and joy.
2. **Design is making something with intention.** It isn't only how something looks or how it behaves. It is deciding what matters most to people and building only that.
3. **Every feature I add costs something.** It asks for people's **time, attention and trust**, and I can't afford to waste any of them.
4. **Choosing what to build is mostly choosing what not to build.**
5. **The goal isn't a beautiful app, an organised app, a simple app or a focused app.** Those all matter, but the real goal is to serve the people who use it and make their lives better.
6. **My job is to inform, not decorate.** A screen that *looks finished* is worth nothing. I want a screen that *helps someone finish something*.
7. **Simple is not the same as minimal.** Hiding everything behind one menu looks minimal and isn't simple. Simple means **exactly enough**.
8. **Consistency takes self-control and restraint.** When everything matches, people sense integrity.
9. **Quality is the result of time, effort and care.** It is considered, not random. It has to be earned; I can't claim it with a label.
10. **Good design disappears.** People notice a badly designed interface and don't notice a well-designed one. If people are thinking about my UI, I've already lost a little.
11. **People should sense the humanity of whoever made it.** That is the highest compliment software can get.

---

## Why this matters

People have four kinds of need, and a well-designed product meets all of them:

| Need | What the product must do |
|---|---|
| **Safety and predictability** | Make it easy to predict what an action will do. Feel stable, solid and trustworthy. |
| **Knowledge, meaning and understanding** | Give information that is clear and helpful so people can make informed choices. |
| **Getting things done** | Streamline workflows so people can reach their personal and professional goals quickly. |
| **Beauty and joy** | Be pleasing, enjoyable and sometimes delightful. |

The commercial reality backs this up. New software ships every hour, and people are pickier than ever. Oliver's figure: around **88% of users abandon an app and never pay after one poor experience**. Every vague icon and every inconsistent label is a small thorn. Users will never report those thorns. They will just find the app annoying and leave, and I'll never see why.

The gap between a vibe-coded app and a product people pay for is almost never the code. It's the **interface and design decisions**.

Quality is also about survival. People instinctively seek out quality because things that are well made don't hurt them. When every part of an experience meets their expectations, they **trust** it. Trust comes from a product keeping its promise, over and over, in every detail.

> *"You're very aware of an interface which has been poorly designed, and you're not at all aware of an interface which has been well designed."*

---

## How I use this document

- **Part 0** covers what I think design and quality are.
- **Parts 1–10** are the principles and rules, in the order I apply them: purpose → structure → navigation → content → visual → interaction → words → people → responsibility → delight and craft.
- **Part 11** is for landing pages.
- **Part 12** is how I work: my process.
- **Part 13** settles the disagreements between the sources.
- **Part 14** is my rules sheet. I paste it into any AI tool I build with and say *these are the rules*.
- **Part 15** is the audit checklist I run on every screen before shipping.

A warning to myself: **there is no formula.** Leaning into one principle often means compromising on another. Too much feedback is annoying. Too much visibility is distracting. Too much progressive disclosure makes workflows slow. Designing is mostly about resolving those tensions with judgment, and that judgment gets easier the better I know the fundamentals. These principles are my North Star, not a vending machine.

---

# Part 0 — What design and quality actually are

## Design principles tell me *why*, not *how*

Technique and process matter, but they don't produce great design on their own. Great design comes from understanding how people perceive the world, process information, make decisions and communicate. That understanding is universal and timeless. It applies to graphic design, architecture, interiors, retail, cars, landscapes, and software.

Trends turn over every few years: skeuomorphic, flat, neumorphic, glass, the current whitespace-and-tables style of tools like Attio. Underneath the fashion sits a **small set of principles**. If I get those right, what I build looks competent and people trust it, whatever the trend.

## What quality means to me

From the designers Lauren Strehlow interviewed, quality is:

- **What we agree is good.**
- **Not random.** Nothing about it is slapped together. It is *considered* and organised, and it shows that someone thought it through.
- **Care and time.** It's better than something without quality simply because someone cared about it.
- **Felt before it's described.** People feel it and struggle to put a finger on it.
- **Like someone already thought of you.** Everything you need is easy to reach and easy to understand.
- **Painless.** Not mentally, physically or emotionally painful. Nothing makes you feel uncomfortable, stupid or inconvenienced.
- **Out of the way.** All your concentration goes to what you're actually trying to do: sharing a photo, finding the right song, closing a deal. None of it goes to the UI.

### The details give it away

In a recording booth, the gaps between wall panels are either perfectly even from top to bottom or they aren't. If they vary, you can tell it wasn't well crafted, even if you can't say why. Software is the same: a 13px gap next to a 16px gap, an icon one pixel off-centre, a button label not quite centred. **The small things are what show craftsmanship.**

### Two kinds of care

1. **Did I care enough to make it the best it could be?**
2. **Did I care about *your* experience?** Mine, my mum's, a neighbour's, someone's on the other side of the world. I have to take myself out of the equation and put myself in their shoes. It's not about liking my own design.

### Intentions are felt

Food cooked with love tastes different. If I intend to make something great and do everything needed to get there, people feel it. The reverse is also true: if I rushed the settings page because I didn't care, that feeling leaks into how people see the whole product.

### Quality is earned, not claimed

A pizza box that says "Our commitment is quality" convinces nobody. Being cool doesn't involve saying you're cool. **Every part of the experience communicates quality**, not only the UI: the landing page, the screenshots, the docs, the emails, how I answer support requests and reviews.

## My four aspirations

These feel almost unreachable, which is exactly why they're motivating:

1. **Simple.** It doesn't try to do more than it needs to, and what it does, it does really well. People are living real lives, on good days and bad days, and their mental energy belongs there, not in my interface. Software shouldn't be a burden.
2. **Stunning.** Polish means things line up exactly as intended, including how they *feel*: a swipe animation that tracks the finger precisely, a layout that looks visually perfect.
3. **Timeless.** I design to still look right in five years, not dated after one. **Durable over trendy.** A design that lasts saves time now and later.
4. **A positive effect on people's lives.** That might mean being accurate, being entertaining, or making someone's day a little easier. Would my product survive someone scrolling through their apps asking *"which of these actually make my life better?"*

---

# Part 1 — Before I draw anything: purpose and structure

Most people open a blank canvas and start thinking about cards, icons and where the sidebar goes. **That is starting at the end.**

## Start with intent

The first question is always: **What did this person arrive to do?**

Not "what would be cool", not "what can I fit", but what job they came to get done. People aren't tourists wandering my maze. I built the maze and know every corner; they've never seen it. They bought my product to **get a job done**, and all they care about is the result.

> Just because I love the app doesn't mean anyone else cares about it. They care about the outcome.

### The Capern example (Oliver)

Capern was basically a table of investors. Log in and you get:

- The database.
- Filters for the leads you need, with a key explaining what each filter does.
- A count of contacts.
- An export action.
- A sidebar.
- **Credits in the bottom left**, so you always know how many exports you have left.

That's it. The instinct is to see how much you can fit on a front end, and **that instinct is wrong**. The real question is: **how little can I get away with while still helping people finish the job?**

## Purpose: does this deserve to exist?

Before I sketch or write code, I ask whether each feature has a purpose. Every feature I add asks for time, attention and trust, so I justify each one:

- Who is this for?
- What job does it do for them?
- What happens if it doesn't exist?
- Is it worth what it costs in attention?

**Before adding anything, I try deleting something.** When there's nothing left to remove, it's done.

## Information architecture: Majo's process

Information architecture means organising and prioritising information so people find what they need, when they need it, without friction. I follow this sequence:

1. **Write down everything the product does**: features, workflows, nice-to-haves. At this stage I don't judge or cut anything.
2. **Imagine how someone else uses it.**
   - When and where are they using it?
   - How does it fit into their routine?
   - What actually helps them, and what gets in the way?

   I add the answers to the list.
3. **Clean up.**
   - **Remove** anything that isn't essential.
   - **Rename** anything that isn't clear.
   - **Group** things that naturally belong together.

What I learn from this: **if I'm not clear on what's essential, I can't communicate it in the product.** Simplifying sharpens the purpose and gives me a starting point for how people will find features and when they'll use them.

## Each page answers one question

The clearest sign of a generated app is **repetition**. AI puts the same four KPI cards on the dashboard, the analytics page *and* the billing page, because it doesn't remember what it already built.

- The Team page is about the team. It doesn't need analytics.
- For analytics, people go to Analytics or the dashboard.
- A Guest list is a list of guests. It doesn't need "guests this period" or "total guests this year". It's a list because the tab is called *Guest list*.

**I audit every page:** what is the *one thing* someone comes here for? Anything that isn't that gets deleted.

## Functionality grows when intent grows

Someone who wants a holiday but doesn't know where is *browsing*, not *searching*. That second intent is what filters exist for.

**I add functionality when I find that people need to do more, never because I had space to fill.** Adding something because "this could be cool for them" is putting words in their mouth.

## The 80/20 rule

Roughly 80% of a system's value comes from 20% of its functions, and roughly 80% of people use only 20% of the features. The exact numbers vary, but the point holds: **not all features and information are equally important.** That tells me what goes up front and what can go one layer down (see *Progressive disclosure*, Part 3).

## A responsibility check, even at this stage

Before I commit to a feature, I ask:

- How could this be misused?
- Who could be harmed by it?
- How do I prevent that?

If the risk to people's safety outweighs the value, **I don't build it.** (More in Part 8.)

---

# Part 2 — Navigation and wayfinding

## My whole interface is a wayfinding system

Airports are designed for people who are tired, jet-lagged, rushed and stressed, which describes a lot of people using software. Good wayfinding:

- Offers a complete, understandable list of general places to go.
- Gives the detail needed about what's in each place.
- Is contextual, getting more specific as you go deeper.
- Clearly shows where you are relative to everything else.
- Gives a clear **exit route**. It's comforting to know you can always get back somewhere familiar and start over.

### Every screen must answer these questions

| Question | What answers it on the web |
|---|---|
| **Where am I?** | Page title and header, the highlighted nav item, breadcrumbs |
| **What can I do here?** | Visible, clearly labelled page actions in the header |
| **Where can I go?** | Sidebar or top nav, links within the content |
| **What will I find when I get there?** | Clear labels, recognisable icons |
| **What's nearby?** | Sibling sections, related items, tabs |
| **How do I get out?** | Back button, breadcrumbs, Esc/Close on overlays, logo links home |

I go through the product **one screen at a time** and ask how well each one answers these. Where the answer is unclear, there's work to do.

## Primary navigation: the sidebar or top nav

On iOS this is the tab bar; for me it's usually a sidebar or top nav. It's always visible, so every main section is reachable from anywhere. (Liquid Glass even treats the tab bar and sidebar as **one navigation element that scales with the canvas**. I think about mobile bottom nav and desktop sidebar the same way: one system, not two.)

- **Keep it short.** Every extra item is one more decision and makes the product look more complicated than it is.
- **Merge sections that are really just groupings.** Majo's "Crates" was only a way of grouping Records, so it went inside Records. No need for both.
- **Navigation is for navigating, not for actions.** "Add" doesn't belong in the nav even if it's the main action. It goes inside the section where people will most likely use it, such as a "New record" button in the Records header.
- **Label everything explicitly.** People should know what's behind a nav item without clicking it and without skipping it because they aren't sure. Majo renamed "Swaps" and "Saves" to more direct labels.
- **Pair labels with familiar icons** from one consistent set. Icons back up meaning; they don't replace labels.
- **Show clearly where I am** with an active state on the current item.

### Don't hide navigation behind a hamburger (visibility)

Imagine the Clock app's tabs hidden in a hamburger menu: people would have far more trouble discovering what else the app does.

- **Desktop:** show the navigation.
- **Mobile web:** use a visible bottom bar or a short visible nav when possible. Use a hamburger only when there are genuinely too many destinations, and then make sure the current section is still labelled on the page.

## Every screen gets a header: title and actions

Majo's biggest fix was replacing a menu and a branding title at the top of the screen with a **toolbar**:

- **A title that names the screen**, not the logo and not a slogan. It sets expectations and keeps people oriented as they scroll.
- **Actions specific to this screen**, the ones people are most likely to want, placed here instead of in the navigation.
- **Only the essentials**, since space is limited, each with a recognisable icon or a clear label.
- **A back link or breadcrumb** on deeper screens, so people know how they got here and how to leave.

Branding in the top-left spot is wasted space if it doesn't tell people where they are.

## Going deeper should feel like expanding

When someone taps "See all" on a section, the next screen should use **the same arrangement** as the section they came from. It should feel like the same content expanding, not like a new place. Every deeper screen still gets a title, its own actions and a way back.

## Menus and overlays

- **Menus should open from the thing that triggered them.** In Liquid Glass the bubble pops open right where you tapped, which makes the relationship between the button and its contents obvious. On the web, I anchor dropdowns and popovers to their trigger and don't throw them into a corner.
- **Menus are vague and unpredictable as primary navigation.** People need context first; a menu is for secondary options.
- **Modal or slide-out panel?** If a form has four fields and the slide-out panel is mostly empty, a **centred modal** is probably better. Slide-outs suit content that benefits from staying next to the list it came from.
- **Always provide an exit**: a close button, Esc, and clicking outside for non-destructive overlays.

## A mega menu on marketing sites

On a marketing site's navbar, a **mega menu** quietly tells visitors the product has **depth worth exploring**. That's fine on a marketing site, where browsing is the point. Inside the app, I keep navigation plain.

---

# Part 3 — Laying out content

The content should be organised to guide people to what matters most and to what they expect to find first.

## Hierarchy: every screen is a sentence

Something has to be the **subject**. If everything is the same size and weight, people have to read all of it to find what they want.

Visual hierarchy guides the eye through the screen so people notice elements **in order of importance**. The tools are:

- **Size**
- **Weight**
- **Colour and contrast**
- **Position and order** (higher up means more important)
- **Spacing** (more space around something gives it more importance)

**In practice:** I pick the **one element per screen that matters** and turn the volume down on everything around it. When the hierarchy is strong, the most important thing on the screen is always the most obvious.

- **Basecamp** does this with almost nothing: bold project titles and muted secondary text. That is the entire system, and it reads like a simple document.
- **Airtable** took spreadsheets, the most boring thing on Earth, and made rows scannable with colour-coded statuses.

### The squint test

I blur my eyes (or the screenshot) and see where my attention lands. In Majo's first draft, the eye went straight to the first collection because it was heavy and colourful. People missed half the content and lost their sense of place. If the thing my eye lands on isn't the most important thing, the hierarchy is wrong.

### A consistent example

- **"Welcome back"** in bold (a greeting, not a heading).
- "Here's what's happening today" in softer secondary text.
- One label-style section title: **RECENT ACTIVITY**.
- "Three tasks completed this week" as body text.
- "Updated 2 minutes ago" as caption text, muted.

The awful version mixes fonts, uses capitals in some places and not others, and makes some text grey at random. That's what many apps look like.

## Progressive disclosure

Progressive disclosure means **easing people from the simple to the complex**. It hides complexity so basic tasks can be done through simple, approachable interfaces.

**The cheeseburger (Mike Stern).** A waiter asks one question at a time: how would you like it cooked, which cheese, any toppings, which side. Ordering would be overwhelming if you faced every option at once. Earlier answers also make later ones irrelevant: if you don't order fries, you don't need to hear about truffle fries.

**The print dialog.** Most of the time people care only about which printer, how many copies and which pages. That's well under 20% of the options and covers well over 80% of what people want. Everything else is **one click away**. This also stops people changing settings they don't understand and then phoning a relative in a panic.

**Majo's version.** Show a few items per section, with a **"See all" disclosure next to the section title**. The rest of the content isn't missing; it's waiting until it's relevant.

### The catch

Progressive disclosure can also **bury** things. Mike Stern loves garlic fries and would have ordered them if he'd known they existed.

**My rules:**

- The top 20% of functions (by frequency and importance) are **visible**.
- The other 80% are **one clear step away**, never three.
- Anything people *need to know about*, even if they rarely use it, gets a visible entry point.
- Beginners see the simple version. Experienced people can reveal what they need quickly (advanced settings, "More options", keyboard shortcuts).

## Visibility: don't hide what people need

Usability improves a lot when controls and information are **clearly visible**. A car's dashboard is cluttered with gauges, numbers and warning lights, and all of it is there because hiding it would be dangerous.

- In Mail, unread badges and status indicators are clutter in one sense. Removing them would look cleaner and **make the product much worse**: people would have to open each email to find out its status.
- **I surface key status at higher levels** whenever I can: list rows show status, and nav items show counts.

### Two views: delete things vs keep them visible

| Oliver (SaaS) | Apple (Mike Stern) |
|---|---|
| "When there's nothing left to remove, it's perfect." Collapse rows of buttons into a kebab menu. Delete anything that isn't the page's one job. | Visibility greatly improves usability. Hiding information (badges, navigation in a hamburger) looks cleaner and hurts usability. Dense interfaces can overwhelm, so it's a trade-off. |

**When each applies:**

- **Hide or collapse** things that are **rarely used, secondary, or duplicated elsewhere**: extra row actions, metadata that isn't what people scan for, decorative chips.
- **Keep visible** anything people **scan to make decisions** (status, priority, unread, due date, the key number), **primary navigation**, and **safety-critical state** (unsaved changes, a live recording, a destructive mode being on).
- **The test:** would removing it make people click into things just to find out? If so, it stays.

## Choosing the right container

The layout should be the clearest way to show *this* content. Decoration without a concrete purpose makes important features harder to find.

| Container | Use it when | Avoid when |
|---|---|---|
| **List** | Structured information people scan quickly, text-heavy items, items with long names, lots of items that need to fit | The content is primarily visual |
| **Table** | Comparing items across several attributes, sorting, filtering, bulk actions (Capern, Attio, Airtable) | There are only one or two attributes, or on narrow mobile screens without a fallback |
| **Grid / collection** | Visual items (photos, covers, products, templates) people browse and recognise by sight | Two items fill a whole screen, or text is long. Majo's grid wasted space on two items and handled long text badly, so it became a list. |
| **Cards** | Summarising distinct objects that each have a few pieces of information and an action | Every piece of information gets a card, or a card holds only one line |
| **Bento grid** | Marketing pages where different content deserves different amounts of space | Inside the app for routine data |

A list is flexible, familiar and highly usable. It takes less vertical space than images, so more fits on screen. **I start from proven component patterns** (Majo used Apple's list template) instead of designing from scratch. Designing for function pays off.

For collections: **consistent spacing between items** and **minimal text on each item**. That's what makes them feel dynamic and scannable.

## Grouping content (Majo's four themes)

As the number of choices grows, so does the effort to process them, and instead of browsing, people feel overwhelmed and leave. Before I work out how to *display* lots of content, I *organise* it:

1. **By time.** Recent files, "Continue where you left off", "This week". Also by **season and current events** (end of quarter, tax season, holidays), which makes the product feel alive and relevant.
2. **By progress.** Drafts, in progress, half-finished setup. People rarely finish everything in one go, so this makes the product fit how real life works.
3. **By pattern.** Related items and things that belong together ("Similar leads", "Customers in the same industry"). This turns a quick look into a longer exploration by showing connections people didn't know to look for.
4. **By meaning/type.** Separate different kinds of content (Majo split *Groups* and *Records*) and give each section a clear title.

These work for any product, even one whose content isn't visual or doesn't change often. They reduce choice overload and make the product feel a step ahead.

## Proximity: controls live next to what they affect

The closer a control is to an object, the more people assume they're connected. The bathroom light switch is in the bathroom.

- Put the action next to the thing it acts on. A row's actions go on the row; a section's actions go in its header; a field's help text goes under the field.
- **Closeness is also ergonomic**: people want to control whatever they're focused on, so put the control where their attention already is.
- Keynote puts object-creation tools right above the canvas, and the format/document toggles right above the panels they open.

## Grouping: related things together, unrelated things apart

If one switch in a row controls the blinds and the rest control lights, the blinds switch should be **set apart**. Grouping shows people how elements relate and gives the design structure.

- Group related controls with space, dividers or a shared container. Sketch clusters its grouping, transform, path and layer-order controls.
- **Separate** anything that behaves differently, especially **destructive actions**. Delete doesn't sit in the same button cluster as Save.
- Many apps get this wrong; it's easy to overlook. I check it deliberately.

## Mapping: controls resemble what they affect

Blinds go up and down, so an up/down control makes sense. Three light switches in a row should match the layout of the three lights on the ceiling.

- A horizontal property gets a **horizontal slider**. Rotation gets a **dial**, not a slider or stepper.
- The order of controls should mirror the order of the things they control, such as column settings in column order.
- **A label explaining a control is often a sign that the mapping is bad.** Reading takes time and doesn't help people remember. I fix the mapping first and add a label only if it's still needed.
- **The best mapping is direct manipulation.** Drag the thing itself, resize the thing itself, edit the text where it is. It's more intuitive and more precise.

## Symmetry, balance and rhythm

Symmetry reads as health, stability, balance and order. Symmetrical elements are perceived as belonging together even when they don't touch.

- **Reflectional symmetry** gives balance: key elements centred on a median line, everything else balanced against each other (Weather, Camera, Clock, Phone).
- **Translational symmetry** gives structure through repetition: evenly spaced rows, a consistent rhythm of cards, identical gaps. The Clock app's evenly repeated cities are an example.
- I look for chances to use symmetry for balance and order, and I treat uneven spacing between repeated items as a bug.

## Fix the cards first (Oliver)

The biggest visible improvement for the least work. AI is worst at **dense, repeated components**, and a list of cards is where it dumps every button, chip and timestamp.

- Collapse a row of buttons into a **triple-dot (kebab) menu**, keeping the one primary action visible if there is one.
- Turn text chips into **icons** where the icon is unambiguous.
- Move **the number that actually matters** to the right, where the eye lands when scanning.
- Move everything else out of the way.

Same information, about **a third of the noise**. What the card shows should match what the person is looking for.

### Worked example: density

**Too much:** "Sarah Chen, Product Designer, running Project X, In progress, High priority, Bug, Front-end", each as its own coloured chip, then Marcus with another five coloured chips. That's colour and clutter everywhere.

**Better:** Sarah's name and project, "In progress" as plain text, **high priority as the only coloured element** (a small red dot or a red label), and a kebab menu for everything else. We still know she's in progress and high priority.

**Rule:** don't use two different signalling systems at once. **Progress as words, priority as colour** is much clearer than colouring both.

## Design for ugly data, not demo data

The design looks great because I filled it with tidy examples: short names, round numbers, perfect photos. **I test with real data** to see how bad it actually looks.

I decide these rules up front:

- **Long strings.** Truncate with an ellipsis (Oliver's rule of thumb is about 15 characters in tight spots; otherwise truncate at the container width) and show the full value on hover or focus.
- **Long names, other languages, larger text sizes** (Majo: *"But will it hold up?"*). Layouts must handle text that doubles in length, text in German or Arabic, and people who have their browser zoomed to 200%.
- **Huge and tiny numbers**: 0, 1, 1,000,000, negatives, missing values.
- **Missing images and avatars**: fall back to initials on a **solid circle**. Put icons on solid circles too, so they work on any background.
- **Empty states**, designed deliberately (see below).
- **Loading states**: skeletons, not blank space.
- **Error states**: clear, human, and they tell people how to fix things.

New users see all of these before they see my perfect demo state.

### Empty states

An empty state is often someone's **first impression** of a feature. It should:

- Say what will appear here ("Your invoices will show up here").
- Offer **the one action** that fills it ("Create your first invoice").
- Never be a blank white rectangle, and never be a decorative illustration with no next step.

---

# Part 4 — Visual design

Visual design communicates the product's **personality and tone** and shapes how people feel, but it always **supports function**. It is the careful use of hierarchy, typography, imagery and colour working *together*. Each one deserves attention, but the real impact comes when they combine into a single meaning.

## Undo what the AI gave me first

AI tools (Cursor, Lovable, Bolt and the rest) build something functional in an afternoon and apply **the same defaults every time**. People who look at software all day spot those defaults immediately. These are the cheapest fixes I'll ever make, and most take under an hour.

**Signs of slop:**

- Emojis as decoration or as icons
- Glow shadows
- Clashing gradients (especially purple to blue)
- Random font sizes
- **Different border radii** on buttons: some pill-shaped, some square
- Things that aren't centred (a "Watch demo" label off-centre in its button)
- Feature boxes of different sizes with different radii
- A saturated blue or purple base plus a second bright accent fighting it
- The same four KPI cards on every page
- Alternating text-left/image-right sections all the way down the marketing page
- Stock photos
- Elements flying in from the sides as you scroll

Each of these is the tool **adding visual material where information should be**.

## Colour: restraint and meaning

### A restrained base and one accent

**AI will pick bright, clashing colours.** I pick a **restrained base and one accent**. Muted colours work.

Stripe's palette is boring, and Stripe is one of the most trusted interfaces in software. **People trust simplicity**: greyscale, whitespace, less detail, less colour. They don't trust glowing buttons, purple gradients and everything fighting for attention.

The "boring" version on the right of Oliver's comparison isn't actually boring. It's **muted and minimal**, and that tells people the product will speak for itself. I'm not here to excite people with the design; I'm here to guide them to the result they want.

**The Attio/Airtable-style look:** near-white backgrounds, thin borders, little or no shadow, **mostly greyscale**, colour only on things that mean something (a muted green ICP score with a thin green border), logos in full colour, all button radii the same.

### Let the data carry the colour

- A dashboard full of coloured buttons looks cheap.
- The same dashboard with **muted chrome**, and colour saved for **charts and statuses**, looks expensive.
- **Colour is only for things that are showing something**: status, priority, trend, category, selection, the primary action.

This matches Apple's Liquid Glass rule: **"If you want to bring colour into your app, do it in the content layer"**, not the navigation and controls.

### Colour follows importance: the email example

Composing an email to Maya White:

- **Send** is what you want them to do → **solid accent** (primary).
- **Save draft** is a middle option → **neutral/white** (secondary).
- **Discard** is what you *don't* want them to do casually → **low emphasis** (tertiary/ghost), kept apart.

Colour and emphasis lead people toward finishing the task.

### Use the accent sparingly (Liquid Glass tinting)

- **Tint only primary elements and actions.** A red "View bag" button in a food delivery app works because it's the only red thing.
- **If every element is tinted, nothing stands out**, and it becomes confusing.
- Accent colour belongs on **buttons, controls and selection states**, and only where it doesn't hurt legibility, comfort or dark-mode behaviour.

### Semantic colours: named by purpose, not appearance

Apple's system colours have names like `label`, `secondaryLabel` and `secondarySystemBackground`, not "black" or "purple". They're **semantic**: named after their *job*, so they can adapt to light and dark mode, increased contrast and different environments without extra work.

I do the same on the web with design tokens:

```
--color-bg               /* page background */
--color-bg-secondary     /* grouped/sidebar background */
--color-surface          /* cards, modals */
--color-border           /* dividers, inputs */
--color-text             /* primary label */
--color-text-secondary   /* supporting text */
--color-text-tertiary    /* placeholder, disabled, timestamps */
--color-accent           /* the ONE brand accent: primary buttons, links, selection */
--color-on-accent        /* text/icons on accent */
--color-success / --color-warning / --color-danger / --color-info
```

Components never use a raw hex value; they use a role. Dark mode becomes a matter of redefining roles, not hunting through components.

### Brand palette: personality, with rules

Semantic colours handle the system. **Personality** comes from a small brand palette used in specific, rule-bound places. Majo chose **four colours and a few retro shapes**, set **simple rules** for combining them, and used them for group artwork. That gave a consistent style and made it easier to stay consistent as the app grew.

- A small palette (3–5 colours) with **written rules** about where each may appear.
- Used in the **content layer**: illustrations, covers, category artwork, charts, marketing.
- Never used for text colour at random or for chrome.

**The balance:** know when to rely on the system (semantic, adaptive, accessible) and where to add personality (a curated palette in the content).

### Contrast and legibility

- Body text meets **WCAG AA (4.5:1)**; large text and UI components meet **3:1**.
- Placeholder text isn't the only label for a field.
- Never use colour alone to carry meaning. Pair it with text, an icon or a shape, for colour-blind people and for greyscale printing.

## Typography

### Use a type system instead of eyeballing sizes

Apple's **system text styles** (Large Title, Title, Headline, Body, Callout, Subheadline, Footnote, Caption) give a consistent range for showing levels of importance without eyeballing sizes or inventing styles. I set up the same kind of scale for the web (Part 14) and **use only those styles**.

- **Few typefaces.** One family, two at most (for example a UI sans plus a display face for marketing headlines).
- **Few sizes, few weights, few colours.** Internal consistency makes a product feel cohesive.
- **Consistent case.** If section labels are uppercase, *all* section labels are uppercase. No mixing.
- **Different levels need visible differences.** A headline one pixel bigger than body text is noise, not hierarchy. Use size *and* weight *and* colour steps.

### Let people choose their text size

Apple's text styles support **Dynamic Type**, so people pick a comfortable size and the layout adapts. On the web:

- Size text in `rem` and respect the browser's base font size.
- Layouts survive **200% zoom** with no horizontal scrolling and nothing overlapping.
- Containers grow with their text; I don't fix heights on anything containing text.

This makes the product more inclusive and easier for everyone.

### A display font for personality, used in limited places

Majo used a **bolder, expanded font** only for group titles, so they looked different from list text. A distinctive display face can carry personality in a *few* places (hero headlines, section artwork, empty-state headings) while the UI stays in the system face.

### Text over images

Legibility breaks quickly over busy or high-contrast images. **Clarity comes first.**

- Add a subtle **gradient scrim or blur** behind the text. It improves readability and adds some depth without disrupting the design.
- Or move the image into the background of a full-bleed area so the text has a **stable space** of its own.

## Icons

### Never use emojis as icons

Emojis as UI icons are the fastest way to look amateur. **Real icon sets** carry the same meaning, clash less, cause less friction and make the product look grown up.

Icons take up little of the screen, yet they're one of its **most revealing details**.

### Two views: which icon set?

| Apple | Oliver (SaaS) |
|---|---|
| Use **SF Symbols**: consistent, and already familiar to anyone on Apple platforms. | Install **Lucide** or **Phosphor** (or **Feather**): free, thousands of icons, consistent sizing and style. |

**When each applies:** for native Apple apps, SF Symbols, always. For web and SaaS, which is most of my work, **Lucide or Phosphor**. Both views agree on the underlying rule: **one consistent icon family** with one stroke weight, one sizing scale and one corner style. I don't draw my own (Majo finds it really hard too, and consistency matters more than originality).

### Familiar metaphors over creative ones

- **Trash means delete.** Using a trash icon for anything else breaks what people know from all other software. Getting creative with the delete icon costs instant recognition too.
- **The sharrow lesson.** On iOS, "share/action" is a box with an arrow pointing up. Some iOS apps used the three-connected-dots share icon to match their website. That's a reasonable instinct and **the wrong call**, because what matters is being consistent with **what people already know**, not with my brand.
- **For common actions, I don't reinvent the wheel.** I innovate on the problem, not on the magnifying glass.

### Icons and labels together

- Primary navigation: **icon + label**.
- Toolbars: icon-only is fine for *universally* known actions (search, close, more, settings); otherwise add a label or at least a tooltip.
- Use icons to **replace repeated text labels** in dense data: a building icon instead of "Company:", a calendar icon instead of "Date added:", a dollar sign for value. Oliver's Attio example does exactly this.

## Imagery

- **A consistent visual style.** Mixed photo styles, colour treatments and illustration styles look random (Majo's first attempt).
- **No stock photos.** Show the **real product**.
- **Crop to the point.** A full screenshot makes people hunt; a cropped one tells them what to notice.

## Shape: one radius system

- **All buttons share the same radius.** Not some pills and some squares.
- Radii come from a small scale (Part 14), assigned by component size.
- **Concentricity** (from Liquid Glass): nested rounded shapes share a centre. **Inner radius = outer radius − padding.** A button inside a card inside a modal should look nested, not stuck on. Apple's controls nest precisely into the rounded corners of windows and devices.

## Depth, layers and materials

### The two-layer model (Liquid Glass)

Apple splits every interface into:

1. **A content layer**: the actual stuff (lists, tables, media, documents).
2. **A navigation/control layer**: toolbars, tab bars, sidebars and floating controls that sit *above* content.

Liquid Glass belongs **only on the navigation layer**. This is the most useful idea I take from it, even on the web.

### Two views: flat vs depth

| Oliver / Attio style | Apple Liquid Glass |
|---|---|
| Near-white, thin borders, **no shadows**. Glow shadows and chunky drop shadows are signs of slop. | A translucent material that bends light, with **adaptive shadows** that deepen over busy content and fade over plain backgrounds, highlights, and depth that grows as elements get bigger. |

**When each applies:**

- **Data-dense SaaS screens** (tables, dashboards, CRMs, admin panels): **flat**. Borders and background shifts separate things; shadows are rare and soft.
- **Floating elements that truly sit above content** (dropdowns, popovers, modals, sticky headers over scrolling content, floating action bars): **a clear layer** using a soft shadow or translucency, because they *are* above the content, and depth is how you show that.
- **Media-rich or consumer products** (photos, music, video, maps): translucent materials over the content can work beautifully, following the rules below.

### Translucency rules, borrowed from Liquid Glass for the web

If I use translucent/blurred surfaces (`backdrop-filter`):

- **Only on the navigation/control layer**, never on content. A glass data table competes with everything else and muddies the hierarchy.
- **Never glass on glass.** Stacking translucent layers looks cluttered and confusing. Anything on top of a translucent surface uses **solid fills, transparency or vibrancy** so it reads as part of that surface.
- **Two variants, never mixed.** Apple's *Regular* (adapts, always legible, works anywhere) and *Clear* (more transparent, needs a dimming layer). I use Clear only when **all three** conditions hold: it's over media-rich content, the content won't be harmed by a dimming layer, and whatever sits on top is bold and bright.
- **Legibility adapts.** Small elements (nav bars) can switch light/dark based on what's behind them. **Large surfaces** (menus, sidebars) should *not* flip, because a big surface changing is distracting.
- **Bigger elements look thicker**: deeper shadow, more blur. A menu opened from a toolbar button should look more substantial than the button.
- **Tint only the primary action.** Use a translucent tint, not a solid opaque fill, which breaks the material.
- **No overlap when at rest.** On first load, content and floating controls shouldn't overlap. Reposition or rescale the content so there's clear separation.
- **Focus changes appearance.** An unfocused window or background panel **visually recedes** to direct attention.

### Separation on scroll (scroll edge effects)

When content scrolls under a sticky header, Apple **gently dissolves the content** under it (a gradient fade, or a subtle dimming on dark content) so titles stay legible. When there's a pinned accessory under the toolbar, such as column headers, it uses a **"hard" edge** instead: a uniform treatment across the toolbar and accessory.

On the web:

- A sticky header gains a **subtle border, shadow or fade only once content scrolls under it**.
- Tables with sticky column headers get a **hard, solid** header background so rows never show through.

### Accessibility modifiers for materials

Apple's glass automatically respects **Reduce Transparency** (frostier, more opaque), **Increase Contrast** (mostly black and white with contrasting borders) and **Reduce Motion** (calmer effects, no elasticity). On the web I respect the equivalents:

- `prefers-reduced-motion`
- `prefers-contrast: more`
- `prefers-reduced-transparency` (where browsers support it; otherwise always keep a solid fallback)
- `prefers-color-scheme`

---

# Part 5 — Interaction and behaviour

Interactive experiences **happen over time**, with a lot of back and forth. The biggest mistake is designing static screens and forgetting the conversation between them.

## Affordance: make it obvious what can be done

Affordance is the relationship between a person and an object that suggests what's possible. A plate's smooth surface and raised rim suggest *put food on it* and *pick it up*, not *drink from it*. Affordance varies from person to person; people most readily notice affordances for actions they're already likely to take.

In interfaces:

- **Buttons look pressable**: a shape, a fill or a border, and hover and pressed states.
- **Sliders look draggable**: a filled circle on a line is enough.
- **Links look like links.** Non-interactive text never looks like a link.
- **Interactive and static elements must never be confused.** If a card is clickable, the whole card responds (hover, cursor, focus ring). If it isn't, it doesn't pretend to be.
- **Motion can signal affordance.** Weather nudges its content up slightly when tapped to hint that it scrolls. A partially visible next card hints at horizontal scrolling.
- We're comfortable with a lot of abstraction now: rounded corners are enough to say "button", and a subtle shadow says "this can move independently". But **abstraction has a floor**: text with no hint of being interactive does not afford clicking.

If affordances are unclear, people interact in ways I don't support, and they mistake controls for decoration.

## Mental models: match what people already expect

Everyone carries a simplified model of every system they've used:

- **The system model** is how they think it works. (Two water sources, hot and cold, mixed together, with a delay before the temperature changes.)
- **The interaction model** is how they think they operate it. (Turn the handles.)

When a design **matches** someone's mental model, they call it **intuitive**. When it doesn't, they call it **unintuitive**, even if it's objectively cleverer.

### Don't be Mortimer

Mortimer the faucet designer had a brilliant idea: one handle for temperature, one for flow. It was better in theory, but it looked exactly like a normal faucet and behaved completely differently. People turned on "hot" and no water came out.

- **Labels and small tweaks to form are band-aids**, easily missed when people have deeply ingrained expectations.
- **Changing people's mental model is risky**, and it gets riskier the more familiar people are with the product.
- **For long-lived products:** changes will always be hard for people to adjust to, however good they are. Only make big changes when I'm **100% sure they're clear wins for existing users**. Never change for the sake of change. Test, and prove beyond doubt that the new way is better. *Then* push through, because people will come around.
- **If something truly behaves differently, it should look different.** Don't dress a new behaviour in an old costume.

## Consistency: similar things look and behave the same

Inconsistency undermines usability. Every car puts the brake on the left and the accelerator on the right, which is why you don't relearn driving with each new car.

### External consistency: follow conventions

People's expectations come mostly from **other products they use**. I can't know exactly which ones, but they've certainly used the web and their OS. So I follow web conventions:

- The logo top-left links home.
- Close (×) is at the top-right of dialogs, and Esc closes them.
- Primary and secondary button order is consistent across every dialog.
- Search looks like search, with a magnifying glass.
- ⌘/Ctrl+K opens a command palette if I have one; ⌘/Ctrl+S saves; Enter submits a single-field form.
- Links are underlined or clearly coloured; visited states make sense where relevant.
- The standard icons for standard actions.

**Be consistent with what *they* know, not what *I* prefer** (the sharrow lesson).

### Internal consistency: my product matches itself

- **Looks the same means behaves the same.** If one button moves to a new screen, another toggles something and a third opens a modal, there's no pattern to learn.
- **Consistent placement.** On a Mac, the window close button is always top-left. When an action is always in the same place on every screen, people stop thinking about it. Primary actions always sit in the same place in the header, and destructive actions always in the same place.
- **One icon style, a few type styles, a few colours, one radius system.**
- **One word per concept.** If a button says **Delete** on one screen and **Remove** on another, people have to stop and reread. You end up with *Remove*, *Delete* and *Trash* all meaning the same thing. Pick one and write it down (Part 14).
- **Same labels mean the same destinations.** Never mix "Get started", "Try free", "Start trial" and "Get the demo" for the same destination.

Humans pattern-match, and every inconsistency breaks the pattern and adds friction. Consistency is hard: it takes deliberate effort and restraint.

**When to break consistency:** try new ideas, because that's how innovation happens. But **inconsistency in simple things (icons, labels, placement) trips people up.** Stay consistent unless there's a very strong reason not to.

### Familiarity through metaphor

Metaphors have helped people learn software since the first GUIs: put things you don't want in the **trash**, and take them back out if you change your mind, just like the real world.

- **Too literal:** people may not recognise the real-world object you're referencing.
- **Too abstract:** the idea doesn't come across.
- **Just right:** it draws on something people know and **helps them predict what it will do**.
- A metaphor that behaves differently from its real-world counterpart surprises people in a bad way.

## Feedback: my side of the conversation

Cars give constant, layered feedback because mistakes are dangerous. Software should do the same. Feedback answers four unspoken questions:

1. **What can I do?**
2. **What just happened?**
3. **What is happening now?**
4. **What will happen next?**

### Four kinds of feedback

| Type | Car | Software |
|---|---|---|
| **Status** | Gear shown twice (gearstick and dashboard), fuel gauge, speedometer | Unread indicators, "Syncing…", plan and credit usage (Capern's credits bottom-left), who's online, "Unsaved changes". Camera shows recording **three ways**: red dot, running timer, record-button state. Critical status deserves redundancy. |
| **Completion** | Engine sound and vibration, the click of gears, doors locking automatically | "Saved" ticks, sent animations, a toast confirming the action, a row animating away. Apple Pay's sound and animation: impossible to miss. |
| **Warning** | Low fuel, brake-pad warning | "You have 3 credits left", "This will notify 240 people", an approaching limit, an expiring card. |
| **Error** | "Can't start: no fuel" | A form error, a failed upload, lost connection, each with what to do next. |

**Every action I offer produces some confirmation.** Automatic actions (the doors locking themselves) need feedback *even more*, because people didn't trigger them.

Good completion feedback is **discreet, not intrusive, and hard to miss**. It reassures people so their attention can go to the next thing.

### Prevent errors before reporting them

Errors are always disappointing. It's better to help people avoid them:

- **Inline validation**: show what's accepted *as they type*, not after submitting.
- **Constraints**: date pickers instead of free text where appropriate, disabled states with a reason.
- **Work out what they meant and do something sensible.** Type June 31 in Things 3 and it quietly becomes July 1, with no error. That's a very human thing to do. Trim whitespace, accept phone numbers in any format, fix obvious casing.
- **Warnings** before the point of no return.

### When errors happen

- Say **what happened** in plain language.
- Say **why**, if it helps.
- Say **how to fix it**, ideally with a button that does it.
- Put the error **next to the thing that caused it** (proximity).
- Never blame the person. Never show a raw error code alone.

### The "explain it out loud" test (my favourite technique)

1. Ask someone who has **never used the product** to use it while thinking aloud: what's unclear, what's confusing.
2. Then **explain to them how it actually works.** Guide them and tell them what to pay attention to.
3. Step back and compare **what I said** with **what the product says**.

When people explain their design in person, it's almost always clearer than the design itself. Whatever I said to fill the gaps is exactly what the interface is missing. **Good feedback is like having the designer sitting in the room with you.** So I ask: *if I were next to them, what would I say, and how would I say it?*

**Don't overdo it:** too much feedback is annoying. It should be proportional to the importance of the action.

## Speed is also an aesthetic

Oliver's figure: **a one-second delay costs about 7% of conversions.** The fix isn't always faster code; it's **showing something immediately**.

LinkedIn shows grey **skeleton bars** for a split second when you search. It didn't load faster; it *felt* faster. A blank screen looks broken.

> **People don't need speed. They need evidence that something is happening.** They'll happily wait two seconds when they can see progress. They won't wait two seconds staring at a blank screen.

My defaults:

| Wait | What I show |
|---|---|
| Instant (< ~100 ms) | Nothing extra; just respond. Every tap or click gets immediate visual acknowledgment (pressed state). |
| Short (~0.3–1 s) | **Skeletons** matching the final layout, for content being fetched. A spinner *inside* the button for actions. |
| Over ~1 s | A **progress indicator**, determinate if possible ("Uploading 3 of 12"). |
| Long jobs (many seconds or minutes) | Progress plus **what's happening** ("Enriching 240 leads…"), permission to leave ("We'll email you when it's done"), and something **playful** if it fits the brand (PostHog's hedgehog wandering the screen). |

**Optimistic UI**: for actions that almost always succeed (liking, reordering, toggling), I show the result immediately and reconcile in the background, undoing clearly if it fails.

**Oliver's native-spinner trick:** on iOS, some apps use Apple's system spinner instead of a custom one, so people blame the phone rather than the app. The web version: **native-feeling, restrained loaders** read as "the system is working"; a showy custom spinner draws attention to the wait.

Craft means **no wait after a tap, no jittery scrolling, no layout that breaks on resize**. Software that feels fragile makes people doubt the results they'll get from it.

## Agency: people are in control

People feel in control when **I let them do things their way.**

- **Offer choices.** Don't force everyone down one predetermined path.
- **An interface should never stand between a person and what they're trying to do.**
- **Let people jump straight in** and explore at their own pace.
- People are much more engaged when they control their own experience.
- **Give control over pacing**: "Load more" rather than infinite scroll (see Motion); pause and resume on long jobs; cancel on anything running.

## Forgiveness: people will make mistakes

Giving people freedom means they'll send, change and delete things by accident. **Forgiveness** means they can always recover, which makes them feel capable, secure and **free to explore**.

### My tiers for risky actions

| Action type | Treatment |
|---|---|
| **Reversible, low stakes** (archive, move, mark read, remove from a list) | Just do it, confirm with a toast, and offer **Undo** (about 5 seconds). No dialog. |
| **Destructive but recoverable** (delete to a bin, cancel a draft) | Do it, confirm with a toast, offer **Undo**, and keep a **bin/trash** people can restore from. |
| **Destructive and final, or expensive, or wide-reaching** (permanent delete, sending to 10,000 people, charging a card, changing a plan) | A **confirmation dialog** that says exactly what will happen and what's affected. |
| **Catastrophic, "danger zone"** (deleting a database, workspace, account or server) | Confirmation plus **typing the name** to confirm (Supabase makes this tedious on purpose). |

### Two views: confirmation vs undo

| Oliver | Apple |
|---|---|
| "Some buttons should be hard to press." Add "Are you sure?" to anything destructive, expensive or final. Confirmation gives certainty, not just friction. | Make it easy to **undo any action**. Double-check only when something is destructive. **Use interruptions carefully**, only when someone is about to make a *big* mistake. |

**When each applies:** Apple's default is **undo first**, because interruptions tax everyone to protect a few. Oliver's confirmations belong where **undo is impossible or the damage spreads beyond the person** (other people notified, money moved, data permanently gone). The tier table above is how I reconcile them. **A confirmation dialog on every delete trains people to click "Yes" without reading**, which defeats the purpose.

### A good confirmation dialog

- **Title that states the action and the object:** "Delete the Q3 launch plan?"
- **Consequence in plain words:** "This removes the project and all 42 of its tasks."
- **Finality stated clearly:** "This can't be undone."
- **The button repeats the verb:** "Delete project", never "OK" or "Yes".
- **The safe option is easy** (Cancel, Esc) and the destructive button is styled as destructive.
- For danger-zone actions, **type the name to confirm**.

### Close the loop: the Zeigarnik effect

Unfinished actions nag at people. If something vanishes instantly with no confirmation, people don't trust that it worked. They refresh to check, or they worry.

**Every meaningful action ends with a clear completion state:** a tick, a "Project deleted" toast with **Undo**, a thumbs-up after the spinner. Certainty is part of the design.

## Motion: it has to earn its place

### Two views

| Oliver | Apple |
|---|---|
| No animation in the app except celebrating completion (confetti). Scroll-jacking, elements flying in, parallax and fade-ins are cheesy. The only fade-ins are **skeleton loaders**. | Motion and visuals are **designed as one**. **Responsive, fluid animation gives immediate, natural feedback.** Menus pop open from where you tapped; controls morph between states; elements respond to touch. It makes the interface feel alive and helps people understand where things came from. |

**Where they agree, and my rule:** **Does this motion tell the person something? If not, it goes.**

Motion that *earns* its place:

- **Feedback**: a button pressing, a toggle sliding, a row animating out when deleted, a checkmark drawing in.
- **Continuity**: a panel expanding *from* the card that opened it; a menu growing *from* its trigger; a list item moving to its new position when re-sorted. This answers "where did that come from and where did it go?"
- **Affordance**: a hint that something scrolls, drags or expands.
- **State change**: loading → loaded (skeleton → content), collapsed → expanded.
- **Completion and celebration** (see Delight).

Motion that **doesn't** earn it:

- Scroll-jacking
- Elements flying in from the edges as you scroll
- Parallax for decoration
- Things fading in on page load just because they can
- Animations that make people wait before they can act
- Bouncy, attention-seeking loops

**Craft details:**

- Short and quick (150–250 ms for most UI), **ease-out** for things entering and **ease-in** for things leaving.
- Motion **tracks input exactly**: a dragged sheet follows the finger; a swipe animation lines up with the swipe gesture.
- Motion **can be interrupted**: people never wait for an animation to finish before acting.
- **Respect `prefers-reduced-motion`**: replace movement with simple crossfades or instant changes.

### Pagination: "Load more" over infinite scroll

For most product lists, **"Load more"** beats infinite scroll:

- It gives people **control**.
- They can actually **reach the footer**.
- It doesn't slowly drag down their machine.
- They keep their place and sense of progress.

Infinite scroll is justified only for truly endless, casual feeds where there's no "end" to reach.

## Direct manipulation

The best mapping is the most direct one: **act on the object itself.**

- Drag to reorder, drag to resize, edit text where it sits (click-to-edit fields).
- Drag and drop for files.
- Keyboard equivalents for all of it (accessibility and power users).

---

# Part 6 — Words: UX writing

Words are interface. Most "confusing UI" is actually confusing copy.

## Plain, concise and clear

- **Plain language.** No jargon, no internal names, no engineering terms. Speak naturally.
- **No redundancy.** Say it once. Don't repeat the page title in the first sentence.
- **Get to the point.** Front-load the important word ("Delete project", not "Click here if you'd like to delete this project").
- **Respect people's time.** Fewer words, fewer steps.

## Labels say what things *are*

- Name sections by what they contain, not by clever branding. Majo renamed "Swaps" and "Saves" to clearer labels; the page title replaced a branded wordmark.
- People shouldn't have to click to find out what something is.

## Buttons say what will happen

- **Verb + object** where it helps: "Create invoice", "Send email", "Delete project".
- **Never "OK" or "Yes"** on a decision dialog; repeat the action instead.
- The same action always uses **the same verb** (Part 14 dictionary).

## Simple can mean adding words

Simplifying sometimes means **adding context**. A bare play/pause button is simple, but when someone comes back to a paused video they need **where they are and how much time is left**. Adding that information makes it simpler to use.

- "3 credits left" beats a bare number.
- "Updated 2 minutes ago" beats nothing.
- "This will notify 240 people" beats a plain "Send".

## Summarise, and prefer graphics where they fit

- Is there complex data that would be easier to understand as a **chart**?
- Can I **summarise** so people focus on what they care about ("3 invoices overdue, $4,200 total")?
- Every element should help make the point.

## Copy that sells outcomes (marketing)

The jump from good to great is copy that moves from **what it does** to **how it helps**:

- "Collect and analyse your data quickly" → descriptive, fine.
- "Turn your data into decisions" → the same feature, **promising an outcome**.

That rewrite is the **biggest single improvement** on a landing page.

## Tone

Choose the **emotion** I want people to feel (relaxed, confident, excited) and write to reinforce it. Error copy stays calm and helpful. Success copy is warm, not over the top. Nothing makes people feel stupid.

---

# Part 7 — People: onboarding, flexibility and inclusion

## Knowing what I don't know

It's a big world, and people have their own needs, habits and ways of getting through life. **My opinions and habits are neither always right nor the only ones.** I design with **modesty**. For every idea, I ask things like:

- Will this work for someone **in a wheelchair**, or using a **screen reader**, or **only a keyboard**?
- Will it work for someone who has **never used this product**?
- Will it work for someone **coming from a competitor** or another platform?
- Will it work for someone **on a slow connection**, an **old phone** or a **small screen**?
- Will it work for someone who **doesn't speak my language**, or reads **right to left**?
- Will it work for someone **stressed, rushed or distracted**?

Asking prompts the real question: *did I care enough to consider that?*

## Onboarding

The moment after someone starts a trial is when they're **least patient and most critical**. You used to have days; now you have **minutes, sometimes seconds**.

### Two views

| Oliver (SaaS) | Apple (WWDC18 and WWDC26) |
|---|---|
| **Progressive onboarding**: one obvious action that gets the job done, then reveal the next. Make the first step **impossible to miss**: a card with a shadow, greener than everything around it, saying **"Start here"**. Add a **progress bar** so people see the finish line. Celebrate when it's done (confetti, "well done" emails). | **Active discovery beats being told.** People remember what they discover themselves. Tooltips and pointing arrows mostly make *designers* feel comfortable, and people forget what they were told. Give people **agency**: let them dive in rather than guiding them down a fixed path. Apps people use infrequently must be **understandable immediately**, as if people already knew them. |

**Both agree:** **never force a tutorial.** Forced tours feel like a lecture; people click through without reading to reach the product.

**When each applies:**

- **If the product can deliver value on the first screen** (most consumer tools, simple utilities), take Apple's approach. Drop people straight into the real thing, make the primary action obvious through **hierarchy** rather than overlays, and teach in context (empty states, inline hints the first time a feature appears).
- **If the product needs setup before it's useful** (connecting accounts, importing data, inviting a team, as with most B2B SaaS), take Oliver's approach: a **short, dismissible "Get started" checklist** with one clearly highlighted next step, a visible finish line, and a small celebration at the end. The checklist is **optional and skippable**, never a gate.
- In both cases, reveal complexity **as intent grows**: the second feature is introduced once someone has used the first.

### Instantly understandable

Many products are used **only now and then**: a recipe app while cooking, booking pet care before a holiday, an expense tool once a month. They must be understandable immediately, as if people already knew how to use them. **Familiar navigation and patterns** do most of that work.

## Hold their hand, but don't trap them

Oliver: *hold their hand far more than feels necessary; guide them down the right routes.*
Apple: *give them agency.*

**Both, together:** make the right path **obvious** through hierarchy, defaults and clear next steps, while keeping every other path **available**. Guidance through design is good; guidance through restriction is not.

## Flexibility: the product adapts to real life

People use products in ways as unique as they are. Listening to music looks completely different at home on speakers, on a run with earbuds and a watch, or driving hands-free.

### Context and device

- **Phone**: quick, touch-first, one-handed, glanceable, interrupted. Big targets, the primary action within thumb reach, short flows.
- **Desktop**: deep workflows, precise pointer control, keyboard shortcuts, multiple panels, dense tables, bulk actions.
- **Every device deserves a solution that uses what's special about it**, not the desktop layout squashed down. Responsive design isn't just reflow; it's **rethinking the task** for the context.

### Abilities and audience

I get curious about who my audience is:

- How old are they?
- What languages do they speak?
- Are they **pros or beginners**?
- Do they rely on accessibility features?

I won't solve for everyone on day one, but I always look at how the experience can be more inclusive.

### Accessibility baseline for the web

- **Contrast**: AA minimum (4.5:1 text, 3:1 UI and large text).
- **Keyboard**: everything reachable and operable; logical tab order; **visible focus rings** (never `outline: none` without a replacement).
- **Screen readers**: semantic HTML first; labels on every input; `alt` text on meaningful images; accessible names on icon-only buttons.
- **Text resize**: works at 200% zoom.
- **Motion**: respects `prefers-reduced-motion`.
- **Targets**: at least 44×44px on touch.
- **Colour is never the only signal.**
- **Errors are announced**, not only coloured red.
- **Forms**: visible labels (not placeholder-only), clear required markers, errors tied to their fields.

### Personalisation

Often there's **no single layout that suits everyone**. Then the best option is to let people **adapt it**:

- Rearrange controls, columns or dashboard widgets.
- Hide controls they never use.
- Save views, filters and default sorts.
- Choose density (comfortable/compact) and theme (light/dark/system).

Flexibility takes work, but it's worth it, because **it shows people I designed with them in mind.**

## Beginners and experts

- Beginners get the simple default path, sensible defaults, and progressive disclosure.
- Experts get **accelerators**: keyboard shortcuts, a command palette, bulk actions, saved views, and advanced settings one click away.
- Neither group's needs should crowd out the other's.

---

# Part 8 — Responsibility and trust

Responsibility means **acting in people's best interest**.

## Privacy is a human right

Imagine a stranger walks up: *"Give me your phone number." "For what?" "I just need it." "…Why?" "I'll tell you once you give it to me."* Nobody would trust that person, yet interfaces do exactly this all the time: permission prompts the moment the app launches, before anyone knows what it does, and data requests with no explanation.

**Responsible interfaces:**

- **Wait for the right moment** to ask for personal data or permissions, in context, when the benefit is obvious. Ask for notification permission after someone sets up something worth being notified about, not on page load.
- **Ask only for what's necessary.** Every extra field in a signup form costs trust and conversions.
- **Explain what the data is for** before asking, in plain words.
- **Make privacy settings findable and understandable.**
- **Don't collect what I don't need.**

## Safety: think about misuse and harm

I'm responsible for everyone using my product *and* **anyone who could be affected by it**. For every feature:

- How could it be misused?
- Who would be harmed?
- How do I prevent that?

## Responsible AI features

When I build intelligent features, I **expect the model to produce something unexpected or wrong** sometimes.

Apple's example: a recipe app where someone has logged an allergy. The model might still suggest an ingredient that causes a severe reaction. That's real-world harm, and it can't be left to chance.

- Think realistically about what could go wrong, then **add safeguards**:
  - **Previews** before AI output is applied or sent.
  - **Confirmations** before AI takes actions on someone's behalf.
  - **Clear labelling** of AI-generated content, with **disclaimers** where accuracy matters.
  - **Hard constraints** that the model can't override (the allergy check runs in code, not in the prompt).
  - **Easy editing and undo** of anything AI produced.
- **Remove the feature entirely** if the risk to people's safety outweighs its value.

## No dark patterns (my own addition, in the spirit of all the sources)

Ethical friction is good; manipulative friction isn't. I never:

- Hide the cancel button, or make cancelling far harder than signing up.
- Pre-tick consent boxes or add-ons.
- Use guilt-trip copy ("No thanks, I don't like saving money").
- Fake urgency or scarcity.
- Disguise ads or upsells as content or navigation.
- Style the option I want people to choose so that it tricks them.

Friction exists to **protect people**, never to trap them.

## Trust comes from keeping promises

- Simplicity builds trust (Stripe).
- Consistency builds trust (people sense integrity).
- Feedback builds trust (they know what happened).
- Forgiveness builds trust (they know they can recover).
- Respecting privacy builds trust.
- **Every detail keeps or breaks the promise.**

Taking responsibility seriously leads to **a product people can trust**, and that's the best business case there is.

---

# Part 9 — Delight and value

## Two views on delight

| Oliver | Apple (WWDC26) |
|---|---|
| Celebrate people **doing the job**: confetti when someone connects their first account, "Well done, now connect the next one" emails, a tick or thumbs-up after a spinner, confetti at milestones. Simple and effective. | **"The way to make a design delightful isn't by adding confetti or tacking on extra flourishes at the end."** Delight comes from **identifying the emotion** you want people to feel (relaxed, confident, excited) and reinforcing it throughout. Delight is **the sum of all the care**, the natural result of getting every other principle right. |

**My stance (leaning Apple):**

- **Delight is earned first through everything else**: agency, safety, familiarity, flexibility, craft. A confetti burst can't rescue a confusing product.
- **Celebration is allowed when it's a real milestone** for the *person* (first successful send, first payment received, setup complete, a big goal reached), **not** for routine actions. Confetti on every save is noise.
- **It fits the emotion.** A finance tool celebrates calmly (a satisfying tick, a warm message); a creative or social tool can be more playful.
- **Small, human touches**: the June-31 date fix, a funny loading hedgehog on long jobs, a thoughtful empty state, a well-chosen sound. Delight lives in the details.
- It's always optional in effect: brief, skippable, and respectful of reduced motion.

> Delight is what's left over when I give people the agency to act, the safety to explore, the comfort of familiar patterns, and the ability to make it their own.

## Show people the value they're getting (Oliver)

The most underused retention feature in B2B is **showing people what they've achieved**.

- B2B buyers must **justify the subscription** to a boss or to themselves.
- If the product doesn't show its impact, **they'll assume they aren't getting much**. People never guess high.
- Make it a **scoreboard**, not just a tool:

> **Your impact this month**
> You've saved 30 hours · automated 100 tasks · found 26 leads · generated $18K in pipeline.

- Put it **on the dashboard**. Recap it in a monthly email. Mark milestones.

This matches Apple's aspiration of **positive impact on people's lives**: I make that impact *visible*.

## Stunning, in the right places

- **Polish**: things line up exactly as intended; gestures and animations match; nothing is off by a pixel.
- For experiences meant to be immersive (games, media, creative tools), aim for **work-of-art beauty**, and teach the rules *within the product's world*, not in bolted-on tooltips.

---

# Part 10 — Craft

Craft is **attention to detail that tells people I care** about the experience I'm giving them.

## What cheap feels like

A rickety door that won't close. A shirt that falls apart in the wash. In software:

- Tap a button and nothing happens for a moment.
- Scrolling stutters.
- Icons are misaligned.
- Resize the window or rotate the phone and the layout falls apart.
- Text overflows its container.
- Spacing is *almost* consistent.

When software feels thrown together, people **doubt the results** they'll get from it. Meticulous craft does the opposite: it **inspires confidence**.

## Quality materials

As with physical products, craft starts with good materials:

- **Typefaces** that look great across devices and sizes.
- **Colours** that adapt properly to light and dark and to contrast settings.
- **Clear graphics and iconography** from one consistent family.
- **Responsive animation** that is fluid and gives immediate, natural feedback.
- **A solid technical base**: reliable, secure, accessible, fast.

## Iteration

- **I won't get it right the first time.** Majo didn't, and nobody does. Each round of iteration brings the design closer to something supportive, predictable and easy to move through.
- The best small decisions (the ones that look obvious) often take **a very long time** to arrive at. **You can't hire more people to get there faster.** Sometimes you have to sit with it. Patience is part of the process.
- Hard work is part of the reward. Easy solutions sometimes mean I've missed something. The climb makes the view worth it.

## Maintenance: design has a lifespan

- Great design has **longevity**, so I keep evolving it.
- When new capabilities appear (new browser APIs, new devices, new input methods, new accessibility settings), I **ask whether they make sense** for the product.
- When the product evolves with those changes, people feel **supported and rewarded**.
- Craft is an **uncompromising commitment to detail**, now *and* over time.

## Pre-ship craft checklist

- [ ] Spacing uses only values from the scale; repeated items have identical gaps.
- [ ] Every button has the same radius (per size) and the label is optically centred.
- [ ] Nested corners are concentric.
- [ ] Icons are from one family, one stroke weight, aligned to text baselines or centres.
- [ ] Hover, focus, active, disabled and loading states exist for every interactive element.
- [ ] Layout works from 320px to ultra-wide, at 200% zoom, with long text and in another language.
- [ ] Dark mode checked screen by screen, not assumed.
- [ ] No layout shift when content loads (skeletons match final dimensions).
- [ ] No action waits without feedback.
- [ ] Scrolling is smooth; animations don't drop frames.
- [ ] Empty, loading, error, partial and "too much data" states are designed.
- [ ] Copy uses the verb dictionary; labels are consistent everywhere.

---

# Part 11 — Landing pages

The landing page is where a vibe-coded product **loses most of its customers**. It must give:

- **A clear reason for being here.**
- **A clear thing being sold.**
- **A clear reason to buy.**

There's a quality bar on SaaS landing pages that people **trust without noticing**. Getting from generic to professional is **a known path with a few moves**. Landing pages are about **presentation, not complexity**.

## Get out of template territory

- **Drop the alternating layout** (text left, image right, over and over). It's the signature of vibe-coded slop.
- **Stack the hero** and give it room.
- **Delete every stock photo.** Replace each with a **screenshot of the actual product**.
- **Every call to action says the same thing.** Never mix "Get started", "Try a demo", "Get the demo" and "Start free trial". **The same label means the same destination.** At most one primary CTA ("Start for free") and one secondary ("Book a demo").

## A structure that works (Oliver's Paper Schedule example)

1. **Hero**: an outcome headline, a softer subtitle, primary and secondary CTAs.
2. **The three big features**: what will be achieved, with restrained motion to signal "this is the main section".
3. **Each feature shown in motion**: the product actually working (leads filling in, enrichment running, sequences being written).
4. **Social proof**: reviews and a row of customer logos.
5. **How it works in 1–2–3 steps.** Three steps, not twenty.
6. **One final "here's what it does".**
7. **Pricing**: simple.
8. **FAQs.**
9. **A final CTA or demo.**

People who want this will recognise it. From there it's just: *what do I do and how do I sign up?*

## Where it starts to look expensive

**Curate the visual, then add depth:**

- **Stop showing the whole dashboard.** **Zoom in on the one part** that proves the point of each section. A full screenshot makes people hunt; a cropped one tells them what to notice.
- **Replace a row of four identical cards with a bento grid**, so different content gets different amounts of space.
- **Product-design touches:** a small badge, a row of customer logos, a **mega menu** that suggests depth.
- **Precise motion:** a blur as one panel changes to the next; a menu that stays open and slides sideways instead of closing and reopening.
- **Outcome copy** everywhere (Part 6).

None of this needs custom illustration, 3D or a freelancer. It's all **the same components I already have**. I already designed the product and I already know what it does.

## Apple principles on the landing page

- **Wayfinding**: people always know where they are on the page (sticky nav, clear section headings).
- **Hierarchy**: one subject per section.
- **Consistency**: CTAs, button styles and terms match the product itself, so the marketing site and the app feel like one thing.
- **Responsibility**: honest claims; no dark patterns on pricing.
- **Quality is earned**: every surface, from the landing page to the App Store listing to support replies, communicates it.

---

# Part 12 — How I work

## Prove it: "Why is this good? How do you know?"

Doug's first design lesson: his head of design asked *"Why is this good?"* and then *"How do you know?"* He didn't know, so he drew the idea (possibly in Microsoft Paint), took it onto the museum floor, and asked real visitors what they thought they should do.

- **I can't assume my designs work.** Not from my own experience, and not from talking about them.
- **Prototype, and put it in front of real people** in real contexts. See what they learn and what they miss. If more is needed, do more.
- The real question behind "why is this good?" is: **is this worth the energy to build?** Evidence answers it.

## Watch real behaviour

- Use **session recordings and product analytics** (Hotjar, PostHog) to see where people actually get stuck. I've spent months inside the product; they haven't.
- Run the **explain-it-out-loud test** (Part 5) on every major flow.

## Draw caricatures to communicate

Type designers invented a way to discuss shapes that words can't describe: **redraw what you see, exaggerated**. Push the flaw to the extreme ("this curve feels this cramped to me") so others can see the subtler version that's actually there.

- Use exaggerated sketches when words fail.
- Ask others to do the same, to see through *their* eyes.
- Good collaboration means finding **the shared view**: seeing the world through their eyes and letting them see it through mine.

## Be open to feedback

- **Accept, sort and prioritise feedback** as it comes, from myself and others. I learn far faster than if I get defensive and dig in.
- After using my own work for a while, **I develop blind spots**. Fresh eyes from people I trust catch what I no longer can.
- Defensiveness is instinctive, especially after late nights. I notice it and put it aside.

## Set expectations with collaborators

At the start of a project or with a new team:

- *This is how I work. This is how I communicate. How do you?*
- *Here are the goals I think we're working toward. Here's what matters to me. What matters to you?*
- *We'll get this out of the way and speak directly.*

It feels awkward, and it prevents a lot of drama and confusion. Everyone works toward **the same goal**.

## Collect references

- Screenshot products and sites I admire. Browse **Dribbble** and **Mobbin**. **Keep a folder.**
- Study *why* a reference works, using the principles in this document, not just *what* it looks like.
- When building with AI (Cursor, Lovable, Bolt, Claude), **upload the references** with *"match this design"*, **plus this rules sheet**.

## Working with AI tools

- AI forgets what it already built and falls back to its defaults. **Paste my rules sheet every time**: *these are the rules.*
- After every generated screen, run the **slop list** (Part 4) and the **audit** (Part 15).
- Ask the AI the same question I ask myself of every element: **does this help the person finish the job they came here for?** If it's decoration, cut it.

## Apple's Human Interface Guidelines are a reference, even on the web

When I'm unsure how to use a component (whether an action belongs in the nav, when to use a modal, how a list should behave), I check the **Human Interface Guidelines**. Majo does exactly this. Most of their reasoning transfers directly to the web.

## Balance the principles

- The principles pull against each other: visibility vs simplicity, feedback vs noise, agency vs guidance, consistency vs innovation.
- **Too much of any good thing is bad.**
- How much each matters depends on **platform, screen size, use case and the experience level of the people I'm designing for**.
- I use knowledge and intuition to find the best path, and I test to confirm it.

## Design is never finished

There's no single right answer. Each decision builds on earlier ones, from the first tap to the last scroll. Stay curious and keep improving it.

---

# Part 13 — The disagreements, settled

| Topic | Oliver (SaaS) says | Apple says | When each applies / my rule |
|---|---|---|---|
| **Removing vs showing** | Delete anything that isn't the page's job; collapse into kebab menus. | Visibility improves usability; don't hide navigation or status. | Hide what's **rare or secondary**; show what people **scan to decide**, plus nav and critical status. Test: would hiding it force people to click in to find out? |
| **Minimal** | Muted and minimal builds trust. | Simple ≠ minimal; sometimes simple means **adding** context. | Minimal *styling*, complete *information*. Aim for "exactly enough". |
| **Icons** | Lucide / Phosphor / Feather. | SF Symbols; follow platform conventions (the sharrow). | Web → Lucide or Phosphor. Apple native → SF Symbols. Always one family, familiar metaphors, consistency with what *people* know. |
| **Depth and shadows** | No shadows; thin borders. | Liquid Glass: layered, adaptive shadows, translucency. | Data-dense screens → flat. Truly floating layers → visible depth. Translucency only on the nav layer, never glass on glass. |
| **Colour** | Restrained base + one accent; colour only for data and status. | Semantic system colours; accent on controls and selection; brand colour in the content layer; tint only primary actions. | They agree. Semantic tokens for chrome, one accent for primary actions, colour for meaning, brand palette in content. |
| **Animation** | None except completion celebrations; skeleton fade-ins only. | Fluid, responsive motion designed together with the visuals; continuity and feedback. | Motion must **tell people something**: feedback, continuity, affordance, state. Never decoration. Respect reduced motion. |
| **Delight** | Confetti and "well done" moments. | Not confetti; delight is the sum of care and the chosen emotion. | Earn it through everything else first. Celebrate **real milestones** only, in a tone that fits the emotion. |
| **Onboarding** | "Start here" card, progress bar, celebrate each step. | Active discovery; agency; no tooltips; instantly understandable. | Value on the first screen → drop people in and teach in context. Setup required → short optional checklist. **Never force a tutorial.** |
| **Guiding people** | Hold their hand more than feels necessary. | Agency: let them explore their own way. | Make the right path obvious through hierarchy; keep every other path open. |
| **Destructive actions** | "Are you sure?" on anything destructive, expensive or final; type-to-confirm. | Make everything undoable; interrupt only before *big* mistakes. | **Undo first.** Confirm only when irreversible, expensive or affecting others. Type-to-confirm only in the danger zone. |
| **Consistency across platforms** | (implied) CTAs and verbs consistent everywhere. | Be consistent with the **platform people are on**, even over brand consistency. | Consistent **words and behaviour** everywhere; follow each **platform's conventions** for controls and icons. |
| **Loading** | Skeletons; native spinner so people blame the system. | Responsive, immediate feedback; no waiting after a tap. | Immediate pressed state, skeletons for content, progress over one second, restrained loaders. |
| **Where colour lives** | Charts and statuses. | The content layer, not the controls. | Same idea: chrome stays neutral, content carries colour. |

---

# Part 14 — My rules sheet (paste this into AI tools)

> **These are the rules. Follow them on every screen. Don't invent new sizes, colours, radii or verbs.**
> *(Values are my defaults. Change them per project, but always have one and only one set.)*

## Principles in one breath

- Every page answers **one question**. Delete anything that isn't that.
- Every screen answers: **where am I, what can I do, where can I go, how do I get out.**
- **One subject per screen.** Turn everything else down.
- **Inform, don't decorate.** No emojis, no glow, no gradients-for-the-sake-of-it, no stock photos, no repeated KPI cards.
- **Colour means something** or it isn't used.
- **Every action gets feedback.** Every wait gets evidence. Every mistake can be undone.
- **Same thing, same word, same look, same place.**

## Spacing (4px base)

`4 · 8 · 12 · 16 · 24 · 32 · 48 · 64 · 96`

- Inside components: 4–12.
- Between related elements: 8–16.
- Between groups: 24–32.
- Between page sections: 48–96.
- Related things closer together than unrelated things, **always**.

## Type scale (UI)

| Style | Size / line height | Weight | Use |
|---|---|---|---|
| Display | 40–48 / 1.1 | 600 | Marketing hero only |
| Title 1 | 30 / 1.2 | 600 | Page title |
| Title 2 | 24 / 1.25 | 600 | Section title |
| Title 3 | 20 / 1.3 | 600 | Card or panel title |
| Headline | 16 / 1.4 | 600 | Emphasised body, row titles |
| Body | 16 / 1.5 (14 in dense UI) | 400 | Default text |
| Callout / Secondary | 14 / 1.45 | 400 | Supporting text, descriptions |
| Label | 12 / 1.3, uppercase, +0.04em tracking | 500 | Section labels (consistently uppercase) |
| Caption | 12 / 1.35 | 400 | Timestamps, meta, helper text |

- Sizes in `rem`. One UI family (plus an optional display face for marketing). Weights 400/500/600 only.
- Text colour roles only: `text`, `text-secondary`, `text-tertiary`, `accent`, `danger`.

## Radius

`4` (chips, badges, small inputs) · `8` (buttons, inputs) · `12` (cards, popovers) · `16` (modals, large panels) · `full` (avatars, pills: **only** avatars and status pills, never mixed with square buttons)

- **Inner radius = outer radius − padding.**
- All buttons of the same size use the same radius.

## Controls

| Size | Height | Horizontal padding | Use |
|---|---|---|---|
| Small | 32px | 12px | Dense tables, toolbars |
| Default | 40px | 16px | Most UI |
| Large | 48px | 20px | Marketing CTAs, mobile primary actions |

- Touch targets are at least **44×44px**.
- Button hierarchy: **Primary** (solid accent, **one per view**), **Secondary** (neutral, bordered), **Tertiary** (ghost/text), **Destructive** (danger colour, set apart from the others).
- Every interactive element has **default, hover, focus-visible, active, disabled and loading** states.

## Colour roles

`bg · bg-secondary · surface · border · text · text-secondary · text-tertiary · accent · on-accent · success · warning · danger · info` plus a separate **data palette** for charts.

- A mostly greyscale interface. **One accent.** Colour only for primary actions, selection, status and data.
- No raw hex values in components. Light and dark defined for every role.
- Contrast is AA minimum. Colour is never the only signal.

## Borders, shadows and layers

- Separate things with **1px borders or background changes** first.
- Shadows only on **truly floating layers** (menus, popovers, modals, toasts), soft and never glowing.
- Translucency/blur only on the **navigation layer**, never glass on glass, always with a solid fallback.
- Sticky headers gain a border or fade **only once content scrolls under them**.

## Icons

- **Lucide** (or Phosphor, but pick one per project). One stroke weight. Sizes 16 / 20 / 24 only.
- Icon + label in primary navigation. Icon-only only for universal actions, with an accessible name and tooltip.
- **No emojis as UI.** Standard metaphors for standard actions (trash = delete, magnifier = search, gear = settings, × = close).

## Motion

- 150–250ms for UI; ease-out entering, ease-in leaving.
- Only for **feedback, continuity, affordance and state change**. No scroll-jacking, parallax, fly-ins or decorative fades.
- Respect `prefers-reduced-motion`.

## States every data view must have

- **Loading**: a skeleton matching the final layout.
- **Empty**: what goes here, plus the one action that fills it.
- **Error**: what happened, how to fix it, a retry.
- **Partial / too much**: truncation with ellipsis and the full value on hover; pagination with **Load more**; handles 0, 1 and 10,000 items.
- **Success**: a clear completion state (tick, toast, **Undo** for about 5 seconds).

## Loading thresholds

- Under ~100ms: immediate pressed state only.
- ~0.3–1s: skeleton, or a spinner inside the button.
- Over 1s: progress indicator.
- Long jobs: progress plus explanation plus "we'll notify you".

## Destructive actions

- Reversible → do it, toast, **Undo**.
- Irreversible, expensive or affecting others → confirm dialog: "Delete *X*?" + consequence + "This can't be undone" + button "Delete *X*".
- Danger zone → type the name to confirm.

## Verb dictionary (one word per concept)

| Use | Meaning | Never use instead |
|---|---|---|
| **Create** | Make a new object ("Create project") | New, Add (for new objects), Make |
| **Add** | Put an existing thing into a collection ("Add member", "Add to list") | Insert, Attach (unless it's a file) |
| **Edit** | Change an existing object | Modify, Update, Change |
| **Save** | Keep changes | Apply, Submit (except forms sent to others), Confirm |
| **Delete** | Destroy the object | Remove, Trash, Erase, Destroy |
| **Remove** | Take out of a collection; the object still exists ("Remove from team") | Delete (when not destroying) |
| **Archive** | Hide but keep, restorable | Hide, Store |
| **Cancel** | Abandon the current operation | Discard (except for drafts), Abort |
| **Close** | Dismiss a view with nothing lost | Exit, Dismiss |
| **Done** | Finish a multi-step or editing mode | Finish, Complete, OK |
| **Send** | Deliver a message or invite | Submit, Dispatch |
| **Invite** | Ask someone to join | Add user (for people not yet members) |
| **Share** | Give access or a link | Send link, Distribute |
| **Export** / **Import** | Move data out of / into the product | Download (for data exports), Upload (for imports) |
| **Sign in** / **Sign out** / **Sign up** | Auth | Log in, Log out, Register (never mixed) |
| **Settings** | Preferences | Preferences, Options, Config |

- Buttons are **verb + object** when ambiguous ("Delete project"), never "OK" or "Yes".
- Marketing CTAs: **one primary label** used everywhere (e.g. "Start for free") and **one secondary** (e.g. "Book a demo").

## Copy

- Plain language, no jargon, no redundancy.
- Labels describe what things **are**; buttons describe what **will happen**.
- Errors: what happened, why, how to fix. Never blame.
- Marketing: **outcomes over features** ("Turn your data into decisions").

---

# Part 15 — The screen audit: questions I ask of every screen

## Purpose

- [ ] What is the **one question** this screen answers? Could I say it in a sentence?
- [ ] Is there anything here that isn't about that? (Delete it.)
- [ ] Is this screen repeating something that lives elsewhere (KPI cards, analytics)?
- [ ] Does every element help people finish the job they came for?

## Wayfinding

- [ ] Where am I? (Title, active nav item, breadcrumb.)
- [ ] What can I do? (Header actions are clear and relevant.)
- [ ] Where can I go? What will I find there? What's nearby?
- [ ] How do I get out or back?

## Hierarchy and layout

- [ ] Squint: does my eye land on the most important thing first?
- [ ] Is there exactly **one** primary action?
- [ ] Are related things grouped and unrelated things separated?
- [ ] Are controls next to what they affect?
- [ ] Does the control arrangement mirror what it controls (mapping)?
- [ ] Is spacing even and on the scale? Is the layout balanced?
- [ ] Is this the right container (list, table, grid, cards, modal vs panel)?
- [ ] Is progressive disclosure hiding something people need to know exists?

## Visual

- [ ] Only colours from the roles? One accent? Colour only where it means something?
- [ ] Only styles from the type scale? Consistent case?
- [ ] One icon family, one weight, familiar metaphors, no emojis?
- [ ] Same radius on every button; nested corners concentric?
- [ ] Shadows and translucency only on floating layers, never glass on glass?
- [ ] Text over images legible (scrim or blur)?
- [ ] Dark mode checked?

## Behaviour

- [ ] Does every interactive thing *look* interactive, and every static thing look static?
- [ ] Does anything behave differently from what it looks like (the Morty faucet)?
- [ ] Does every action give immediate feedback and a clear completion state?
- [ ] Is every wait covered by a skeleton or progress indicator?
- [ ] Can every mistake be undone? Are irreversible actions confirmed with specific copy?
- [ ] Does every piece of motion tell people something? Does it respect reduced motion?
- [ ] Is validation inline? Do errors explain how to fix them? Does the product infer intent where it safely can?

## Words

- [ ] Plain language? No jargon? No redundancy?
- [ ] Are verbs from the dictionary? Is the same action named the same everywhere?
- [ ] Do buttons say what will happen?
- [ ] Is there context where people need it ("3 credits left", "Updated 2 min ago")?

## Real data and states

- [ ] Tested with long names, huge numbers, missing images, another language, 200% zoom?
- [ ] Empty, loading, error, partial and overflow states designed?
- [ ] Works from phone width to wide desktop, rethought for each rather than squashed?

## People

- [ ] Works with keyboard only? Screen reader? Visible focus?
- [ ] Contrast passes? Colour never the only signal? Touch targets 44px+?
- [ ] Understandable by someone who's never seen it, or who uses it once a month?
- [ ] Works for beginners by default and gives experts shortcuts?
- [ ] Can people personalise what can't suit everyone?

## Responsibility

- [ ] Am I asking for data or permissions only when needed, in context, with a reason?
- [ ] How could this be misused, and who could be harmed?
- [ ] If AI is involved: previews, confirmations, labelling, hard safeguards, undo?
- [ ] No dark patterns anywhere?

## Quality

- [ ] Would I be proud if the person I respect most looked closely at the details?
- [ ] Does it feel like someone thought of the person already?
- [ ] Does it make their life a little easier, or a little better?
- [ ] Will it still look right in five years?
- [ ] Can they **sense the humanity** of whoever made it?

---

## The last word

The principles here are simple. Applying them isn't. Each one can pull me in a different direction, and design is mostly about resolving those tensions with judgment, testing and care.

When I get it right, people won't notice the design. They'll notice that they got what they came for, quickly and confidently, without feeling stupid, and that they'd happily come back. On some level, they'll recognise the hard work and care that went into it.

> **I'm not designing for me. I'm designing for other people. So I make great things for them.**

---

## Sources

- **Mike Stern**, *Essential Design Principles*, WWDC17 (`wwdc17.md`)
- **Lauren Strehlow**, *The Qualities of Great Design*, WWDC18 (`wwdc18.md`)
- **Majo**, Apple Design Evangelism, WWDC25: structure, navigation, content, visual design (`wwdc25-01.md`)
- **Linda & Doug**, *Design Principles*, WWDC26 (`wwdc26-01.md`)
- **Chan, Shubham & Bruno**, *Liquid Glass*, WWDC25 (`liquid-glass.md`)
- **Oliver**, *SaaS UI: The Checklist That Makes Software Look Like a Product People Pay For* (`SAAS-Design.md`)
- Apple **Human Interface Guidelines** (referenced throughout the talks)

*Numbers in Part 14 (spacing, type scale, radii, control heights, motion timings, loading thresholds) are my own working defaults, not taken from the sources. The "No dark patterns" section and the web translations of Apple-specific ideas (semantic tokens, `backdrop-filter`, media queries) are my own extrapolations of the principles above.*
