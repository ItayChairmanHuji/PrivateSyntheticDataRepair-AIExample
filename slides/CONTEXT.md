# Slides 


## Details
Slides are made to present the work to other researchers. 
This file explains what should be in each slide. 

## Tech 
The slides should be generated using a react code. It should be done with slidev and/or remotion as you see fit. 

## Rules
- You must follow the content detailed in the content. 
- The slides should follow a standard of academic slides
- Slides should be properly designed 
- Slides should be compiled and ready to use 

## Content

### Title
- Title of the work: Private synthetic data repair. 
- Names: Itay Chairman, Dr. Amir Gilad, Dr. Xi He. 

### Background on me
- Background about the presentor
- Studied for a bachelor of computer engineering and physics in BIU as part of the highschool students program. 
- Focused on machine learning (a research project in RL) and Cryptography and MPC. 
- Afterwards joined the army as a backend developer and later on started working in the field of machine learning. 
- Started a master degree in computer science HUJI under the supervision of Dr. Amir Gilad
- Consider attaching an image of me

### Introduction- plan
- Introduction on synthetic data
- Introduction on denial constraints
- Do synthetic data and denial constraints work together? 

### Synthetic Data- Why do we need it? 
- Present the workflow of working with private data
- There is a data which is private 
- A synthetic data is generated using a differentially private algorithm. 
- The post processing property of DP allow us to do any analysis we wish on this synthetic data. 
- The analyst's assumption is that the synthetic data would be good enough so that algorithm applied on the synthetic data could yield results relevant to the private data. 
- Can it be guaranteed?

### Synthetic data example 
- Private data (as table): 
ID: t1, t2, t3,t4 
Edu-num: 14, 13, 14, 22
Edu: Udergrad, HS, Undergrad, Prof
Occu: Manager, Craft-repair, Farming, Prof
Income: 50,47,50,62 
Age: 52,48,25,57
Race: AA, SA, C, AA 

- Synthetic data (as table):
ID: t1, t2, t3, t4, t5, t6
Edu-num: 15, 12 ,15 ,22, 14, 16 
Edu: Undergrad, HS, Undergrad, Prof, Undergrad, Undergrad
Occu: Manager, Craft-repair, Farming, Prof, Prof, Craft-repair
Income 50, 40, 50, 60, 30, 60
Age: 55, 45, 22, 55, 50 ,50 
Race: AA, SA, C, AA, AA, AA 

### Denial Constraints
- Denial constraints are a type of integrity constraints used in database theory. 
- The idea behind them is to give a set of conditions that can not be applied all together in the same database.
- The general form of denials constraints are $\forall t_1,t_2 \lnot(\phi_1(t_1,t_2)\land \dots \phi_k(t_1,t_2))$ such that $\phi_i(t_1,t_2) \in \{t_1[A_1] o t_2[A_2], t_1[A_1] o a_1, t_2[A_2] o a_2\}$ for any $A_1,A_2$ in the attribute set of the data, operation $o\in\{=,\neq,>, <, \ge, \le\}$ and $a_1,a_2$ in the domains of the attributes. 


### Denial Constraints Example
- $\forall t_1, t_2 \lnot(t_1[Edu] = t_2[Edu]])\land t_1[Edu-num] \neq t_2[Edu-num]$
- Can also written as $Edu \rightarrow Edu-num$
- $\forall t_1, t_2 \lnot(t_1[Occu] = "prof" \land t_2[Occu] = "craft-repair"\land t_1[Income] = t_2[Income])$
- Reference the private and synthetic datasets to show satisfactions and violations of the constraints in the data. Use colors to highlight rows. Consider splitting to multiple slides to make it more readable. 

### Do synthetic data and denial constraints work together?
- In general, if we use a violation free private data to generate synthetic data, there is no guarantee that the synthetic data will not contain violations 
- In fact, research has shown several times that a lot of violations accrue when generating synthetic data. 
- We checked it ourselves on the adult dataset with PATECTGAN, AIM and MST and show millions (if not billions) of violations in the synthetic data. 

### What can we do
- Ignore the problem
- Embed the constraints in the synthetic generation process. 
- Repair the data using a classical repair process. 
- Our approach

