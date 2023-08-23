# Z-scores don’t make good rankings

Every fantasy basketball dabbler has come across Z-scores at some point. They are cornerstones of how player value is quantified across categories, allowing for the creation of objective ranking lists based on actual performance. Drafters who are inexperienced or simply don’t have the time to do their own research rely on these rankings to make sensible picks, and even dedicated drafters may use them as a starting point.

One would expect that such a widely used metric has a strong theoretical foundation- I certainly did when I first started looking into fantasy basketball rankings. But the reality is that there is not much to support Z-scores besides intuition and years of orthodoxy. 

I believe that while Z-scores are a sensible heuristic, they are fundamentally flawed and far from the optimal ranking system. I wrote a paper to that effect earlier this month, which is available [here](https://arxiv.org/abs/2307.02188). Some readers may be interested in it. The code used to investigate the papers' hypotheses is included in this GitHub repository. 

I realize that the explanation included in the paper is not particularly readable, especially for those unfamiliar with the relevant mathematical concepts. Hopefully this readme will provide a more readable explanation.

## 1.	What are Z-scores?

Z-scores are a real concept in statistics. They are what happens to a distribution after subtracting the mean (average) written as $\mu$ and dividing by the standard deviation (how “spread out” the distribution is) written as $\sigma$. Mathematically, $Z(x) = \frac{x - \mu}{\sigma}$. So if a set of numbers has an average of $10$ and a standard deviation of $5$, $Z(20) = \frac{20-10}{5} = 2$

This transformation is useful for number crunchers, because it takes a set of numbers that could have any scale and remakes them into a new set with $\mu = 0$ and $\sigma =1$. Intuitively, this could be helpful in the fantasy basketball context, because all categories should be equally important despite having different scales. 

For use in fantasy basketball, a few modifications are made to basic Z-scores 
-	Z-scores should not be calculated using statistics from all NBA players, because most NBA players will never sniff fantasy teams and should be irrelevant. One common fix is to first score players by basic Z-score, then use the top players to re-calculate means and standard deviations. Players are then re-ranked with the updated means and standard deviations
-	Another fix is needed for free throw percent and field goal percent. Players who shoot more attempts matter more for these categories, so impact is scaled by number of attempts before the Z-score transformation

I define $m_p$ as player $p$'s average, with $m_\mu$ and $m_\sigma$ as $\mu$ and $\sigma$ over the set of high-performing players. Z-scores for standard categories are then 

$$
\frac{m_p - m_\mu}{m_\sigma}
$$ 

See below for an animation of what weekly blocking numbers look like after the Z-score transformation

https://github.com/zer2/Fantasy-Basketball--in-progress-/assets/17816840/b0af1525-d2ed-4149-a14a-274c262df643

And for the percentage categories, with $a$ signifying attempts and $r$ signifying success rate,

$$
\frac{\frac{a_p}{a_\mu} \left(r_p - r_\mu \right)}{r_\sigma}
$$

The aggregate Z-score is the sum of Z-scores across all categories. Ordering all players by aggregate Z-score then produces an intuitively sensible ranking list.    

## 2. Justifying Z-scores

As I said before, I think Z-scores are suboptimal. But there is a sense in which they do make sense, and before getting into their flaws, it is helpful to understand the positive case for them.  


### A.	Category differentials

An important quantity of interest is the difference in category score, e.g. blocks, between two teams. The sign of the difference will determine the winner. 

Distributions per player can be transformed into category differentials under the assumption that players are chosen randomly. One might expect this to be complicated because all the distributions look a little different from each other. Blocks for example have an unusual “long tail,” with many of the league’s blocks come from a small number of elite shot-blockers. One might be concerned that the total blocking numbers for a team may look different than say, the number of points. 

Fortunately, all of the categories will look similar in aggregate because of one of the most amazing theorems in mathematics, the central limit theorem. The central limit theorem says that when adding a bunch of random numbers together, their average (or sum) ends up looking a lot like a bell curve, even if the sampled distribution was not a bell curve. To demonstrate, see the below animation on the differential between two teams’ numbers of blocks. One team has twelve players and the other has eleven, with one player still to be chosen. 

https://github.com/zer2/Fantasy-Basketball--in-progress-/assets/17816840/9a07ba69-d284-491a-bfe4-57deec31c12a

The blocking data didn’t look like a bell curve at all, but the difference in blocks across full teams does. This will apply to all categories. 

### B.	Writing a formula for the category differential

Bell curves are defined by two numbers, mean and variance (standard deviation squared). In other words, all you need to know about a bell curve is its mean and variance, and then you can calculate everything else about it. 

It is easy to find the mean and variance of the category differentials thanks to a nice property that both numbers share. They are additive across multiple variables; that is to say, the mean of a sum is the sum of the means and the variance of a sum is the sum of the variances (technically this isn’t always true because of correlations, but we don’t need to get into that). Note that when subtracting a number its mean is subtracted instead of added.

Let’s return to the example where one team has eleven players and the other has twelve. The average differential is team two’s average score minus team one’s average score, which is just $m_\mu$ ($1.78$). Variances are additive so total variance is $23 * m_\sigma^2$, or standard deviation is $\sqrt{23 * m_\sigma^2}$ ($6.80$). This lines up with empirically calculated values from the simulation run above ($1.44$ and $6.66$). 

### C.	Adding a new player

Our theoretical scenario has unbalanced teams for a reason. One last player needs to be picked, and we can see how winning chances are affected by that choice.  

Let’s say that the unchosen player has a blocking average of $m_p$. The mean of the differential goes down by $m_p$, and nothing happens to the variance, since the player’s score is known. Therefore the normal approximation of the differential has mean $m_\mu - m_p$ and variance $23 * m_\sigma^2$. 

### D.	Calculating probability of victory

Mathematically, this is the trickiest part. 

We have a probability distribution for the difference in score between team two and team one. We already know that whenever the value is below zero, team one will win. So we need to know what percent of the distribution is below zero.

In general, when we want to know what the probability is that a random number will be less than or equal to a particular value, we use a formula called a cumulative distribution function. $CDF(x) =$ the probability that a particular distribution will be less than $x$. We can use $CDF(0)$, then, to calculate what we want. 

The $CDF$ of the normal distribution is well known. The details of how to apply it to this case are somewhat complicated, but we can cut to the chase and give an approximate formula for the standard statistics

$$
\frac{1}{2}\left[ 1 + \frac{2}{\sqrt{23 \pi}}* \frac{m_p – m_\mu}{m_\sigma} \right]
$$

The math of why it works is even more complicated, but the percentage statics can be treated the same way. Chance of winning is

$$
\frac{1}{2} \left[ 1 + \frac{2}{\sqrt{23 \pi}} * \frac{ \frac{a_p}{a_\mu} \left( r_p – r_\mu \right) }{r_\sigma}\right]
$$

Hey look those are Z-scores! Adding up all the probabilities to get the expected number of categories won, the formula is

$$
\frac{1}{2}\left[9 + \frac{2}{\sqrt{23 \pi}} * \sum_c Z_c \right]
$$

We can see that the expected number of category victories is directly proportional to the sum of Z-scores. For the 'Each category' and 'Rotisserie' formats, this is generally what drafters are trying to optimize for, so there is a compelling case to use Z-scores for those formats. The 'Most Categories' format is more complicated, but it still seems reasonable to use Z-score as a heuristic for it. 

So what's the problem?
    
## 3.The flaw of Z-scores

As elegant as Z-scores are, they are not perfect. 

Astute readers may have noticed a problematic assumption underlying the proof presented in the last section. All performance values were known from the get-go, which is not the case in practice. Even if long-term means are known, performances can vary significantly from one week to the next. 

To see why this is a problem consider a hypothetical category for which all players average between -1 and 1, but actual values differ from -1,000 to +1,000 from week to week. It is intuitively obvious that this category would be not important to draft for. You could draft a bunch of +1 average players, but no matter how many you got, the result of the category would still be essentially a coin flip.     

Real basketball statistics can be kind of like this too. Steals, for instance, are notoriously volatile, and have much more week-to-week variance than player-to-player variance. Even if you draft well for steals, you have a good chance of losing the category often due to bad luck. 

Fixing this requires modifying variance to account for week-to-week changes. Mathematically, typical week-to-week variance is added to the existing player-to-player variance. See below what this looks like for blocks

https://github.com/zer2/Fantasy-Basketball--in-progress-/assets/17816840/ff8961db-d1ad-4851-8bda-bdf6b030fe97

## 4.	Reformulating Z-scores 

The key mistake was that we sampled player means to get the distributions for team totals. Instead of player means, we should have sampled player performances. Updating variance to be for player performances instead of means yields a new formula

$$
\frac{m_p – m_\mu}{\sqrt{m_\sigma^2 + m_\tau^2}} 
$$

Or, for the percentage statistics, 

$$
\frac{\frac{a_p}{a_\mu} \left( r_p – r_\mu \right) }{\sqrt{r_\sigma^2 + r_\tau^2}} 
$$

I call these G-scores.

## 5.	Simulation results

This analysis would suggest that G-scores are more appropriate as a one-stop shop ranking system. But we’re using some crucial assumptions- in particular, we are assuming that other drafters are picking players randomly, which is definitely not true even if they are using a ranking system. It would be interesting to see how G-scores did against Z-scores in a real competition, where the assumptions do not necessarily hold true.

The code in this repository performs this simulation with the following parameters 

- Drafts are 12-team, 13-player, total categories. So the expected win rate is 8.33%
- Teams consist of 2 C, 1 PG, 1 SG, 2 G, 1 SF, 1 PF, 2F, 3 Utility. All games played are counted
- All drafters pick the highest-ranking available player that could fit on their team
- Actual weekly performances are sampled for each player for each week
- Strategies are tested 10,000 times at each seat

https://github.com/zer2/Fantasy-Basketball--in-progress-/assets/17816840/3e2b2acf-562f-4152-8d41-88bd57798bf1

G-score performed way better than Z-score in the simulation!

When interpreting these results, it is important to remember that they are for an idealized version of fantasy basketball. The real thing will be much more complicated due to uncertainties about long-term means for players, waiver wire moves, and more advanced strategies like punting. We can't expect the G-score to do this well in real life. 

Also, ranking systems are inherently suboptimal because they cannot adapt to the circumstances of the draft. In the paper, I outline a methodology for dynamically choosing players which performs better. It's just the tip of the iceburg though; I believe much more sophisticated algorithms could be developed to push performance even further. 
