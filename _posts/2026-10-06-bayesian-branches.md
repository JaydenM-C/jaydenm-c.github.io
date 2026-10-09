---
title: 'Bayesian Branches'
subtitle: 'An introduction to phylogenetic tree inference'
date: 2026-10-06
permalink: /posts/2026/10/bayesian-branches/
excerpt: "If you've ever wondered where baby trees come from..."
tags:
  - phylogenetics
  - linguistics
  - computational methods
---

As a parting gift on my final day at the Surrey Morphology Group, before my big move to the University of Zurich, I delivered an 'Expertise Session' on phylogenetic tree inference. This is a kind of skills/knowledge-sharing workshop talk, with half an hour for presentation and half an hour for discussion and questions. Evolutionary thinking is increasingly familiar in the SMG lab. We recently had a reading group on _The Philosophy of Evolutionary Theory_ by Elliott Sober (which covers evolutionary concepts like selection and drift, but not tree inference itself) and people have been generally exposed to phylogenetic comparative methods in quantitative typology (which relies on a pre-existing reference phylogeny). But this led to the very reasonable question: where do the trees come from in the first place? What is the actual tree inference process? What are the data? What are the models?

So, I was given the daunting task of explaining phylogenetic tree inference in linguistics in, uh, 30 minutes..! Although it would take multiple sessions, even a full semester course, to do the subject proper justice, it was still a useful exercise. Most of my post-PhD work has been in the PCMs/typology realm, so it's actually been a while since I thought too much about the OG task of inferring trees and it was good to revisit it and get my head around it again.

I'm sharing my slides here, with some bonus notes, mainly for the benefit of the session's attendees. But of course, if anyone else finds it useful, all the merrier! Due to the time constraints, I aimed to keep it fairly high level, and also leaning more conceptual, less hands-on. The aim is not so much a tutorial to guide people through the process of inferring their first tree in BEAST. Rather, I'd like people to walk away with a more intuitive sense of what a phylogenetic tree figure in a linguistics paper represents (and what it doesn't represent), and perhaps a little less afraid to read (and critique) the methodological jargon in a phylogenetics paper. And, I wanted to help people avoid some common misconceptions.

