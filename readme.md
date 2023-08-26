# Z-scores don’t make good rankings

Every fantasy basketball dabbler has come across Z-scores at some point. They are cornerstones of how player value is quantified across categories, allowing for the creation of objective ranking lists based on actual performance. Drafters who are inexperienced or simply don’t have the time to do their own research rely on these rankings to make sensible picks, and even dedicated drafters may use them as a starting point.

One would expect that such a widely used metric has a strong theoretical foundation- I certainly did when I first started looking into fantasy basketball rankings. But the reality is that there is not much to support Z-scores besides intuition and years of orthodoxy. 

I believe that while Z-scores are a sensible heuristic, they are fundamentally flawed and far from the optimal ranking system. I wrote a paper to that effect earlier this month, which is available [here](https://arxiv.org/abs/2307.02188). Some readers may be interested in it. The code used to investigate the papers' hypotheses is included in this GitHub repository. 

I realize that the explanation included in the paper is not particularly readable, especially for those unfamiliar with the relevant mathematical concepts. Hopefully the simplified argument presented here will be easier to follow

## 1.	What are Z-scores?

Z-scores are a real concept in statistics. They are what happens to a set of numbers after subtracting the mean (average) written as $\mu$ and dividing by the standard deviation (how “spread out” the distribution is) written as $\sigma$. Mathematically, $Z(x) = \frac{x - \mu}{\sigma}$. So if a set of numbers has an average of $10$ and a standard deviation of $5$, $Z(20) = \frac{20-10}{5} = 2$

This transformation is useful for number crunchers, because it takes a set of numbers that could have any scale and remakes them into a new set with $\mu = 0$ and $\sigma =1$. Intuitively, this could be helpful in the fantasy basketball context, because all categories should be equally important despite having different scales. 

For use in fantasy basketball, a few modifications are made to basic Z-scores 
-	Z-scores should not be calculated using statistics from all NBA players, because most NBA players will never sniff fantasy teams and should be irrelevant. One common fix is to first score players by basic Z-score, then use the top players to re-calculate means and standard deviations. Players are then re-ranked with the updated means and standard deviations
-	Another fix is needed for free throw percent and field goal percent. If a team has one player who goes $9$ for $9$ and another who goes $0$ for $1$ the aggregate average is $90$ percent, closer to $100\%$ than $0\%$. Clearly players who shoot more attempts matter more for these categories, so percentages are scaled by number of attempts vs. the average before the Z-score transformation

I define $m_p$ as player $p$'s average, with $m_\mu$ and $m_\sigma$ as $\mu$ and $\sigma$ over the set of high-performing players. Z-scores for standard categories are then 

$$
\frac{m_p - m_\mu}{m_\sigma}
$$ 

See below for an animation of what weekly blocking numbers look like after the Z-score transformation

https://github.com/zer2/Fantasy-Basketball--in-progress-/assets/17816840/f20be45a-3600-4630-a224-3b07ce40a0dd

And for the percentage categories, with $a$ signifying attempts and $r$ signifying success rate,

$$
\frac{\frac{a_p}{a_\mu} \left(r_p - r_\mu \right)}{r_\sigma}
$$

The aggregate Z-score is the sum of Z-scores across all categories. Ordering all players by aggregate Z-score then produces an intuitively sensible ranking list. 

## 2. Justifying Z-scores

As I said before, I think Z-scores are suboptimal. But there is a sense in which they do work, and before getting into their flaws, it is helpful to understand the positive case for them

### A.	Category differences

The case for Z-scores starts with the exploration of an important quantity; the difference in category score between two teams. The sign of the difference will determine the winner. 

Distributions per player can be transformed into category differences under the assumption that players are chosen randomly. One might expect this to be complicated because all the distributions look a little different from each other. Blocks for example have an unusual “long tail,” with many of the league’s blocks come from a small number of elite shot-blockers. One might be concerned that the total blocking numbers for a team may look different than say, the number of points. 

Fortunately, all of the categories will look similar in aggregate because of one of the most amazing theorems in mathematics, the central limit theorem. The central limit theorem says that when adding a bunch of random numbers together, their average (or sum) ends up looking a lot like a Bell curve, even if the sampled distribution was not a Bell curve. To demonstrate, see the below animation on the difference between two teams’ numbers of blocks. One team has eleven players and the other has twelve, ignoring the unchosen player for the time being 

https://github.com/zer2/Fantasy-Basketball--in-progress-/assets/17816840/73c3acaa-20c9-4a61-907a-ee0de2ff7e3b

The blocking data doesn't look like a Bell curve at all, but the difference in blocks across full teams does

### B.	Properties of the category difference

It is helpful to calculate the mean and standard deviation of the Bell curve from the example above, where one team has eleven players and another has twelve, with one player yet to be picked. 

When adding numbers together, the sum of individual means becomes the overall mean. When some of those numbers are subtracted instead, their means are subtracted from the total mean rather than added. That makes the overall mean of the difference $12 * m_\mu - 11 * m_\mu = m_\mu$.

In this case, the standard deviation of the sum is the square root of the sum of the individual standard deviations (be careful- this isn't always true when correlations are involved). Therefore the standard deviation of the difference is $\sqrt{23 * m_\sigma^2}$

### C.	Adding the unchosen player

The unchosen player has a category average of $m_p$. Incorporating them, the mean of the difference goes down by $m_p$, and nothing happens to the standard deviation, since the player’s score is known. Therefore the final difference has mean $m_\mu - m_p$ and standard deviation $\sqrt{23 * m_\sigma^2}$

### D.	Calculating probability of victory

Mathematically, this is the trickiest part. 

We have a probability distribution for the difference in score between team two and team one. We already know that whenever the value is below zero, team one will win. So if we can calculate the probability that the distribution is below zero, we will know team one's chance of winning the category.

In general, when we want to know what the probability is that a random number will be less than or equal to a particular value, we use a formula called a cumulative distribution function. $CDF(x) =$ the probability that a particular distribution will be less than $x$. We can use $CDF(0)$, then, to calculate what we want. 

The $CDF$ of the Bell curve is well known. The details of how to apply it to this case are somewhat complicated, but we can cut to the chase and give an approximate formula for the standard statistics

$$
\frac{1}{2}\left[ 1 + \frac{2}{\sqrt{23 \pi}}* \frac{m_p – m_\mu}{m_\sigma} \right]
$$

And for the percentage statistics 

$$
\frac{1}{2} \left[ 1 + \frac{2}{\sqrt{23 \pi}} * \frac{ \frac{a_p}{a_\mu} \left( r_p – r_\mu \right) }{r_\sigma}\right]
$$

Hey look those are Z-scores! Adding up all the probabilities to get the expected number of categories won, the formula is

$$
\frac{1}{2}\left[9 + \frac{2}{\sqrt{23 \pi}} * \sum_c Z_c \right]
$$

We can see that the expected number of category victories is directly proportional to the sum of Z-scores. In other words, the higher a player's total Z-score is, the better they are for fantasy. 

This seems like a compelling case for Z-scores as a heuristic. What's my problem with them, then?

## 3.The flaw of Z-scores

Sneakily, the previous section relied on the assumption that each player would score a pre-determined amount in each category. That's not the case at all in reality- even if long-term averages are well-known, performances can vary significantly from one week to the next. In addition to randomly choosing other players, we also should have randomly chosen how they would perform for the week.

This does not change $\mu$ but it does change $\sigma$ because it adds another source of variance. Mathematically, typical week-to-week variance is added to the existing player-to-player variance. 

See below what this looks like for blocks

https://github.com/zer2/Fantasy-Basketball--in-progress-/assets/17816840/ff8961db-d1ad-4851-8bda-bdf6b030fe97

Note that the new standard deviation is $\sqrt{m_\sigma^2 + m_\tau^2}$ rather than $m_\sigma + m_\tau$ because of how standard deviation aggregates across multiple variables, as described in section 2B 

## 4.	Reformulating Z-scores 

All the same arguments we made before still work, except that we need to replace the standard deviation values. This changes standard Z-scores to 

$$
\frac{m_p – m_\mu}{\sqrt{m_\sigma^2 + m_\tau^2}} 
$$

And, for the percentage statistics, 

$$
\frac{\frac{a_p}{a_\mu} \left( r_p – r_\mu \right) }{\sqrt{r_\sigma^2 + r_\tau^2}} 
$$

I call these G-scores, and it turns out that these are quite different from Z-scores. For example, steals have a very high week-to-week variance, and carry less weight in G-scores than Z-scores as a result. 

This matches with the way many fantasy players think about volatile categories like steals; they know that a technical advantage in them based on Z-scores is flimsy so they prioritize them less. The G-score idea just converts that intuition into a mathematical rigor

## 5.	Simulation results

The argument for G-scores makes many assumptions, including that other drafters are picking players randomly, which is definitely not completely true even if they are using a ranking system. It would be interesting to see how G-scores did against Z-scores in a real competition, where the assumptions do not necessarily hold true.

The code in this repository performs this simulation with the following parameters 

- Drafts are 12-team, 13-player, total categories. So the expected win rate is 8.33%
- Teams consist of 2 C, 1 PG, 1 SG, 2 G, 1 SF, 1 PF, 2F, 3 Utility. All games played are counted
- All drafters pick the highest-ranking available player that could fit on their team
- Actual weekly performances are sampled for each player for each week
- Strategies are tested 10,000 times at each seat

The results are, in my opinion, very interesting 

https://github.com/zer2/Fantasy-Basketball--in-progress-/assets/17816840/3e2b2acf-562f-4152-8d41-88bd57798bf1

G-scores perform way better than Z-scores in the simulation! This is great evidence that our logic made sense, and the G-score modification really is appropriate. 

When interpreting these results, it is important to remember that they are for an idealized version of fantasy basketball. The real thing will be much more complicated due to uncertainties about long-term means for players, waiver wire moves, and more advanced strategies like punting. We can't expect the G-score to do this well in real life. 

Also, ranking systems are inherently suboptimal because they cannot adapt to the circumstances of the draft. In the paper, I outline a methodology for dynamically choosing players which performs better. It's just the tip of the iceburg though; I believe much more sophisticated algorithms could be developed to push performance even further
