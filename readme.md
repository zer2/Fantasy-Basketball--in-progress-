# Z-scores don’t make good rankings

Z-scores are the standard way to quantify player value for fantasy sports with category scoring. Drafters who are inexperienced or simply don’t have the time to do their own research rely on Z-score rankings to make sensible picks, and even dedicated drafters may use them as a starting point.

However, just because something is standard does not mean that it is correct. I believe that while Z-scores are a sensible heuristic, they are fundamentally flawed and far from the optimal ranking system. I wrote a paper to that effect earlier this month, which is available [here](https://arxiv.org/abs/2307.02188). Some readers may be interested in it. The code used to investigate the papers' hypotheses is included in this GitHub repository. 

I realize that the explanation included in the paper is not particularly readable, especially for those unfamiliar with the relevant mathematical concepts. Hopefully the simplified argument presented here will be easier to follow

## 1.	What are Z-scores?

Z-scores are a real concept in statistics. They are what happens to a set of numbers after subtracting the mean (average) written as $\mu$ and dividing by the standard deviation (how “spread out” the distribution is) written as $\sigma$. Mathematically, $Z(x) = \frac{x - \mu}{\sigma}$. 

This transformation is useful for number crunchers, because it takes a set of numbers that could have any scale and remakes them into a new set closely centered around zero. Intuitively, this could be helpful in the fantasy basketball context, because all categories should be equally important despite having different scales. 

For use in fantasy basketball, a few modifications are made to basic Z-scores 
-	The percentage categories are adjusted by volume. This is because players who shoot more matter more; if a team has one player who goes $9$ for $9$ (100%) and another who goes $0$ for $1$ (0%) their aggregate average is 90% rather than 50\%. The fix is to multiply scores by the player's volume, relative to average volume
-	$\mu$  and $\sigma$ are calculated based on players expected to be on fantasy rosters, rather than the entire NBA. Usually the set of top players is approximated by using Z-score calculated across the entire NBA, then Z-scores are recalculated based on $\mu$ and $\sigma$ of the top players

Now Z-scores can be formally defined for the fantasy context. With 
- $m_p$ as player $p$'s average
- $m_\mu$ as the average for a top player
- $m_\sigma$ as the standard deviation across top players

Z-scores for standard categories are  

$$
\frac{m_p - m_\mu}{m_\sigma}
$$ 

And for the percentage categories, with $a$ signifying attempts and $r$ signifying success rate, Z-scores are

$$
\frac{\frac{a_p}{a_\mu} \left(r_p - r_\mu \right)}{r_\sigma}
$$

See below for an animation of weekly blocking numbers going through the Z-score transformation step by step. First the mean is subtracted out, centering the distribution around zero, then the standard deviation is divided through to make the distribution more narrow

https://github.com/zer2/Fantasy-Basketball--in-progress-/assets/17816840/5996da7a-a877-4db1-bb63-c25bed81415f

The transformation looks similar for all the other categories.

The sum of the resulting Z-scores from every category is the aggregate Z-score, which provides an intuitive quantification of overall player value

## 2. Justifying Z-scores

As I said before, I think Z-scores are suboptimal. But there is a sense in which they do work, and before getting into their flaws, it is helpful to understand the positive case for them.

The case for Z-scores utilizes a simplifying assumption: that besides the player currently being chosen, all other players are chosen randomly from a pool of high-performing players. This assumption is obviously not exactly true, since drafters are trying to take the strongest players available, not choosing at random. But in aggregate teams probably don't look all that different from random assortments of players, and this assumption makes the math significantly more managable.

Before we can justify Z-scores, we need to lay some theoretical groundwork. You will see that once the groundwork is in place, the case for Z-scores becomes immediately apparent 

### A.	Category differences

The difference in category score between two teams is an important metric because it tells us which team is winning the category and by how much. With the help of the simplifying assumption that players are chosen randomly, we can get a sense of what the difference between two teams will be. Let's say that one team has eleven players and is trying to choose a twelfth. The second team has twelve players. Then, using real player averages, we can randomly choose players for each team many times, and see what the category difference looks like each time. See this simulation being carried out for blocks below

https://github.com/zer2/Fantasy-Basketball--in-progress-/assets/17816840/73c3acaa-20c9-4a61-907a-ee0de2ff7e3b

You may note that the result looks a lot like a Bell curve, even though the raw block numbers look nothing like a Bell curve. This happens because of one of the most amazing theorems in mathematics, the central limit theorem. The central limit theorem says that when adding a bunch of random numbers together, their average (or sum) always ends up looking a lot like a Bell curve. This means that differences for all categories will look like Bell curves, no matter how averages for the category are distributed among players 

### B.	Properties of the category difference

It is helpful to calculate the mean and standard deviation of the Bell curve from the scenario above, where team one has eleven players and team two has twelve. 

Adding all of the scores from team two and subtracting the scores from team one is the same thing as adding all of them together, except the team one scores are multiplied by $-1$. Multiplying by $-1$ switches the sign of the mean without changing the standard deviation. So effectively we are adding eleven variables with mean $-m_\mu$ and standard deviation $\sigma$, and twelve variables with mean $m_\mu$ and standard deviation $\sigma$. 

When adding random numbers together, the sum of individual means becomes the mean of the total. That makes the mean of the difference $-11 * m_\mu + 12 * m_\mu = m_\mu$.

In this case, the standard deviation of the sum is the square root of the sum of the individual standard deviations (I say "in this case" because the math is more complicated when correlations are involved). Therefore the standard deviation of the difference is $\sqrt{23 * m_\sigma^2}$ or $\sqrt{23} * m_\sigma$

### C.	Adding the unchosen player

The unchosen player has a category average of $m_p$. Incorporating them, the mean of the difference goes down by $m_p$, and nothing happens to the standard deviation, since the player’s score is known. Therefore the final difference has mean $m_\mu - m_p$ and standard deviation $\sqrt{23} * m_\sigma$

### D.	Calculating probability of victory

We have a probability distribution for the difference in score between team two and team one. We already know that whenever the value is below zero, team one will win. So if we can calculate the probability that the distribution is below zero, we will know team one's chance of winning the category.

In general, when we want to know what the probability is that a random number will be less than or equal to a particular value, we use a formula called a cumulative distribution function. $CDF(x) =$ the probability that a particular distribution will be less than $x$. We can use $CDF(0)$, then, to calculate what we want. 

The $CDF$ of the Bell curve is well known. The details of how to apply it to this case are somewhat complicated, but we can cut to the chase and give an approximate formula 

$$
\frac{1}{2}\left[ 1 + \frac{2}{\sqrt{\pi}}* \frac{- \mu }{ \sigma} \right]
$$

We've already calculated $\mu$ and $\sigma$ for the standard statistics. Substituting them in yields

$$
\frac{1}{2}\left[ 1 + \frac{2}{\sqrt{23 \pi}}* \frac{m_p – m_\mu}{m_\sigma} \right]
$$

And analagously for the percentage statistics 

$$
\frac{1}{2} \left[ 1 + \frac{2}{\sqrt{23 \pi}} * \frac{ \frac{a_p}{a_\mu} \left( r_p – r_\mu \right) }{r_\sigma}\right]
$$

Hey look those are Z-scores! Adding up all the probabilities to get the expected number of categories won, with $Z_{c,p}$ as player $p$'s Z-score for category $c$, the formula is

$$
\frac{1}{2}\left[9 + \frac{2}{\sqrt{23 \pi}} * \sum_c Z_{c,p} \right]
$$

We can see that the expected number of category victories for team one is directly proportional to the sum of the unchosen player's Z-scores. This tells us that the higher a player's total Z-score is, the better they are for fantasy, at least under the assumptions we have made. 

This seems like a compelling case for Z-scores as a heuristic. But is there any way for the logic to be improved?

## 3.The flaw of Z-scores

Sneakily, the previous section relied on the assumption that each player would score a pre-determined amount in each category. That's not the case at all in reality- even if long-term averages are well-known, performances can vary significantly from one week to the next. Randomly choosing weekly performances would have made the model more realistic. 

Below, see how standard deviation changes for blocks when randomly selecting both player and performance

https://github.com/zer2/Fantasy-Basketball--in-progress-/assets/17816840/ff8961db-d1ad-4851-8bda-bdf6b030fe97

This standard deviation is larger because it incorporates week-to-week variation. Note that it is $\sqrt{m_\sigma^2 + m_\tau^2}$ rather than $m_\sigma + m_\tau$ because of how standard deviation aggregates across multiple variables, as described in section 2B 

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

The argument for G-scores makes many assumptions, including that other drafters are picking players randomly, which is definitely not completely true even if they are using a ranking system. It would be interesting to see how G-scores do against Z-scores in a "real" competition, where the assumptions do not necessarily hold true.

The code in this repository simulates fantasy basketball with the following parameters 

- Drafts are 12-team, 13-player, total categories. So the expected win rate is 8.33%
- Teams consist of 2 C, 1 PG, 1 SG, 2 G, 1 SF, 1 PF, 2F, 3 Utility. All games played are counted
- All drafters pick the highest-ranking available player that could fit on their team, based on empirically correct rankings for the season
- Actual weekly performances are sampled for each player for each of twenty-five weeks
- The team with the best record wins (there are no playoffs)
- Strategies are tested 10,000 times at each initial drafting position

Results are shown below 

https://github.com/zer2/Fantasy-Basketball--in-progress-/assets/17816840/3e2b2acf-562f-4152-8d41-88bd57798bf1

G-scores perform way better than Z-scores in the simulation! This is evidence that the logic above makes sense, and the G-score modification really is appropriate. 

When interpreting these results, it is important to remember that they are for an idealized version of fantasy basketball. The real thing will be much more complicated due to uncertainties about long-term means for players, waiver wire moves, and more advanced strategies like punting. We can't expect the G-score to do this well in real life. 

Also, ranking systems are inherently suboptimal because they cannot adapt to the circumstances of the draft. In the paper, I outline a methodology for dynamically choosing players which performs better. It's just the tip of the iceburg though; I believe much more sophisticated algorithms could be developed to push performance even further