One thing that did lighten my task a little: This was actually the second part in a super-mega-two-parter Expertise Session. The first half was called _Bayesian Bayesics_, an introduction to Bayesian statistics, by my fellow Bayes Bros [Maria Copot](https://copotm.github.io) and [Cerys Hughes](https://ceryshughes.github.io). We had a discussion earlier in the week about whether "Bayes bro" was complimentary or derogatory – to be clear, in the case of these two it is definitely the former, and I am honoured to be part of their brethren.

So, without further ado, the slides.

<object data="/files/pdf/Intro_to_tree_inference-handout-sml.pdf#view=FitH"
        type="application/pdf"
        style="width:100%; aspect-ratio:16/9; border:1px solid #ddd;">
  <p>Your browser can't show the slides inline. <a href="/files/pdf/Intro_to_tree_inference-handout-sml.pdf">Download them here</a>.</p>
</object>

<p><a href="/files/pdf/Intro_to_tree_inference-handout-sml.pdf">Download the slides (PDF)</a></p>

### The model menu

Slide 15 lists the kinds of priors that go into a Bayesian phylogenetic model. But we didn't go into detail about what options a linguist might actually select for those priors. There are three main ingredients you'll need to choose.

**1. Transition models (how characters change)**

  - **Binary CTMC** (continuous time Markov chain): Essentially the gain/loss model on slide 12. There's a rate at which characters are gained (0→1) and a rate at which they're lost (1→0). These rates are estimated from the data.
  - **Stochastic Dollo** (Nicholls & Gray 2008): Each character is born exactly once, and can be lost many times. This suits lexical data, because it's essentially impossible for the same cognate to be independently innovated more than once. (Though note that, in practice, chance resemblances and undetected borrowings could look like multiple parallel innovations.)
  - **Covarion**: A character can switch between "fast" and "slow" (or even frozen) rates over time. Captures the intuition that cognates can be relatively stable for centuries and then suddenly enter a period of volatility. Unlike stochastic Dollo, covarion allows for cognates to be innovated multiple times – this isn't particularly ecologically valid for a linguistic cognate, but in practice it can have the effect of absorbing some noise from undetected chance resemblances and borrowings (which can look like multiple innovations in a tree).

There's just one problem. Fitting a single transition model to the entire lexicon presupposes that all cognates evolve in more or less the same way. In fact, as linguists, we have a strong intuition that some parts of the lexicon are slower and more resistant to change than others. The good news is that it's possible to let rates vary across characters:

  - **Gamma-distributed rates**: Lets characters vary faster or slower than others. [Pagel et al. (2007)](https://www.nature.com/articles/nature06176) find a relationship between word frequency and evolutionary rates (more frequent lexical items ~ slower to change).

A couple more methodological notes:

  - **Ascertainment correction:** We can only code cognates we can actually see. Sounds obvious enough – we can't code something we never see! But what this means is that there are no all-zero columns (even though, in reality, there were surely plenty of cognates that existed through history that disappeared from existence). The absence of lots of all-zero columns makes little difference for estimating tree topology (can't do any subgrouping if all languages look the same), but it *does* make a difference for estimating evolutionary rates. So this needs to be corrected for in the likelihood. If you see ascertainment correction mentioned in a paper, this is all it means.
  - **Binary vs multistate coding:** In the talk, I discussed binarising cognate data, which I would say is the most usual approach. However, it's possible to use multistate variables too (like the left half of slide 7). Binary coding can handle synonyms (if a language has two words for the same meaning, it just has two 1s), but also treats every binary character as independent, even though characters of the same meaning class are very much not independent. Multistate coding neatly handles lexical replacement as a single event (if a language replaces word A with word B, it's just a single shift from A→B in one column. In binary land, a single lexical replacement results in a 0→1 gain in one column and a 1→0 loss in another). However, multistate transition models can get awkward. With many states you can't estimate a full rate matrix, so people fall back on an equal-rates Mk-style model. That model implies a lineage can switch back to an ancestral cognate class as easily as to any other, which is not realistic.
  - Don't confuse rate variation across *characters* with clock models, which describe rate variation across *branches*. 

**2. Clock models**

  - **Strict clock:** Every branch shares one rate of change. This is the simplest option, and essentially the assumption behind old-school glottochronology. It's rarely realistic for languages, but it's a useful baseline to test the fancier clocks against.
  - **Uncorrelated relaxed clock:** Each branch gets its own rate, drawn from a shared distribution (usually lognormal), independently of its neighbours. A lineage can have a burst of rapid change without its sisters or daughters inheriting it. This is a common default in linguistic studies.
  - **Random local clock:** Rates are inherited down the tree and change only at a few points, so whole clades share a rate. The model estimates how many rate shifts there are and where they happen. Intuitively, this fits a subgroup that went through an unusually turbulent period of change.

