# Z-scores don’t make good rankings

Every fantasy basketball dabbler has come across Z-scores at some point. They are cornerstones of how player value is quantified across categories, allowing for the creation of objective ranking lists based on actual performance. Drafters who are inexperienced or simply don’t have the time to do their own research rely on these rankings to make sensible picks, and even dedicated drafters may use them as a starting point.

One might expect that such a widely used metric has a strong theoretical foundation. I certainly did when I first started looking into fantasy basketball rankings. But the reality is that there is not much to support Z-scores besides intuition and years of orthodoxy. 

I believe that while Z-scores are a sensible heuristic, they are fundamentally flawed and far from the optimal ranking system. I wrote a paper to that effect earlier this month, which is available [here](https://arxiv.org/abs/2307.02188). Mathematically inclined readers may be interested in it. The code used to run the simulations that validate the hypothesis are included in this GitHub repository. 

I realize that the explanation included in the paper is not particularly readable, especially for those with little background in mathematics. Hopefully this readme will provide a more readable explanation.

## 1.	What are Z-scores?

Z-scores are a real concept in statistics. They are what happens to a distribution after subtracting the mean (average) and dividing by the standard deviation (how “spread out” the distribution is). Mathematically, $\frac{x - \mu}{\sigma}$. So if a set of numbers has an average of 10 and a standard deviation of 5, $Z(20) = \frac{20-10}{5} = 2$

This transformation is useful for number crunchers, because it takes a set of numbers that could have any scale and remakes them into a new set centered closely around zero. Z-transformed statistics have predictable properties and are similar to each other, which is helpful in many contexts. Intuitively, fantasy sports could be one of those contexts, because all metrics should be equally important despite having different scales. 

For use in fantasy basketball, a few modifications are made to basic Z-scores 
-	Z-scores should not be calculated using statistics from all NBA players, because most NBA players will never sniff fantasy teams and should be irrelevant. One common fix is to first score players by basic Z-score, then use the top players to re-calculate means and standard deviations. Players are then re-ranked with the updated means and standard deviations. 
-	Another fix is needed for free throw percent and field goal percent. Players who shoot more attempts matter more for these categories, so impact is scaled by number of attempts before the Z-score transformation. 

After modifications, we have a sensible strategy for scoring players. See below for an animation of what weekly blocking numbers look like after the Z-score transformation




```python
#hide

from IPython.display import Video

Video("visualizations/BlockVis.mp4", height = 550, width = 900)
```




<video src="visualizations/BlockVis.mp4" controls  width="900"  height="550">
      Your browser does not support the <code>video</code> element.
    </video>



## 2. Justifying Z-scores

As I said before, I think Z-scores are suboptimal. But there is a sense in which they do make sense, and before getting into their flaws, it is helpful to understand the positive case for them.  


### A.	Category differentials

An important quantity of interest is the difference in category score, e.g. blocks, between two teams. The sign of the difference will determine the winner. 

Distributions per player can be transformed into category differentials under the assumption that players are chosen randomly. One might except this to be complicated because all the distributions look a little different from each other. Blocks for example have an unusual “long tail,” with many of the league’s blocks come from a small number of elite shot-blockers. One might be concerned that the total blocking numbers for a team may look different than say, the number of points. 

Fortunately, all of the categories will look similar in aggregate because of one of the most amazing theorems in mathematics, the central limit theorem. The central limit theorem says that when adding a bunch of random numbers together, their average (or sum) ends up looking a lot like a bell curve, even if the sampled distribution was not a bell curve. To demonstrate, see the below animation on the differential between two teams’ numbers of blocks, where one team has twelve players and the other has eleven


```python
#hide

from IPython.display import Video

Video("visualizations/SimulationVis.mp4", height = 550, width = 900)
```




<video src="visualizations/SimulationVis.mp4" controls  width="900"  height="550">
      Your browser does not support the <code>video</code> element.
    </video>



The blocking data didn’t look like a bell curve at all, but the difference in blocks across full teams does. This will apply to all categories. 

### B.	Writing a formula for the category differential

Bell curves are defined by two numbers, mean and variance (standard deviation squared). In other words, all you need to know about a bell curve is its mean and variance, and then you can calculate everything else about it. 

It is easy to find the mean and variance of the category differentials thanks to a nice property that both numbers share. They are additive across multiple variables; that is to say, the mean of a sum is the sum of the means and the variance of a sum is the sum of the variances (technically this isn’t always true because of correlations, but we don’t need to get into that). Note that when subtracting a number its mean is subtracted instead of added.

Let’s return to the example where one team has eleven players and the other has twelve. The average differential is team two’s average score minus team one’s average score, which is just one times the mean of the distribution (1.78). Variances are additive so total variance is 23 times the variance, or standard deviation is square root of 23 times the standard deviation squared (6.80). This lines up with empirically calculated values (1.44 and 6.66). 

### C.	Adding a new player

Our previous examples had unbalanced teams for a reason. One last player needs to be picked, and we can see how winning chances are affected by that choice.  

Let’s say that the unchosen player has a blocking average of $m_u$. The differential goes down by $m_u$, and nothing happens to the variance, since the player’s score is known. This gives us a formula for the category distribution totals:  

### D.	Calculating probability of victory

Mathematically, this is the trickiest part. 

We have a probability distribution for the difference in score between team two and team one. We already know that whenever the value is below zero, team one will win. So we need to know what percent of the distribution is below zero

In general, when we want to know what the probability is that a random number will be less than or equal to a particular value, we use a formula called a cumulative distribution function. CDF(x) = the probability that a particular distribution will be less than x. We can use CDF(0), then, to calculate what we want. 

The CDF of the normal distribution is well known. The details of how to apply it to this case are somewhat complicated, but we can cut to the chase and give an approximate formula for the counting statistics

$$
\frac{1}{2}\left[ 1 + \frac{2}{\sqrt{\pi}}* \frac{m_p – m_\mu}{m_\sigma} \right]
$$

The math of why it works is complicated, but the percentage statics can be treated the same way. Chance of winning is

$$
\frac{1}{2} \left[ 1 + \frac{2}{\sqrt{\pi}} * \frac{ \frac{a_p}{a_\mu} \left( r_p – r_\mu \right) }{r_\sigma}\right]
$$

Hey look those are Z-scores! When we add up all the probabilities, we get 

$$
\frac{1}{2}\left[1 + \frac{2}{\sqrt{\pi}} * \sum_c Z_c \right]
$$

We can see that the expected number of victories is directly proportional to the sum of Z-scores. So Z-scores do make sense!
Or do they?
    
## 3.The flaw of Z-scores

Astute readers may have noticed a problematic assumption underlying the proof presented in the last section. All performance values were known from the get-go, which is not the case in practice. This increases variance by the average variability of the statistic week-to-week. E.g. for blocks


```python
#hide

from IPython.display import Video

Video("visualizations/NewVariabilityVis.mp4", height = 550, width = 900)
```




<video src="visualizations/NewVariabilityVis.mp4" controls  width="900"  height="550">
      Your browser does not support the <code>video</code> element.
    </video>



To see why this is a problem consider a hypothetical category for which all players average between -1 and 1, but actual values differ from -1,000 to +1,000 from week to week. It is intuitively obvious that this category would be not important to draft for. You could draft a bunch of +1 average players, but no matter how many you got, the result of the category would still be essentially a coin flip.     

Real basketball statistics can be kind of like this too. Steals, for instance, are notoriously volatile, and have much more week-to-week variance than player-to-player variance. Even if you draft well for steals, you have a good chance of losing the category often due to bad luck. 


## 4.	Reformulating Z-scores 

The key mistake was that we added up player means to get the distributions for team totals. Instead of player means, we should have added up player performances. Replacing variance with the new formula yields

$$
\frac{m_p – m_\mu}{\sqrt{m_\sigma^2 + m_\tau^2}} 
$$

Or, for the percentage statistics, 

$$
\frac{\frac{a_p}{a_\mu} \left( r_p – r_\mu \right) }{\sqrt{r_\sigma^2 + r_\tau^2}} 
$$


## 5.	Simulation results

This analysis would suggest that G-scores are more appropriate as a one-stop shop ranking system. But we’re using some crucial assumptions- in particular, we are assuming that other drafters are picking players randomly, which is definitely not true even if they are using a ranking system. It would be interesting to see how G-scores did against Z-scores in a real competition, where the assumptions do not necessarily hold true

The code in this repository performs this simulation with the following parameters 

- Drafts were 12-team, 13-player, total categories. So the expected win rate is 8.33%
- Teams consisted of 2 C, 1 PG, 1 SG, 2 G, 1 SF, 1 PF, 2F, 3 Utility. All games played were counted
- All drafters picked the highest-ranking available player that could fit on their team
- Actual weekly performances were sampled for each player for each week
- Strategies were tested 10,000 times at each seat



```python
#hide

from IPython.display import Video

Video("visualizations/SImResultsVis.mp4", height = 550, width = 900)
```




<video src="visualizations/SImResultsVis.mp4" controls  width="900"  height="550">
      Your browser does not support the <code>video</code> element.
    </video>



G-score performed way better than Z-score in the simulation!

When interpreting these results, it is important to remember that they are for an idealized version of fantasy basketball. The real thing will be much more complicated due to uncertainties about long-term means for players, waiver wire moves, and more advanced strategies like punting. We can't expect the G-score to do this well in real life. 
