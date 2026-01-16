# I Used Claude Code To Predict How the Supreme Court Will Rule on Trump's Tariffs

*Learning Resources v. Trump*—a case that could determine whether a president can impose trillions of dollars in tariffs by declaring a "national emergency" over trade deficits. The legal question is narrow: does the word "regulate" in a 1977 statute include the power to tax? The practical stakes are enormous.

I wanted to know how the Court would rule. Not as punditry—everyone has opinions—but as a genuine empirical question. Could I build a system that examines how each justice has actually voted in similar cases, feeds that data to an AI model, and produces probability estimates?

Here's what I built, how I built it, and what it found, with a somewhat surprising prediction. 

## The Problem: Nine People, Infinite Variables

Predicting Supreme Court votes is a cottage industry. Academics build statistical models. Lawyers read tea leaves in oral argument questions. Journalists may quote "sources close to the Court." Most of this is educated guessing.

The challenge is that each justice has a complex jurisprudence—decades of opinions, concurrences, and dissents across hundreds of cases. No human can hold all of that in memory while analyzing a new case. But a large language model can.

My approach was simple in concept: gather every relevant data point about how each justice has voted on related legal issues, structure it carefully, and ask Claude (Anthropic's AI model) to synthesize it into probability estimates.

## The Data Pipeline

I built a pipeline with four main components.

**First, the arguments.** I instructed the model to extract every legal argument from the case—18 distinct claims, organized by issue. The petitioner (Learning Resources) argues the president lacks statutory authority for tariffs and that the Major Questions Doctrine requires Congress to speak clearly when delegating such vast power. The government argues "regulate" has always included tariffs and that courts should defer to presidential emergency determinations in foreign affairs.

**Second, the precedents.** For each argument, I identified which Supreme Court cases would be most relevant—cases on executive authority, delegation doctrine, statutory interpretation, and emergency powers. The Spaeth Supreme Court Database gave me structured data on 30 relevant cases from 1952 to 2024.

**Third, the votes.**  For every case in my precedent list, I pulled each current justice's actual vote: majority, dissent, or concurrence. Did Justice Thomas vote with the majority in *Loper Bright v. Raimondo*? (Yes, he did.) Did Justice Sotomayor dissent in *West Virginia v. EPA*? (Yes, strongly.) This creates a map of where each justice stands on the legal principles at stake.

**Fourth, the opinions.** Votes alone don't capture everything. A justice who writes the majority opinion is more committed to its reasoning than one who merely joins. I pulled full opinion texts from CourtListener's API—majority opinions, concurrences, dissents—for every relevant case where current justices participated. The model then analyzed each justice's reasoning in those opinions, extracting the principles and frameworks they applied.

## Instructing the AI 

With all this data, I ran two separate analyses.

**First pass: Position analysis.** I asked Claude to analyze, for each argument in the case, how each justice's prior opinions and votes would likely inform their view. This produced a detailed report—essentially a research memo showing which precedents cut which way for each justice on each legal issue.

**Second pass: Probability synthesis.** Taking the position analysis as input, I then asked the model to synthesize everything into probability estimates.

**Third pass: Oral argument validation.** After the Court heard the case, I fed the 190-page oral argument transcript to the model and asked it to compare each justice's actual questioning against the predicted positions. This served as a sanity check—if a justice we predicted at 78% for petitioner was lobbing softballs at the government, something would be off.

The probability synthesis prompt included:

- The full factual and legal context of *Learning Resources v. Trump*
- Each of the 18 arguments, organized by side
- The first-pass position analysis for each justice
- The full text of key opinions

For each of the nine justices, I asked for:

1. A probability estimate (0-100%) of voting for the petitioner
2. A confidence rating (high, medium, low)
3. Key factors favoring each side
4. The critical uncertainty that could change the estimate
5. A synthesis explaining the reasoning

I deliberately avoided partisan framing. The model saw only jurisprudential data—past votes, past opinions, legal principles. It had no information about which president appointed each justice or their presumed political leanings.

## The Results

The model predicted a **6-3 victory for the petitioner**, with these individual probabilities:

| Justice | P(Petitioner) | Confidence |
|---------|---------------|------------|
| Gorsuch | 78% | High |
| Thomas | 72% | Medium-High |
| Alito | 65% | Medium |
| Roberts | 62% | Medium |
| Kavanaugh | 60% | Medium-Low |
| Barrett | 58% | Medium-Low |
| Kagan | 28% | Medium |
| Sotomayor | 25% | Medium-High |
| Jackson | 22% | Medium |

Justice Gorsuch emerged as the most predictable vote for the petitioner. His 2019 dissent in *Gundy v. United States* provides a comprehensive three-part framework for limiting delegation of legislative power. While he acknowledged that broader delegation may be permissible in foreign affairs where presidential Article II powers overlap, the tariff claims fit his broader concerns about congressional abdication. Chief Justice Roberts' majority opinion in *West Virginia v. EPA* criticized the EPA for claiming to discover "an unheralded power representing a transformative expansion of its regulatory authority in the vague language of a long-extant, but rarely used, statute designed as a gap filler." The petitioner argues the government's IEEPA reading fits this pattern.

The swing votes are Kavanaugh and Barrett. Both have supported the Major Questions Doctrine in prior cases, but neither has a clear record on foreign affairs deference. Barrett's concurrence in *Biden v. Nebraska* reframes the Major Questions Doctrine as a contextual tool of ordinary statutory interpretation, pushing back against strong clear-statement or substantive-canon versions of the doctrine—which could cut either way here.

## The Counterintuitive Finding

Here's what surprised me: the three liberal justices are predicted to vote *for* the Trump administration's tariff authority.

At first glance, this seems backwards. Justices Sotomayor and Kagan dissented in *Trump v. Hawaii*. They're generally skeptical of expansive executive power claims.

But the model isn't tracking politics—it's tracking doctrine. And doctrinally, the liberal justices have consistently opposed the Major Questions Doctrine. Justice Kagan authored the *Gundy* plurality defending broad congressional delegation, joined by Sotomayor. Kagan's *West Virginia v. EPA* dissent called MQD a "get-out-of-text-free card" that "appoints [the Court] instead of Congress or the expert agency—the decision-maker on climate policy." In *Biden v. Nebraska*, Kagan's dissent (joined by Jackson) continued this critique.

Their jurisprudential commitment to rejecting MQD is stronger than any situational distaste for this particular president's tariffs. Doctrine, it turns out, is stickier than politics.

## Validation Against Oral Argument

After generating these predictions, I tested them against the oral argument transcript. The 190-page transcript shows each justice's actual questioning of both sides.

The predictions held up well:

**Gorsuch (predicted 78%)** was relentlessly skeptical of the government's position. He pressed repeatedly on the nondelegation implications: "Could Congress delegate to the President the power to regulate commerce with foreign nations as he sees fit—to lay and collect duties as he sees fit?" When the government demurred, he pushed harder: "What would prohibit Congress from just abdicating all responsibility to regulate foreign commerce, for that matter, declare war, to the President?" He forced the government to concede that some nondelegation principle must apply even in foreign affairs—then noted dryly, "I'm delighted to hear that."

**Roberts (predicted 62%)** focused on the Major Questions Doctrine: "You have a claimed source in IEEPA that had never before been used to justify tariffs. No one has argued that it does until this particular case... the justification is being used for a power to impose tariffs on any product from any country for—in any amount for any length of time. That seems like... major authority, and the basis for the claim seems to be a misfit." His questions tracked his *West Virginia v. EPA* framework precisely.

**Barrett (predicted 58%)** pressed the government on textual grounds: "Can you point to any other place in the Code or any other time in history where that phrase together, 'regulate importation,' has been used to confer tariff-imposing authority?" When the government could only cite the contested TWEA interpretation, she kept pushing: "So the answer is the contested application in TWEA and then now in IEEPA?" Her skepticism of novel statutory claims aligns with her textualist approach.

**Sotomayor (predicted 25%)** was skeptical of the government—but through a textual lens, not MQD. She pressed hard on the taxing power: "It's not an article. It's a congressional power, not a presidential power, to tax. And you want to say tariffs are not taxes, but that's exactly what they are." She noted Congress has always paired "tariff" and "regulate" when it meant to authorize tariffs, but didn't here. Her skepticism ran through separation-of-powers and statutory structure, not the Major Questions framework.

**Jackson (predicted 22%)** emphasized IEEPA's legislative history: "IEEPA was designed and intended to limit presidential authority... Congress was trying to constrain the emergency powers of the President." She pressed the government on the contradiction: "It seems a little inconsistent to say that we have to interpret a statute that was designed to constrain presidential authority consistent with an understanding that Congress wanted the President to have essentially unlimited authority." Like Sotomayor, she didn't deploy the MQD framework—but her skepticism was clear.

**A complication for the model's predictions:** The oral argument reveals that Sotomayor and Jackson were both skeptical of the government—just through different doctrinal lenses than the conservatives. The model assumed their opposition to MQD would lead them to uphold broad executive authority. But neither justice needs MQD to rule against the government. Sotomayor has a textual path (taxing power belongs to Congress). Jackson has a legislative history path (IEEPA was designed to constrain, not expand). If they find these independent routes to the same destination, the outcome could be more lopsided than 6-3—possibly 8-1 or even 9-0. The model may have over-weighted their MQD opposition and under-weighted their willingness to reach the petitioner's result by other means.

## What This Means

A few observations.

**With proper infrastructure, AI can add real value to legal analysis.** The model isn't doing magic—it's synthesizing patterns across a large corpus of data that humans struggle to hold in working memory. Every piece of input data is public. The value is in the structured synthesis.

**Doctrine matters more than politics.** Media coverage often frames Supreme Court cases as political conflicts. But justices have developed jurisprudences over decades, and those frameworks constrain their votes more than casual observers expect. The liberal justices aren't going to abandon their opposition to MQD because they dislike Trump's tariffs.

**Uncertainty is honest.** The model didn't produce false precision. It gave Kavanaugh and Barrett "Medium-Low" confidence ratings, acknowledging their limited records on foreign affairs questions. It identified specific uncertainties that could change each estimate.

## The Limitations

This approach has real limitations.

The model only knows what I fed it. If there's relevant jurisprudence I missed, the analysis and predictions suffer. The precedent selection relied on the Spaeth database's issue and legal provision codes—comprehensive for coded cases, but potentially missing relevant opinions that don't fit neatly into those categories. A more robust approach would supplement Spaeth with keyword and semantic search across the full corpus of Supreme Court opinions, catching cases that share reasoning patterns even if they address different statutory provisions.

Oral argument performance matters in ways that are hard to quantify. A justice might be genuinely persuaded by an advocate's response, or might be testing arguments they'll ultimately reject. The model can't distinguish.

And of course, justices occasionally surprise everyone. They change their minds. They find case-specific factors that override their general frameworks. A 62% probability still means a 38% chance of the opposite outcome.

## The Code

The full pipeline consists of eight Python scripts, each handling a specific step:

1. **extract_arguments.py** — Parse briefs into structured argument objects
2. **add_relevant_cases.py** — Query Spaeth database for precedent cases
3. **add_case_urls.py** — Link cases to CourtListener
4. **add_justice_votes.py** — Extract each justice's vote per case
5. **extract_opinions.py** — Pull full opinion text via API
6. **analyze_justice_positions.py** — First-pass analysis per argument
7. **estimate_justice_probabilities.py** — Final probability synthesis
8. **md_to_pdf.py** — Format output for human review

The total cost was about $15 in API calls. Total time spent was about 4 hours. The Spaeth database and CourtListener are free.

## What Happens Next

Soon, the Court will issue its opinion. If the model is right, Learning Resources wins 6-3, and the president's tariff authority under IEEPA is sharply limited. If it's wrong, we'll learn something about the model's blind spots.

Either way, the exercise was worthwhile. The data exists—decades of opinions, votes, and reasoning patterns, all public. We now have models capable of synthesizing it. The question is whether we use them. 

Future improvements could include supplementing the Spaeth database with keyword and semantic search to surface relevant cases that don't fit neatly into coded categories, fine-tuning a model on each justice's reasoning frameworks, training on legal issue spotting, and adding human-in-the-loop checkpoints throughout the research process. 


## For the Adventurous

If you're the type who puts money where your analysis is, prediction markets offer a way to test these estimates against the crowd. 

---

*The code and full analysis are available at [repository link]. The case is Learning Resources v. Trump, No. 25-XXX.*

This is a first attempt, not a finished product. Better precedent retrieval, model fine-tuning on judicial reasoning, human-in-the-loop validation, and systematic evaluation against historical outcomes could all improve accuracy. If you're working on similar problems—or want to—I'd welcome ideas, suggestions, or collaboration.

---

**Disclaimer:** This is an experiment—one of the first steps toward deploying language models as part of empirical legal research. It is not legal advice. Do not rely on this analysis when placing bets or making decisions.

**Data Sources:**
- Harold J. Spaeth, Lee Epstein, Andrew D. Martin, Jeffrey A. Segal, Theodore J. Ruger, Sara C. Benesh, and Michael J. Nelson. 2025 Supreme Court Database, Version 2025 Release 01. http://supremecourtdatabase.org
- CourtListener, Free Law Project. https://www.courtlistener.com
