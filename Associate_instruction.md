# Research Assignment: Justice Position Analysis for Learning Resources v. Trump

## Overview

For each argument in `arguments.json`, review the relevant precedent cases where current Supreme Court justices participated. Your task is to summarize each justice's expressed position on the legal issues underlying that argument, based on their votes, opinions authored, or opinions joined in prior cases.

## Materials Provided

1. **arguments.json** - Contains 18 arguments (8 petitioner, 10 respondent) with:
   - `argument_id`, `summary`, `detail` - the argument being made
   - `relevant_cases[]` - precedent cases supporting/challenging the argument
   - `justice_votes[]` within each case - how current justices voted

2. **case_opinions.json** - Full opinion text for all 30 cases (linked by `case_id`)

3. **Current Justices** (9 total):

| Justice | Position | On Court Since |
|---------|----------|----------------|
| John G. Roberts Jr. | Chief Justice | 2005 |
| Clarence Thomas | Associate Justice | 1991 |
| Samuel A. Alito Jr. | Associate Justice | 2006 |
| Sonia Sotomayor | Associate Justice | 2009 |
| Elena Kagan | Associate Justice | 2010 |
| Neil M. Gorsuch | Associate Justice | 2017 |
| Brett M. Kavanaugh | Associate Justice | 2018 |
| Amy Coney Barrett | Associate Justice | 2020 |
| Ketanji Brown Jackson | Associate Justice | 2022 |

## Instructions

For each argument in `arguments.json`:

### Step 1: Understand the Argument

Read the `summary` and `detail` fields to understand the legal proposition being advanced.

### Step 2: Review Each Relevant Case

For each case in `relevant_cases[]` where `justice_votes` is not empty:

1. **Read the case opinion** in `case_opinions.json` (match by `case_id`)
2. **Focus on the legal issue** that makes this case relevant to the argument (see `relevance` field)
3. **For each justice in `justice_votes[]`:**
   - Note their `vote` (majority, dissent, concurrence)
   - Note their `opinion` role (author, concurring, dissenting, none)
   - If they authored or joined an opinion, identify their reasoning on the relevant legal issue
   - If they merely joined without writing, note which opinion they joined

### Step 3: Summarize Justice Positions

For each argument, create a summary in the following format:

```
ARGUMENT: [argument_id] - [summary]

JUSTICE POSITION SUMMARY:

Roberts, C.J.:
- [Case 1]: [Vote]. [Brief description of position/reasoning if authored or key language joined]
- [Case 2]: [Vote]. [...]
- Overall tendency: [synthesis]

Thomas, J.:
- [Case 1]: [Vote]. [...]
...

[Repeat for each justice with relevant case participation]

PREDICTION NOTES:
[Any patterns or signals about how justices might view this argument]
```

## Vote/Opinion Key

From `justice_votes[]`:
- **vote**: `majority` | `dissent` | `concurrence` | `special_concurrence` | `judgment`
- **opinion**: `author` (wrote the opinion) | `concurring` (wrote concurrence) | `dissenting` (wrote dissent) | `none` (joined without writing)

## Priority Arguments

Focus first on these core arguments where justice positions are most predictive:

1. **ARG-P01 / ARG-R01** - Does "regulate importation" include tariffs? (statutory interpretation)
2. **ARG-P05 / ARG-R04** - Does the Major Questions Doctrine apply?
3. **ARG-R07** - Is nondelegation relaxed for foreign affairs?
4. **ARG-R02** - Yoshida precedent and congressional ratification

## Cases with Most Current Justice Participation

These cases have the most justices participating (prioritize for analysis):

| Case ID | Case Name | Year | # Justices |
|---------|-----------|------|------------|
| 2023-015 | Loper Bright v. Raimondo | 2024 | 9 |
| 2022-038 | Biden v. Nebraska | 2023 | 9 |
| 2021-045 | West Virginia v. EPA | 2022 | 8 |
| 2020-044 | United States v. Arthrex | 2021 | 8 |
| 2020-029 | Collins v. Yellen | 2021 | 8 |
| 2019-071 | Seila Law v. CFPB | 2020 | 7 |
| 2019-074 | Trump v. Mazars | 2020 | 7 |
| 2018-003 | Gundy v. United States | 2019 | 7 |

## Deliverable

A document with justice position summaries for each of the 18 arguments, organized by argument ID. Include citations to specific passages from opinions where justices articulated positions relevant to the IEEPA tariff dispute.

## Notes

- Cases decided before a justice joined the Court will have empty `justice_votes[]` for that case - skip those justices for that case
- Some cases (Yoshida, Gibbons, etc.) have `justice_votes_note` explaining why no current justice data exists - note these as "no current justice participation"
- Pay special attention to opinions by Roberts, Gorsuch, and Kavanaugh on executive power and major questions doctrine, as these are likely swing votes
