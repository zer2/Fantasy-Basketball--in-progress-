*Hey! This repository concerns fantasy basketball. If you are unfamiliar with how it works, here are some useful links*
- [*General intro*](https://dunkorthree.com/how-fantasy-basketball-work/)
- [*Scoring formats*](https://support.espn.com/hc/en-us/articles/360003913972-Scoring-Formats)
- [*Snake vs auction drafts*](https://www.dummies.com/article/home-auto-hobbies/sports-recreation/fantasy-sports/fantasy-football/understanding-fantasy-football-snake-and-auction-drafts-149492/)

# Why I think Z-scores can be improved

Quantifying player value across multiple categories is tricky, since it is not immediately obvious how much e.g. a block is worth relative to a steal. There is a standard way to do this, called 'Z-scoring'. Many drafters who are inexperienced or don’t have the time to do their own research rely exclusively on Z-score rankings, and many others use them as a starting point for more complex strategies. 

However, just because something is standard does not mean that it is correct. I believe that while Z-scores are a sensible heuristic, they are suboptimal and inferior to an alternative scoring system that I call the G-score, at least in the head-to-head context. I wrote a paper to that effect last month which is available [here](https://arxiv.org/abs/2307.02188).

I realize that challenging Z-scores is fantasy heresy, and many will be skeptical. I also realize that the paper's explanation is incomprehensible to anyone without a background in math. To that end, I am providing a simplified version of the argument in this readme, which hopefully will be easier to follow. It will define Z-scores precisely, present a logical argument for their use, then improve the argument to derive G-scores as a more appropriate ranking system

## 1.	What are Z-scores?

You may have come across Z-scores in a stats 101 class. In that context, they are what happens to a set of numbers after subtracting the mean (average) written as $\mu$ and dividing by the standard deviation (how “spread out” the distribution is) written as $\sigma$. Mathematically, $Z(x) = \frac{x - \mu}{\sigma}$. 

This transformation is useful because it takes a set of numbers that could have any scale and remakes them into a new set closely centered around zero. Intuitively, it makes sense to apply it to fantasy basketball, because all categories should be equally important despite having different scales. 

For use in fantasy basketball, a few modifications are made to basic Z-scores 
-	The percentage categories are adjusted by volume. This is necessary because players who shoot more matter more; if a team has one player who goes $9$ for $9$ ($100\\%$) and another who goes $0$ for $1$ ($0\\%$) their aggregate average is $90\\%$ rather than $50\\%$. The fix is to multiply scores by the player's volume, relative to average volume
-	$\mu$  and $\sigma$ are calculated based on players expected to be on fantasy rosters, rather than the entire NBA. Players expected to sit on the bench all season never get drafted into fantasy leagues and should be irrelevant. Usually the set of top players is approximated by using Z-score calculated across the entire NBA, then Z-scores are recalculated based on $\mu$ and $\sigma$ of the top players

To formally define Z-scores, consider
- $m_p$ as player $p$'s average
- $m_\mu$ as the average for a top player
- $m_\sigma$ as the standard deviation across top players

Z-scores for standard categories are  then 

$$
\frac{m_p - m_\mu}{m_\sigma}
$$ 

And for the percentage categories, with $a$ signifying attempts and $r$ signifying success rate, Z-scores are

$$
\frac{\frac{a_p}{a_\mu} \left(r_p - r_\mu \right)}{r_\sigma}
$$

See below for an animation of weekly blocking numbers going through the Z-score transformation step by step. First the mean is subtracted out, centering the distribution around zero, then the standard deviation is divided through to make the distribution more narrow. Note that a set of 156 top players has already been defined

https://github.com/zer2/Fantasy-Basketball--in-progress-/assets/17816840/5996da7a-a877-4db1-bb63-c25bed81415f

The transformation looks similar for all the other categories. The sum of the resulting Z-scores from all of them is the aggregate Z-score, which provides an intuitive quantification of overall player value

## 2. Justifying Z-scores

As I said before, I think Z-scores are suboptimal. But there is a sense in which they do work, and before getting into their flaws, it is helpful to understand the positive case for them.

The proof will consider Z-scores in the context of the "Head-to-Head: Each Category" format, because it is relatively easy to analyze compared to "Head-to-Head: Most Categories." 

### A. Assumptions and setup

The case for Z-scores utilizes the simplifying assumption that besides the player currently being chosen, all other players are chosen randomly from a pool of high-performing players. This assumption is obviously not exactly true, since drafters are trying to take the strongest players available, not choosing at random. But a heuristic as elegant as Z-scores could not be derived without this kind of simplifying assumption. 

Say team one is picking a player in a league with twelve players per team. Besides the unchosen player, they will have eleven other randomly chosen players. Their opponents will all have twelve randomly chosen players. With all of this information, we can brute-force calculate the probability that team one wins based on the statistics of the player they are choosing, and try to optimize for it

### B.	Category differences

The difference in category score between two teams tells us which team is winning the category and by how much. By randomly selecting the 23 random players many times, we can get a sense of what team two's score minus team one's score will be before the last player is added. See this simulation being carried out for blocks below

https://github.com/zer2/Fantasy-Basketball--in-progress-/assets/17816840/73c3acaa-20c9-4a61-907a-ee0de2ff7e3b

You may notice that the result looks a lot like a Bell curve even though the raw block numbers look nothing like a Bell curve. This happens because of the surprising "Central Limit Theorem", which says that when adding a bunch of random numbers together, their average (or sum) always ends up looking a lot like a Bell curve. This means that differences for all categories will look like Bell curves

### C.	Properties of the category difference

Bell curves are fully defined by their mean and standard deviation. That is to say, once we know a Bell curve's mean and standard deviation, we can calculate anything else about it.

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

This seems like a compelling case for Z-scores as a heuristic. But is there any way for the logic to be improved?

## 3.The flaw of Z-scores

Sneakily, the previous section relied on the assumption that each player would score a pre-determined amount in each category. That's not the case at all in reality- head-to-head matchups are weekly affairs, and performances can vary significantly from one week to the next. Randomly choosing weekly performances would have made the scenario more realistic. 

Below, see how standard deviation changes for blocks when randomly selecting both player and performance

https://github.com/zer2/Fantasy-Basketball--in-progress-/assets/17816840/ab41db2a-99f2-45b1-8c05-d755c014b30f

Although the mean remains the same, the standard deviation is larger because it incorporates week-to-week variation. Note that it is $\sqrt{m_\sigma^2 + m_\tau^2}$ rather than $m_\sigma + m_\tau$ because of how standard deviation aggregates across multiple variables, as discussed in section 2B

## 4.	Reformulating Z-scores 

It stands to reason that the logic from section 2 can be improved by replacing $m_\sigma$ with $\sqrt{m_\sigma^2 + m_\tau^2}$. For standard categories, this yields scores of 

$$
\frac{m_p – m_\mu}{\sqrt{m_\sigma^2 + m_\tau^2}} 
$$

And analagously for the percentage statistics, 

$$
\frac{\frac{a_p}{a_\mu} \left( r_p – r_\mu \right) }{\sqrt{r_\sigma^2 + r_\tau^2}} 
$$

I call these G-scores, and it turns out that these are quite different from Z-scores. For example, steals have a very high week-to-week standard deviation, and carry less weight in G-scores than Z-scores as a result. 

This matches with the way many fantasy players think about volatile categories like steals; they know that a technical advantage in them based on Z-scores is flimsy so they prioritize them less. The G-score idea just converts that intuition into a mathematical rigor

## 5.	Simulation results

All of our logic has relied on the simplifying assumption that other drafters are picking players randomly, which is definitely innacurate. We can't take it for granted that G-scores actually would work when that assumption is removed. We can, however, simulate actual drafts and see how G-score does compared to Z-score. 

The code in this repository simulates fantasy basketball with the following parameters 
- 12 teams compete, each with 13 players. The expected win rate is $\frac{1}{12} = 8.33\\%$
- The format is "Head-to-Head: Each Category"
- Players are chosen in a snake draft
- Teams consist of 2 C, 1 PG, 1 SG, 2 G, 1 SF, 1 PF, 2F, 3 Utility. All games played are counted
- All drafters pick the highest-ranking available player that could fit on their team, based on empirically correct rankings for the season
- Actual weekly performances are sampled for each player for each of twenty-five weeks
- The team with the best record wins (there are no playoffs)
- Strategies are tested 10,000 times at each initial drafting position

Results are shown below 

https://github.com/zer2/Fantasy-Basketball--in-progress-/assets/17816840/a7f56aea-dc05-4b0f-89df-9044c2275024

When interpreting these results, it is important to remember that they are for an idealized version of fantasy basketball. The real thing will be much more complicated due to uncertainties about long-term means for players, waiver wire moves, and more advanced strategies like punting. We can't expect the G-score to do this well in real life. Still, the dominance displayed by G-scores in the simulations is evidence that our logic makes sense, and the G-score modification really is appropriate for "Head-to-Head: Each Category".

Simulations also suggest that G-scores work better than Z-scores in the "Head-to-Head: Most Categories" format. I chose not to include the results here because it is a very strategic format, and expecting other drafters to go straight off ranking lists is probably unrealistic for it. Still, it stands to reason that if you want to optimize over a subset of categories for "turtling" or "punting", it makes sense to quantify value with a subset of category G-scores rather than Z-scores.

Another possible use-case is auctions. There is a well-known procedure for translating player value to auction value, outlined e.g. [in this article](https://www.rotowire.com/basketball/article/nba-auction-strategy-part-2-21393). If the auction is for a head-to-head format, it is reasonable to use G-scores to quantify value rather than Z-scores

## Addendum 1 : Other formats  

This analysis has focused on the head-to-head formats. For completeness' sake, here are my thoughts on why there are no implications for other formats 
- "Rotisserie": Since Rotisserie uses full-season scores, week-to-week variance is irrelevant and Z-scores still make sense
- "Head-to-Head: Points"/"Season Points": Points leagues don't use category scoring, so neither Z-scores nor G-scores are applicable 

## Addendum 2: Further improvement 

Any situation-agnostic value quantification system is subptimal, since a truly optimal strategy would adapt to the circumstances of the draft/auction. 

In the paper, I outline a methodology called H-scoring that dynamically chooses players based on the drafting situation. It performs significantly better than going straight off G-score and Z-score. However, it is far from perfect, particularly because it does not fully understand how to incorporate punting. There is a lot of room for improvelemt and I hope that I, or someone else, can make a better version in the future! 

