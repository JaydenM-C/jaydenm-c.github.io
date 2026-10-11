---
title: "Evaluating information loss from phonological dimensionality reduction"
collection: talks
type: "Talk"
permalink: /talks/evaluating-information-loss
venue: "Speech Science and Technology (SST) satellite symposium: The role of predictability in shaping human language sound patterns"
date: 2016-12-16
paperurl: 'https://doi.org/10.6084/m9.figshare.4465976'
location: "Western Sydney University, Australia"
---

As in many sciences, cross-linguistic data is often complex and multi-dimensional. The PHOIBLE database of phonological inventories (Moran et al. 2014) is one example, containing 2160 distinct segments across 2155 phoneme inventories. Each segment type is defined by a unique vector of (mostly binary) distinctive phonetic and phonological features. This multivariate dataset can be modeled as a set of coordinates, where each variable (e.g. segment, its distinctive features, its presence in a language, the language's genealogy and location) is an axis in high-dimensional space.

Often, such high dimensionality is reduced during analysis. For example, methods which match segments between phonological inventories, such as phonetic string alignment algorithms used for the automated detection of cognates or phonetic similarity measures, typically collapse the vast variability of segment types into as few as ten sound classes. What is unclear is how much information is lost and whether this loss is uniform across languages, subgroups and linguistic areas. This question is important given the increase in publications using large cross-linguistic databases that conflate phonological variability, such as the Automated Similarity Judgment Program (ASJP; Wichmann et al. 2016), and quantitative approaches using these datasets to approximate phonological diversity, linguistic distance measures, language classification, etc.

Presented here is a method for empirically tracking information loss resulting from dimensionality reduction procedures. We evaluate several common procedures and demonstrate that information loss varies significantly across the world's languages and between different methods, and further, information loss is correlated with broad-scale linguistic genealogy and geography.

### Methodology

To measure information loss in a given language for a given dimensionality reduction procedure, we use a simple 'conflation index', c, which compares the number of distinct phonemic categories in the language after reduction, nreduced, with the full number of distinct categories prior to reduction ninitial. Given that a maximally conflated inventory would contain 1 category, and thus be reduced by (ninitial - 1) phonemes, we define c as (ninitial - nreduced)/(ninitial - 1). We measure c for each language in PHOIBLE for each reduction procedure, and examine its distribution among geographic and genealogical groups. The reduction procedures examined are mappings onto (1) the ASJP orthography (Wichmann et al. 2016); (2) the SCA inventory (List 2012); and (3) Dolgopolsky's macro-phoneme set (Dolgopolsky 1964). Resulting conflation levels are compared across Glottolog continent-level Areas and Families (Hammarström et al. 2016).

### Results

An example of c values, for the ASJP procedure, is in Fig. 1. Distributions of c are significantly non- normal (Shapiro-Wilk's W, alpha=0.05) within the majority of Glottolog areas and families for all reduction procedures. Accordingly, comparisons are made by non-parametric methods. Kruskal-Wallis H tests a null hypothesis that samples are from the same underlying distribution.

We first examined whether the distribution of c varied between continent-sized areas. Results allow us to reject to hypothesis that samples from distinct continental areas are all drawn from the same population. Post-hoc pair-wise comparisons between each of the 10 area pairs reveal a significant difference (at an adjusted alpha rate corresponding to single-comparison rate of 0.05) between Pacific and Africa, the Americas and Asia; and Africa and the Americas (ASJP method), between all pairs bar Europe–Africa and Europe-Asia (SCA), and between all bar Europe and Africa (Dolgopolsky).

To examine genealogical variation in the conflation index c, we compared Glottolog families within areas, asking if samples were drawn from a single area-specific population. Hypothesis testing requires families of reasonable size (we use n>=10). For all three inventory reduction procedures, all areas do contain families with significantly different distributions of c, with the exception of Europe in the ASJP condition. Post-hoc pair-wise testing reveals considerable variation in the proportion of pairs which differ significantly, across areas and across procedures. In Africa, only few family pairs are significantly different (1%-20% across the three reduction procedures, n=15) and similarly in the Americas (4%-22%, n=171). In Asia pair-wise, significant differences between families are more common (24%-33%, n=45), as they were in Europe for the non-ASJP procedures (30%, n=10). In the Pacific, too few families are represented sufficient richly to comment.

### Discussion

All three conflation methods affect continental Areas unequally to a statistically significant degree. Moreover, the variation within Areas differs: Asia is most diversely affected, Africa and the Americas are less so yet still show statistically significant diversity. Only within Europe is there no statistically significant difference among families, and only for one reduction procedure, ASJP. Consequently, research designs employing phonologically conflated data and tested initially with European languages may not generalise as expected to other areas of the world.

Conflation methods affect continental Areas in differing patterns and to varying extents. Dolgopolsky's method, which effects the most radical conflation, has the starkest disparity across Areas, relative to ASJP and SCA methods. Comparing Areas according to the disparities between families when different methods are employed: Europe is the most uniform and Asia is the least, however the methods produce both different magnitudes and rankings of disparities throughout.

### Conclusions

High dimensionality is a hallmark of cross-linguistic data. As databases grow and research focus turns to macro-scale phenomena, attention should be paid to the kind and quantity of information lost during data processing and analysis. In this study, we have evaluated how information is lost through three processes which conflate phonological information, including the method employed by ASJP and subsequently used in numerous publications for topics including comparing segments between languages, for proposing regular sound correspondence, for approximating phonological distance and diversity, and for proposing genealogical classifications. However, as we show here, reducing phonological data before undertaking these analyses has broad but quantifiable ramifications for the results reported in these studies. Research designs should be robustly evaluated, using tools such as the conflation index presented here, c, to ensure broader generalizability and to highlight the shortcomings of research using conflated phonological information.


