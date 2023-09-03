*Hey! This repository deals with fantasy basketball. If you are unfamiliar with how it works, here are some useful links*
- [*General intro*](https://dunkorthree.com/how-fantasy-basketball-work/)
- [*Scoring formats*](https://support.espn.com/hc/en-us/articles/360003913972-Scoring-Formats)
- [*Snake vs auction drafts*](https://www.dummies.com/article/home-auto-hobbies/sports-recreation/fantasy-sports/fantasy-football/understanding-fantasy-football-snake-and-auction-drafts-149492/)

# Z-scores are great- but not the best for H2H

Quantifying player value across multiple categories is tricky, since it is not immediately obvious how much e.g. a block is worth relative to a steal. There is a standard way to do this, called 'Z-scoring', and it is used to make objective rankings of players. Many drafters who are inexperienced or don’t have the time to do their own research rely exclusively on Z-score rankings, and many others use them as a starting point for more complex strategies. 

As far as I know, nobody has ever laid out exactly why Z-scores should work. They just seem intuitively sensible, so people use them.

I looked into the math and did manage to derive a justification for Z-scores. However, the justification is only appropriate for the Rotisserie format. When the math is modified for head-to-head formats, a different metric that I call "G-score" pops out as the optimal way to rank players instead. I wrote a paper to that effect last month which is available [here](https://arxiv.org/abs/2307.02188).

I realize that challenging Z-scores is fantasy heresy, and many will be skeptical. I also realize that the paper's explanation is incomprehensible to anyone without a background in math. To that end, I am providing a simplified version of the argument in this readme, which hopefully will be easier to follow. It defines Z-scores precisely, presents a logical argument for their use in Rotisserie, then presents a modified argument for head-to-head to derive G-scores

## 1.	What are Z-scores?

You may have come across Z-scores in a stats 101 class. In that context, they are what happens to a set of numbers after subtracting the mean (average) signified by $\mu$ and dividing by the standard deviation (how “spread out” the distribution is) signified by $\sigma$. Mathematically, $Z(x) = \frac{x - \mu}{\sigma}$

This transformation is useful because it takes a set of numbers that could have any scale and remakes them into a new set closely centered around zero. Intuitively, it makes sense to apply it to fantasy basketball, because all categories should be equally important despite having different scales. 

For use in fantasy basketball, a few modifications are made to basic Z-scores 
-	The percentage categories are adjusted by volume. This is necessary because players who shoot more matter more; if a team has one player who goes $9$ for $9$ ($100\\%$) and another who goes $0$ for $1$ ($0\\%$) their aggregate average is $90\\%$ rather than $50\\%$. The fix is to multiply scores by the player's volume, relative to average volume
-	$\mu$ and $\sigma$ are calculated based on the $\approx 150$ players expected to be on fantasy rosters, rather than the entire NBA
  
Denoting
- Player $p$'s weekly average as $m_p$ 
- $\mu$ of $m_p$ across players expected to be on fantasy rosters as $m_\mu$
- $\sigma$ of $m_p$ across players expected to be on fantasy rosters as $m_\sigma$ 

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

The transformation looks similar for all the other categories. Adding up the results for all categories yields an aggregate Z-score, which provides an intuitive quantification of overall player value

## 2. Justifying Z-scores for Rotisserie

It is effectively impossible to calculate a truly optimal solution for Rotisserie or any other format, since they are so complex. However, if we make some simplifications, we can demonstrate that Z-scores are a reasonable heuristic

### A. Assumptions and setup

We start by simplifying the problem in a few ways
- We ignore position requirements, waiver wires, injury slots, etc. Drafters run with their drafted players the whole season
- The objective is to maximize the expected value of the number of categories won against an arbitrary opponent in a single week, where all players perform at their long-term means. Note that this translates to optimizing for overall score at the end of the season, since having higher weekly means than another team leads to victory in the category and an additional point to overall score
- Besides the player being drafted, all others are chosen randomly from a pool of top players. This assumption is obviously not exactly true. However, it is not completely crazy either, since all teams will always have some strong and some weak players chosen from a variety of positions, making them random-ish in aggregate

After these simplifications, we can pose the problem as: **if team one has $N-1$ players, randomly selected from a pool of players, and team two has $N$ players chosen randomly from the same pool, which player should the first team choose as their next player to optimize the expected value of categories won against team two, assuming all players perform at exactly their long term mean for a week**? This question is quite solvable by calculating the expected number of category wins for team one based on the statistics of the player they are choosing, then optimizing it. 

The calculation starts by analyzing the difference in category score between two teams

### B.	Category differences

The difference in category score between two teams tells us which team is winning the category and by how much. By randomly selecting the $2N -1$ random players many times, we can get a sense of what team two's score minus team one's score will be before the last player is added. See this simulation being carried out for blocks below with $N=12$

https://github.com/zer2/Fantasy-Basketball--in-progress-/assets/17816840/73c3acaa-20c9-4a61-907a-ee0de2ff7e3b

You may notice that the result looks a lot like a Bell curve even though the raw block numbers look nothing like a Bell curve. This happens because of the surprising "Central Limit Theorem", which says that when adding a bunch of random numbers together, their sum always ends up looking a lot like a Bell curve. Ergo if we ran this experiment for other categories, the results would also look like Bell curves

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

We can see that the expected number of category victories is directly proportional to the sum of the unchosen player's Z-scores. This tells us that the higher a player's total Z-score is, the better they are for Rotisserie, at least under the assumptions we have made

## 3. Modifying assumptions for Head-to-Head

Next we optimize for "Head-to-Head: Each Category." It is much simpler to analyze than the other head-to-head format, "Most Categories"

We can re-use most of the proof from the last section, except that there is one crucial difference. Where we could fairly assume that players would perform at their long-term means for the week in Rotisserie, the same assumption cannot necessarily be made for head-to-head formats. We don't know what weekly performances are going to be, so we should be sampling them in addition to randomly sampling players.

If this feels unintuitive to you, consider the following two scenarios 
- Your opponent has one of Jayson Tatum, Joel Embiid, or Luka Doncic. Tatum will score $60$, Embiid will score $70$, and Doncic will score $80$
- Your opponent has Joel Embiid. He will score either $60$, $70$, or $80$ points this week

From the perspective of trying to win a head-to-head match, these two scenarios are exactly the same! It stands to reason that if we are sampling players, we should be sampling their performances too

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

This matches with the way many fantasy players think about volatile categories like steals; they know that a technical advantage in them based on Z-scores is flimsy so they prioritize them less. Why invest strongly in steals, when you will lose the category often anyway due to bad luck? The G-score idea just converts that intuition into a mathematical rigor
  
## 5.	Head-to-head simulation results

All of our logic has relied on the simplifying assumption that other drafters are picking players randomly, which is definitely innacurate. We can't take it for granted that G-scores actually work when that assumption is removed. We can, however, simulate actual head-to-head drafts and see how G-score does against Z-score. 

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

## Addendum: Further improvement 

Any situation-agnostic value quantification system is subptimal, since a truly optimal strategy would adapt to the circumstances of the draft/auction. 

In the paper, I outline a methodology called H-scoring that dynamically chooses players based on the drafting situation. It performs significantly better than going straight off G-score and Z-score. However, it is far from perfect, particularly because it does not fully understand the consequences of punting. There is a lot of room for improvement and I hope that I, or someone else, can make a better version in the future! 

