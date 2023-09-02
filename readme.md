*Hey! This repository deals with fantasy basketball. If you are unfamiliar with how it works, here are some useful links*
- [*General intro*](https://dunkorthree.com/how-fantasy-basketball-work/)
- [*Scoring formats*](https://support.espn.com/hc/en-us/articles/360003913972-Scoring-Formats)
- [*Snake vs auction drafts*](https://www.dummies.com/article/home-auto-hobbies/sports-recreation/fantasy-sports/fantasy-football/understanding-fantasy-football-snake-and-auction-drafts-149492/)

# Why I think Z-scores can be improved

Quantifying player value across multiple categories is tricky, since it is not immediately obvious how much e.g. a block is worth relative to a steal. There is a standard way to do this, called 'Z-scoring', and it is used to make objective rankings of players. Many drafters who are inexperienced or don’t have the time to do their own research rely exclusively on Z-score rankings, and many others use them as a starting point for more complex strategies. 

However, just because something is standard does not mean that it is correct. I believe that while Z-scores are a sensible heuristic, they do not work as well as an alternative that I call "G-scores", at least in the head-to-head context. I wrote a paper to that effect last month which is available [here](https://arxiv.org/abs/2307.02188).

I realize that challenging Z-scores is fantasy heresy, and many will be skeptical. I also realize that the paper's explanation is incomprehensible to anyone without a background in math. To that end, I am providing a simplified version of the argument in this readme, which hopefully will be easier to follow. It defines Z-scores precisely, presents a logical argument for their use, then refines the argument to derive G-scores

## 1.	What are Z-scores?

You may have come across Z-scores in a stats 101 class. In that context, they are what happens to a set of numbers after subtracting the mean (average) signified by $\mu$ and dividing by the standard deviation (how “spread out” the distribution is) signified by $\sigma$. Mathematically, $Z(x) = \frac{x - \mu}{\sigma}$

This transformation is useful because it takes a set of numbers that could have any scale and remakes them into a new set closely centered around zero. Intuitively, it makes sense to apply it to fantasy basketball, because all categories should be equally important despite having different scales. 

For use in fantasy basketball, a few modifications are made to basic Z-scores 
-	The percentage categories are adjusted by volume. This is necessary because players who shoot more matter more; if a team has one player who goes $9$ for $9$ ($100\\%$) and another who goes $0$ for $1$ ($0\\%$) their aggregate average is $90\\%$ rather than $50\\%$. The fix is to multiply scores by the player's volume, relative to average volume
-	$\mu$ and $\sigma$ are calculated based on the $\approx 150$ players expected to be on fantasy rosters, rather than the entire NBA
  
Denoting
- Player $p$'s average as $m_p$ 
- $\mu$ across players expected to be on fantasy rosters as $m_\mu$
- $\sigma$ across players expected to be on fantasy rosters as $m_\sigma$ 

Z-scores for standard categories (points, rebounds, assists, steals, blocks, three-pointers, and sometimes turnovers) are  

$$
\frac{m_p - m_\mu}{m_\sigma}
$$ 

The same definition can be extended to the percentage categories (field goal % and free throw %). With $a$ signifying attempts and $r$ signifying success rate, their Z-scores are

$$
\frac{\frac{a_p}{a_\mu} \left(r_p - r_\mu \right)}{r_\sigma}
$$

See below for an animation of weekly blocking numbers going through the Z-score transformation step by step. First the mean is subtracted out, centering the distribution around zero, then the standard deviation is divided through to make the distribution more narrow. Note that a set of $156$ players expected to be on fantasy rosters is pre-defined

https://github.com/zer2/Fantasy-Basketball--in-progress-/assets/17816840/5996da7a-a877-4db1-bb63-c25bed81415f

The transformation looks similar for all the other categories. 

Adding up the results for all categories yields an aggregate Z-score, which provides an intuitive quantification of overall player value

## 2. Justifying Z-scores

As I said before, I think Z-scores are suboptimal. But there is a sense in which they do work, and before getting into their flaws, it is helpful to understand the positive case for them.

The proof will consider Z-scores in the context of the "Head-to-Head: Each Category" format, because it is relatively easy to analyze compared to the other head-to-head format, "Most Categories"

### A. Assumptions and setup

Z-scores can be derived by asking the question: **if team one has $N-1$ players, randomly selected from a pool of players, and team two has $N$ players chosen randomly from the same pool, which player should the first team choose as their next player**? This question implicitly assumes that besides the player currently being chosen, all other players from both teams are selected randomly from a pool of high-performing players. This assumption is obviously not exactly true, since drafters are trying to take the strongest players available, not choosing at random. But some kind of simplifying assumption is necessary to derive a tidy heuristic. And this is not a completely crazy one, since all teams will always have some strong and some weak players chosen from a variety of positions, making them random-ish in aggregate. 

Let's imagine a league where $N=12$ and team one is choosing a player. The assumptions tells us that team one has $11$ other randomly chosen players, and team two has $12$ randomly chosen players. With all of this information, we can brute-force calculate the probability that team one wins based on the statistics of the player they are choosing, and try to optimize for it

### B.	Category differences

The difference in category score between two teams tells us which team is winning the category and by how much. By randomly selecting the $23$ random players many times, we can get a sense of what team two's score minus team one's score will be before the last player is added. See this simulation being carried out for blocks below

https://github.com/zer2/Fantasy-Basketball--in-progress-/assets/17816840/73c3acaa-20c9-4a61-907a-ee0de2ff7e3b

You may notice that the result looks a lot like a Bell curve even though the raw block numbers look nothing like a Bell curve. This happens because of the surprising "Central Limit Theorem", which says that when adding a bunch of random numbers together, their average (or sum) always ends up looking a lot like a Bell curve. Ergo if we ran this experiment for other categories, the results would also look like Bell curves

### C.	Properties of the category difference

Bell curves are fully defined by their mean and standard deviation. That is to say, once we know a Bell curve's mean and standard deviation, we can calculate everything else about it.

The mean and standard deviation of our Bell curves can be calculated via probability theory. Including the unchosen player with category average $m_p$
- The mean is $m_\mu - m_p$
- The standard deviation is $\sqrt{23} * m_\sigma$ (The square root in the formula comes from the fact that $STD(X + Y) = \sqrt{STD(X)^2 + STD(Y)^2}$ where $STD(X)$ is the standard deviation of $X$)

### D.	Calculating probability of victory

When the category difference is below zero, team one will win the category

The probability of this happening can be calculated using something called a cumulative distribution function. $CDF(x) =$ the probability that a particular distribution will be less than $x$. We can use $CDF(0)$, then, to calculate the probability that the category difference is below zero and team one wins. 

The $CDF$ of the Bell curve is well known. The details of how to apply it to this case are somewhat complicated, but we can cut to the chase and give an approximate formula 

$$
CDF(0) = \frac{1}{2}\left[ 1 + \frac{2}{\sqrt{\pi}}* \frac{- \mu }{ \sigma} \right]
$$

We already know $\mu$ and $\sigma$ for the standard statistics. Substituting them in yields

$$
CDF(0) = \frac{1}{2}\left[ 1 + \frac{2}{\sqrt{23 \pi}}* \frac{m_p – m_\mu}{m_\sigma} \right]
$$

And analagously for the percentage statistics 

$$
CDF(0) = \frac{1}{2} \left[ 1 + \frac{2}{\sqrt{23 \pi}} * \frac{ \frac{a_p}{a_\mu} \left( r_p – r_\mu \right) }{r_\sigma}\right]
$$

### D. Implications for Z-scores

The last two equations included Z-scores. Adding up all the probabilities to get the expected number of categories won by team one, with $Z_{p,c}$ as player $p$'s Z-score for category $c$, the formula is

$$
\frac{1}{2}\left[9 + \frac{2}{\sqrt{23 \pi}} * \sum_c Z_{p,c} \right]
$$

We can see that the expected number of category victories is directly proportional to the sum of the unchosen player's Z-scores. This tells us that the higher a player's total Z-score is, the better they are for fantasy, at least under the assumptions we have made. 

This seems like a compelling case for Z-scores as a heuristic. So what's my problem with them?

## 3.The flaw of Z-scores

Sneakily, the previous section relied on the assumption that each player would score a pre-determined amount in each category. That's not the case at all in reality- head-to-head matchups are weekly affairs, and performances can vary significantly from one week to the next. We should have been randomly sampling both players and weekly performances. 

Below, see how metrics for blocks change when we do so

https://github.com/zer2/Fantasy-Basketball--in-progress-/assets/17816840/ab41db2a-99f2-45b1-8c05-d755c014b30f

Although the mean remains the same, the standard deviation is larger because it incorporates an additional term for week-to-week variation. Note that the new standard deviation is $\sqrt{m_\sigma^2 + m_\tau^2}$ rather than $m_\sigma + m_\tau$ because of how standard deviation aggregates across multiple variables, as discussed in section 2B

## 4.	Reformulating Z-scores 

We can retrace our steps from section 2, except replacing $m_\sigma$ with $\sqrt{m_\sigma^2 + m_\tau^2}$. For standard categories this yields scores of 

$$
\frac{m_p – m_\mu}{\sqrt{m_\sigma^2 + m_\tau^2}} 
$$

And analagously for the percentage statistics, 

$$
\frac{\frac{a_p}{a_\mu} \left( r_p – r_\mu \right) }{\sqrt{r_\sigma^2 + r_\tau^2}} 
$$

I call these G-scores, and it turns out that these are quite different from Z-scores. For example, steals have a very high week-to-week standard deviation, and carry less weight in G-scores than Z-scores as a result. 

This matches with the way many fantasy players think about volatile categories like steals; they know that a technical advantage in them based on Z-scores is flimsy so they prioritize them less. Why invest strongly in steals, when you will lose the category often anyway due to bad luck? The G-score idea just converts that intuition into a mathematical rigor.

It is easy to confirm that upon reflection, G-scores are more sensible than Z-scores. Consider the following two scenarios
- Your opponent has Joel Embiid. He will score either $60$, $70$, or $80$ points across the week
- You don't know if your opponent has Jayson Tatum, Joel Embiid, or Luka Doncic. Tatum will score $60$ points, Embiid will score $70$, and Doncic will score $80$
  
From your perspective, these two scenarios are the same. Therefore any sensible scoring system should treat player-to-player standard deviation and week-to-week standard deviation in the same way, which G-score does and Z-score does not

## 5.	Simulation results

All of our logic has relied on the simplifying assumption that other drafters are picking players randomly, which is definitely innacurate. We can't take it for granted that G-scores actually work when that assumption is removed. We can, however, simulate actual drafts and see how G-score does against Z-score. 

The code in this repository simulates fantasy basketball with the following parameters 
- $12$ teams compete, each with $13$ players
- The format is "Head-to-Head: Each Category"
- Players are chosen in a snake draft
- Teams consist of $2$ centers, $1$ point guard, $1$ shooting guard, $2$ guards, $1$ small forward, $1$ power forward, $2$ forwards, and $3$ utilities (wildcards). All games played are counted
- All drafters pick the highest-ranking available player that could fit on their team, based on empirically correct rankings for the season
- Coefficients for Z-scores and G-scores are calculated based on a set of $156$ top players calculated by raw Z-score across the NBA 
- Actual weekly performances are sampled for each player for each of $25$ weeks
- The team with the best record wins. There are no playoffs
- Strategies are tested $10,000$ times at each initial drafting position

The expected win rate if all strategies are equally good is $\frac{1}{12} = 8.33\\%$. Actual results are shown below for 9-Cat, which includes all categories, and 8-Cat, a variant which excludes turnovers 

|     | G-score vs 11 Z-score | Z-score vs. 11 G-score|
| -------- | ------- |------- |
| __9-Cat__    |  | |
| 2021  | $15.9\\%$   | $1.5\\%$  |
| 2022 | $14.3\\%$   | $1.3\\%$  |
| 2023    | $21.7\\%$    | $0.4\\%$  |
| Overall    | $17.3\\%$    | $1.4\\%$ |  
| __8-Cat__    |  | |
| 2021  | $10.7\\%$   | $2.9\\%$  |
| 2022 | $12.0\\%$   | $1.5\\%$  |
| 2023    | $15.4\\%$    | $0.9\\%$  |
| Overall    | $12.7\\%$    | $1.8\\%$ |  

When interpreting these results, it is important to remember that they are for an idealized version of fantasy basketball. The real thing is much more complicated due to uncertainties about long-term means for players, waiver wire moves, and more advanced strategies like punting. We can't expect the G-score to do this well in real life. Still, the dominance displayed by G-scores in the simulations is evidence that the assumption of randomness wasn't too problematic, and the G-score modification really is appropriate for "Head-to-Head: Each Category".

To confirm the intuition about why the G-score works, take a look at its win rates by category against $11$ Z-score drafters in 9-Cat

|     | G-score win rate | 
| -------- | ------- |
| Points  | $77.7\\%$   | 
| Rebounds | $70.8\\%$   | 
| Assists    | $81.6\\%$    | 
| Steals    | $25.7\\%$    |  
| Blocks  | $44.9\\%$   | 
| Three-pointers | $77.3\\%$   | 
| Turnovers    | $16.2\\%$    | 
| Field goal %    | $34.9\\%$    | 
| Free throw %    | $40.6\\%$    | 
| Overall   | $52.2\\%$    | 

The G-score drafter performs well in stable/high-volume categories like assists and poorly in volatile categories like turnovers, netting to an average win rate of slightly above $50\\%$. As expected, the marginal investment in stable categories is worth more than the corresponding underinvestment in volatile categories, since investment in stable categories leads to reliable wins and the volatile categories can be won despite underinvestment with sheer luck. 

Simulations also suggest that G-scores work better than Z-scores in the "Head-to-Head: Most Categories" format. I chose not to include the results here because it is a very strategic format, and expecting other drafters to go straight off ranking lists is probably unrealistic for it. Still, it stands to reason that if you want to optimize over a subset of categories for "turtling" or "punting", it makes sense to quantify value with a subset of category G-scores rather than Z-scores.

Another possible use-case is auctions. There is a well-known procedure for translating player value to auction value, outlined e.g. [in this article](https://www.rotowire.com/basketball/article/nba-auction-strategy-part-2-21393). If the auction is for a head-to-head format, it is reasonable to use G-scores to quantify value rather than Z-scores

## Addendum 1 : Other formats  

This analysis has focused on the head-to-head formats. For completeness' sake, here are my thoughts on why there are no implications for other formats 
- "Rotisserie": Since Rotisserie uses full-season scores, week-to-week variance is irrelevant and Z-scores still make sense
- "Head-to-Head: Points"/"Season Points": Points leagues don't use category scoring, so neither Z-scores nor G-scores are applicable 

## Addendum 2: Further improvement 

Any situation-agnostic value quantification system is subptimal, since a truly optimal strategy would adapt to the circumstances of the draft/auction. 

In the paper, I outline a methodology called H-scoring that dynamically chooses players based on the drafting situation. It performs significantly better than going straight off G-score and Z-score. However, it is far from perfect, particularly because it does not fully understand the consequences of punting. There is a lot of room for improvement and I hope that I, or someone else, can make a better version in the future! 