### Ignoring the problem
- One can ignore the problem
- This approach:
1. Decreases data quality 
2. Makes the synthetic data less reliable
- In simple words: Prevents data analyst to do a proper analysis on the data and decrease the quality of the research done on the data.

### Embedding the constraints in the synthetic generation process
- Introducing: Kamino- an algorithm that does exactly that.
- Kamino is a differentially private synthetic data generation algorithm (based on a bayesian network) that accepts private data and denial constraints and generates synthetic data that satisfies the denial constraints. 
- The problems: 
1. Very computationally heavy
2. Generating a new synthetic data is not always possible. 

### Repair the data using a classical repair process
- Repairing a data is a process that takes a dataset and a set of constraints and returns a data that satisfies the constraints
- This work is focused on the classical type of repair called S-Repair (subset repair) which is a repair process that returns a subset of the data that satisfies the constraints.
- There are different types of repairs, we decided to focus on this repair process as it has the strongest theoretical foundations in comparison to other repairs, and is considered the "classical" type of repair.
- The classic s-repair aimed to minimize the number of deletions in the data. 
- The problem with this approach is that it doesn't guarantee anything about the data itself. In other words, the repaired dataset might not resemble the private data at all. 
- Give example of the optimal repair in the next slide (using the running example)

### Our approach- Plan 
- How to approach the problem
- Problem definition
- Marginals Obtaining
- Optimal solution 
- Heretical solution 
- Graphs and Numbers
- Conclusion 

### How to approach the problem
- As said, we decide to focus on the subset repair process.
- We aimed that our framework will find a balance between the number of removed tuples to the resemblance of the private data. 
- To do so, we look at some of the synthetic  data generation algorithms, and saw an interesting property they try to preserve. 
- Two way marginals were used in many synthetic generation algorithms and were proven in other research as well to be useful representing the statistical information of the data. 
- Thus our measurement to closeness to the synthetic data would be the two way marginals.

### Two way marginals example 
- Showing the two way marginals on the private and synthetic data. 

### Problem definition
- On the one hand, we wish to preserve the number of tuples in the private data so we define the loss $L_{\text{size}}=\frac{n-D_r}{n}$
- On the other hand, we wish to preserve the statistical information of the private data. 
- Suppose we have a set $\mathcal{M}$ of two way marginals, we define the loss $L_{\text{stat}} = \frac{1}{|\mathcal{M}|}\sum_{m \in \mathcal{M}|m_{D_r} - m|}$ where $m_{D_r}$ is the marginal corresponding to $m$ in the repaired data.
- Thus we define the total loss function as the weighted sum $L=\alpha * L_{\text{size}}+(1-\alpha)L_\text{stat}$

### Marginals obtaining 
- Some algorithms do give noisy private marginals as they are (for instance MST) but some don't. 
- Although marginals can be taken from the synthetic data, we present a simple mechanism to obtain marginals from the private data itself. 
- Note that this mechanism requires additional privacy budget.

### The marginals obtaining mechanism
- Use the one-shot top k mechanism to choose k marginals. 
- Add noise to the selected marginals using the Laplace/Gaussian mechanism
- Show this as algorithm format (if needed more information/formal writing I can give)

### The utility function
- The utility function can be selected by the user as he wishes according to his/her needs (for instance downstream tasks). 
- Our suggestion is a utility function that takes the worst accurate marginals estimated by the private data. 
- This approach gives us the chance to "fix" statistical mistakes done in the synthetic data generation algorithm and focus on the not well estimated parts. 

### Marginals obtaining example
- Show example on how to find the value of the utility function on the private and synthetic data from the running example

### The optimal solution
- Assuming now that we have the set of marginals, we can smartly apply the repair that minimizes the loss. 
- In other words, we aim to minimize the loss while satisfying all the denial constraints. 
- This could easily be written as an optimization problem 

### How is it done in practice
- Define a vector $x\in \{0,1\}^n$, this would represent if a tuples $t$ appears in the repaired data ($x_t=1$) or not ($x_t=0$). 
- The size of the repaired dataset would be $\sum_{i=1}^n x_i$
- In order to avoid denial constraints violations, we must enforce that for any violating pair $(i,j)$ we will satisfy $x_i+x_j <= 1$
- For marginal $m$ let $M$ be the set of tuples that are related to this marginal in the synthetic data, then the marginal in the repaired data would be $\frac{\sum_{i \in M} x_i}{\sum_{i=1}^n x_i}$. 
- So both the loss function and the constraints can be written using this binary variable. 
- Thus we will build a program that finds the $x$ that minimizes the loss function and satisfies all the denial constraints. 