**3. Tree prior**

  - **Yule (pure birth):** Lineages split at a constant rate and never die out. Obviously unrealistic (languages do go extinct), but simple, with few parameters, and often a reasonable approximation when you only observe the survivors.
  - **Birth-death:** Lineages split at one rate and die out at another. Usually paired with a sampling proportion (what fraction of the family's languages made it into your dataset), which matters because hardly any dataset includes every language in a family.
  - **Fossilised birth-death:** Birth-death, plus the possibility of sampling lineages at different points in time, so ancient languages enter the tree as dated samples. Crucially, a dated sample can either sit on its own branch or be a *sampled ancestor* directly on the line to its descendants. (See the slide 26 note below for some spicy drama on this.)
  - **Coalescent:** Traces a sample of lineages backwards in time within a single population until they merge. It was built for population genetics (gene copies within a species), not for one lineage splitting into many. You'll see it in BEAUti's dropdown, but it's rarely the right choice for a language family.

As for how on earth you're supposed to choose among this smorgasbord of options? The nice thing is you don't have to limit yourself to one particular model specification. And in fact, unless you have strong a priori reasons for preferring a particular transition model/clock model/tree prior over others, you probably shouldn't.

The usual approach is to run the analysis several times with different combinations of model settings, and compare how well each one fits using its **marginal likelihood** (the P(data) bit on slide 14). This is the probability of the data under a given model, averaged over every possible tree and parameter value. Because it’s an average, a model with lots of extra parameters gets penalised automatically if it doesn’t earn its keep. The catch is that, as slide 17 showed, MCMC works precisely because it never has to calculate this term. So estimating it takes extra, fairly computationally expensive runs, using methods such as path sampling, stepping-stone sampling or nested sampling (all available as BEAST2 packages). The ratio of two models’ marginal likelihoods is called a **Bayes factor**, and it tells you how strongly the data favour one model over the other.

Note that, at least if everything is well behaved and goes as it should, the precise model settings should have relatively little impact on the tree topology that you end up inferring. Evolutionary rates (and therefore dates) tend to be more temperamental and sensitive to model choice, which gets to what I was saying in the session about treating branch lengths and dating in language trees with more suspicion (see e.g. [Ritchie & Ho 2019](https://doi.org/10.1093/jole/lzz005)).

### Some footnotes to specific slides

**Slide 9:** In the discussion, we talked about this idea that perhaps coding lexical cognate sets on the basis of regular sound correspondences, and then putting them in a phylo model, is a little circular. The idea here is that, when you're manually reconstructing regular sound changes, you're often inferring certain subgroupings yourself. So you're kind of presupposing language subgroupings to determine cognacy, which you then put in a tree model to infer subgroupings... I'm not sure how much of a problem this really is, but it feels at least slightly awkward to me.

As a personal aside, on this task of distinguishing genuine cognates (i.e. forms with a common ancestral source) from similarities due to borrowings and chance resemblances... In principle, I feel it's less-than-ideal that we deal with this process as a manual data-coding/filtering issue. In a utopian fantasy dreamworld, we might wanna code lexical similarity in an automated, neutral way (agnostic as to the source of that similarity), include all of the lexical similarity data we can get (rather than manually throwing out parts we don't think will be useful) and then let a model sort out which are likely to be shared lexical innovations vs similarity due to borrowing or chance, or conversely, dissimilarity of genuine cognates due to accumulation of wild sound changes, or semantic shift. I'm not the only one to think of this, but it's an incredibly difficult task.

**Slide 16:** The formula for calculating the number of rooted bifurcating trees is (2n-3)!! where n = number of tips.

**Slide 18:** Running several MCMC "chains" just means running the exact same MCMC process a few times over, so you can make sure you get roughly the same result each time. Verification means checking the MCMC trace for each chain to make sure they all converge in the same area. You'll also want to check something called ESS (effective sample size) for each parameter in the model and make sure it's sufficiently high (ideally >200). It's an "effective" sample size rather than just a regular sample size because each individual step in an MCMC chain is not independent of the one before.

**Slide 26:** Ok, buckle up, because we didn't really get time to talk about this in the session itself.

[Chang et al. (2015)](https://doi.org/10.1353/lan.2015.0005) got their Steppe-compatible root by forcing ancient languages such as Latin and Vedic Sanskrit to be the _direct_ ancestors of their modern relatives. In other words, those sampled ancestors were treated as internal nodes in the tree. To explain this a little more concretely: Take Latin – specifically, the particular version of Latin that's coded up and represented in your dataset. The usual trick is simply to treat it as a tree tip, the same as any of your other (modern) languages, but specify a date constraint as a prior that says "this tip must terminate at x date" (or range of dates if you're not quite certain). You can see an example if you look closely at the Sagart et al. phylogeny (slides 20–21). Old Tibetan, Old Chinese and Old Burmese all hang off to the side on a little branch of their own. Chang et al. took a different approach, where they forced Latin to be an internal node, directly ancestral to the Romance languages. It's like saying your sampled ancestor language is a direct grandparent, versus a closely related great aunt. 

What's the consequence of the great aunt vs grandparent choice? Well, in practice, if you take the great aunt approach and the terminal branch to the old language is very small, then it might not make much difference. But it does mean that innovations can accumulate on that branch, so you're allowing for your particular sampled version of Latin/Old Tibetan/whatever to differ a little from the hypothesised genuine common ancestor of all the Romance/Tibetan/etc. languages. Depending on the circumstances, that might be unsatisfying, or it might actually be desirable (can you really say that your version of Latin is _the_ one true ancestor to all modern Romance languages, or is it a reflection of Latin recorded in a particular time and place, which might have accumulated a few changes of its own from the true ancestor?).

Now, think about what it means for dating. If, like Chang et al., you force Latin to be a direct ancestor node, and you give that node an age constraint, then that's it. You've pinned down the Romance lineage, and the model can calibrate on this. You're saying "This is my sampled ancestor, Latin. It's x years old. Therefore, the split of modern Romance can be no older than x." Nice, simple and intuitive for linguists. On the other hand, if you give Latin its own tip, with its own little branch which can accumulate changes, then there is going to be _another_ parent node above that, which is a common ancestor linking your Latin tip with all the modern day Romance languages. You're essentially saying "This is my sampled ancestor, Latin. It's x years old. But the one true common ancestor, from which all the Romance languages descended, is _older_ than x years." This results in the same number of accumulated changes spread over more time, which implies a slower rate of change. Repeat across several sampled ancestors throughout the Indo-European tree and, so the reasoning goes, you're going to get a systematically slower estimated rate of change, therefore longer branches throughout the tree, therefore an older estimate of the age of the tree overall. Chang et al. argue that this is why previous studies estimate older root ages for Indo-European, consistent with the Anatolian hypothesis, and, by contrast, their direct ancestor approach results in a younger root age estimate consistent with the Steppe hypothesis.

[Heggarty et al. 2023](https://doi.org/10.1126/science.abg0818) then took another approach again. Instead of forcing sampled ancestors to be tips or direct ancestral nodes, they used a fancy tree prior which treated each ancient language's ancestry as something to estimate from the data. In other words, you leave open the possibility that the Latin in your sample could be _either_ a tip of its own (great aunt) _or_ the direct ancestral node of Romance (grandparent), and let the model infer which is the better option. It seems the answer was mostly "great aunt", pulling the estimated root age older, consistent with the Anatolian hypothesis. Additionally, I should mention that Heggarty et al. used a substantially new dataset, so the difference in result between Chang et al. and Heggarty et al. can't be attributed purely to model choice. At least some of it might be the outcome of new evidence from the new dataset as well.

I leave it as a genuinely open exercise for the reader to think about which approach is best here, I'm not trying to lead you one way or the other. Personally, I remember finding it a little unsatisfying to treat ancestral languages as tree tips and not-true-ancestors, it just felt a little hacky/messy. So when Chang et al. came out, I liked the idea and found the reasoning quite plausible. But now I lean somewhat in the opposite direction. I think unless you're very certain that your sampled ancestor represents a snapshot of a language of a specific population, which others split from, then maybe the great aunt approach is more ecologically accurate (keeping in mind it's all a bit messy anyway, since language divergence is a gradual process and languages don't split cleanly in a precise instant like a tree diagram would suggest). For me, maybe the biggest takeaway is that root age estimates can be largely a product of the researcher's model choices rather than the data, which is why I'm cautious about interpreting too much from inferred dates in linguistic trees. The Heggarty approach is potentially a nice data-driven way around this particular model choice, though it comes at the cost of more degrees of freedom, and sometimes to me it just feels like these things become a layer of uncertainty on top of uncertainty on top of uncertainty. So, IDK, I would say tread carefully... But I hope this little write-up helps contextualise the Indo-European back-and-forth a bit more at least.

**Slide 33:** One issue here is that the lexical design space is practically infinite. You can innovate any number of novel words to say more things, and so the likelihood of unrelated languages landing on the same word for the same meaning by sheer coincidence is, well, not zero, but very small. (A famous example is Mbabaram, a Pama-Nyungan language of Australia, whose word for "dog" is... _dog_.) So, you don't really have an issue with parallel innovations. If a set of languages share a cognate wordform, then, chance of undetected chance resemblance/borrowing notwithstanding, it's a pretty good indication that the languages belong in some clade together. The problem with grammatical variables, at least certainly the kind of grammatical features that get coded in large comparative datasets like Grambank, is that the design space for grammatical features is often very small. There are only so many options for a language to choose from: only a handful of logically possible basic word orders, only so many grammatical genders languages tend to have, only so many ways of slicing temporality into different tenses, and so on. So you will get many, many instances of languages that share some feature, e.g. they're both SOV, or they both have two genders, despite being half a world away and utterly unrelated. Languages will innovate SOV word order, or shift from, say, a three-gender system to a two-gender system, independently, again and again (i.e. homoplasy), which then makes it hard to get much useful subgrouping information out of these features. And that's before we even think about potential universal selection pressures that could influence the evolution of a language's grammar. This doesn't mean grammatical features are totally off limits per se, and people have certainly tried [see Greenhill et al. (2017) for some discussion](https://doi.org/10.1073/pnas.1700388114), but it hasn't really caught on.

### Resources and further reading

**Some linguist-oriented overviews**

  - Bowern, Claire. 2018. Computational phylogenetics. _Annual Review of Linguistics_ 4(1). 281–296. <https://doi.org/10.1146/annurev-linguistics-011516-034142>.
  - Greenhill, Simon J., Paul Heggarty & Russell D. Gray. 2020. Bayesian Phylolinguistics. In _The Handbook of Historical Linguistics_, 226–253. John Wiley & Sons, Ltd. <https://doi.org/10.1002/9781118732168.ch11>.

**If you really wanna get into it**

  - Drummond, Alexei J., & Remco R. Bouckaert. 2015. _Bayesian Evolutionary Analysis with BEAST_. Cambridge: Cambridge University Press.
  - Felsenstein, Joseph. 2004. _Inferring Phylogenies_. Sunderland, MA: Sinauer.

**Hands-on tutorials**

  - [Taming the BEAST](https://taming-the-beast.org/)
  - [RevBayes tutorials](https://revbayes.github.io/tutorials/) (I haven't actually used RevBayes, but I like the philosophy behind it – you're forced to be explicit about your model choices, so it's harder to learn but makes it less black-boxy. And you can visualise the model as an explicit graph.)

**Software**

- **Cognate coding:** [LingPy](https://lingpy.org) (includes LexStat), [EDICTOR](https://edictor.lingulist.de).
- **Exploratory:** [SplitsTree](https://software-ab.cs.uni-tuebingen.de/download/splitstree6/welcome.html) (NeighborNet).
- **Inference:** [BEAST2](https://www.beast2.org) with the Babel package for linguistic models ([tutorial](https://taming-the-beast.org/tutorials/LanguagePhylogenies/)), [MrBayes](https://nbisweden.github.io/MrBayes/), [RevBayes](https://revbayes.github.io).
- **BEAST2 workflow:** BEAUti (model preparation), TreeAnnotator and DensiTree (all bundled with [BEAST2](https://www.beast2.org)), [Tracer](https://github.com/beast-dev/tracer/releases) (for checking that everything converged nicely at the end).
- **Linguistics-specific:** [BEASTling](https://github.com/lmaurits/BEASTling) (builds BEAST configurations from linguistic data; very linguist-friendly), [contacTrees](https://github.com/NicoNeureiter/contacTrees).


PS I snapped the cover (and closing) image while kayaking in the Spreewald recently. I'm not sure anyone noticed, but the cover version is actually flipped upside-down (the closing slide is the right way up). There is a strained, cringeworthy metaphor for the way we can never directly observe language phylogenies, only mirror them in a phylogenetic tree hypothesis. (Mostly I just wanted a picture with trees and thought this was a nice one.)