### The program itself
$$
\begin{array}{ll}
\textbf{Minimize} & \alpha \cdot \frac{n - \sum_{l=1}^{n} x_l}{n} + \frac{1-\alpha}{|\mathcal{M}|} \sum_{m \in \mathcal{M}} d_m \\
\textbf{subject to:} & \\
& x_i + x_j \leq 1, \quad \forall t_i, t_j \text{ conflicting on } \sigma \\
& d_m \cdot \sum_{l} x_l \geq \sum_{l: t_l[A_i]=a_1, t_l[A_j]=a_2} x_l - P(a_1, a_2) \cdot \sum_{l} x_l, \quad \forall m \in \mathcal{M} \\
& d_m \cdot \sum_{l} x_l \geq P(a_1, a_2) \cdot \sum_{l} x_l - \sum_{l: t_l[A_i]=a_1, t_l[A_j]=a_2} x_l, \quad \forall m \in \mathcal{M} \\
& d_m \geq 0, \quad \forall m \in \mathcal{M} \\
& x_l \in \{0,1\}, \quad \forall l \in [1,n]
\end{array}
$$


### Pros and Cons
- Pros:
    - We get the best solution possible to solve the problem. 
    - Transforms the problem to a widely supported framework that keeps developing with time. 
- Cons:
    - An NP-hard problem. Can take a lot time and resources to solve. 
    - The solution is stricter, so a smart choice of $\alpha$ is need. 


### The heuristic
- Another way to look at the problem is via a "conflict graph" 
- Let each tuple in the data be a vertex and each violation be an edge. 
- Show example with the running example

### What is the repair then? 
- We want to remove vertices from the graph so that no edges would remain. 
- In other words, we can say that we wish to choose a set of vertices such that each edge in the graph touches at list of the vertices we chose. 
- This is just a vertex cover!

### Adjusting to our case 
- In the classical vertex cover problem, we have aimed to reach the minimal cover of the graph, which in our case would correspond to the repair with the minimal deletions. 
- Now we don't want to delete the minimal number of vertices, but minimize the loss function
- So we would work with the (dynamic) weighted vertex cover problem instead. 
- In this problem we would define a weight function for each vertex and our goal would be to minimize the weight of the cover. 
- Our case would be a bit different because the weight would change with time as well. 

### The weight function 
- The weight of a vertex $v$ would be the the marginals distance between the expected marginals and the actual marginals assuming the tuples corresponds to $v$ was removed from the data
- Normalization: Let $w_1,\dots,w_n$ be the weights of the vertices, then the normalized weight of tuple $i$ would be $\frac{w_i - \min\{w_1,\dots,w_n\} + \varepsilon}{\max\{w_1,\dots,w_n\} - \min\{w_1,\dots,w_n\} + \varepsilon}$ 
- Show example with running example. 


### The algorithm
1. Build the conflict graph and init an empty cover $C$ 
2. While there are still edges
    1. Calculate the weight of each vertex and normalize it. 
    2. Calculate the degree of each vertex and normalize it. 
    3. Find the vertex with the smallest weight/degree ratio 
    4. Add the vertex to the cover 
    5. Remove the vertex from the graph + the resulted isolated vertices. 
3. Return $D \setminus C$


### Numbers and graphs: 
- When I'll have graphs I'll add it. 

### Conclusion
- The framework presents the idea of repairing a synthetic data to fix denial constraints violations while considering statistical information. 
- The experimental data shows the tradeoffs between the approaches to repair the data. 

### What is so special about this framework 
- This framework does not present only a solution, but a change of perspective as well.
- Up until now, we kept looking for the best synthetic data, this framework shows another way. 
- Here, we assume that there is no such "perfect data" or it might be very difficult to generate it. 
- Instead we show that it's possible to take a well generated synthetic data and repair it to suit our requirements.

### Thank you so much for listening :) 