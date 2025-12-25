---
title: "Chemical Architecture, Mechanical Reliability, and Environmental Implications of Natural Fiber Geotextiles for Erosion Control"
author: "Luiz Diego Vidal Santos"
bibliography: referencias.bib
csl: springer-vancouver.csl
reference-doc: modelo_formatacao.docx
fig-align: center
table-align: center
lang: en-us
---

Luiz Diego Vidal Santos, ORCID: 0000-0001-8659-8557, <ldvsantos@uefs.uefs.br>*, Universidade Estadual de Feira de Santana – UEFS, Pós-graduação em Planejamento Territorial, Feira de Santana - BA, Brasil

Francisco Sandro Rodrigues Holanda, ORCID: 0009-0000-9358-0531, <fholanda@academico.ufs.br>, Universidade Federal de Sergipe, Departamento de Engenharia Agronômica, São Cristóvão – SE, Brasil

Emersson Guedes da Silva, ORCID: 0009-0004-9742-6215, <academicoguedes@gmail.com>, Universidade Federal de Sergipe, Departamento de Engenharia Agronômica, São Cristóvão – SE, Brasil

Marlon Pedro Santos Gomes, ORCID: 0009-0007-8167-7636, <marlongomes2671@gmail.com>, Universidade Federal de Sergipe, Departamento de Engenharia Agronômica, São Cristóvão – SE, Brasil

Alarico José da Silva Azerêdo, ORCID: 0009-0002-9805-9870, <alaricofilho76@hotmail.com>, Universidade Federal de Sergipe, Departamento de Engenharia Agronômica, São Cristóvão – SE, Brasil

Renisson Neponuceno de Araújo Filho, ORCID: 0000-0002-9747-1276, <renisson.neponuceno@ufrpe.br>, Universidade Federal Rural de Pernambuco, Departamento de Tecnologia Rural, Recife – PE, Brasil

Eliana Midori Sussuchi, ORCID: 0000-0001-9425-0921, <midori@academico.ufs.br>, Universidade Federal de Sergipe, Departamento de Química, São Cristóvão – SE, Brasil

Alceu Pedrotti, ORCID: 0000-0003-3086-8399, <alceupedrotti@gmail.com>, Universidade Federal de Sergipe, Departamento de Engenharia Agronômica, São Cristóvão – SE, Brasil

## Abstract

The degradation of tropical soils and the microplastic liabilities associated with conventional geosynthetics require bioengineering solutions based on renewable materials with timed functionality. This study evaluates the technical feasibility and functional durability of geotextiles produced from *Typha domingensis* and *Syagrus coronata*, using probabilistic modeling to propose engineering specifications grounded in chemical and mechanical degradation under real field exposure. Results indicate that fiber chemical architecture, particularly the lignin/cellulose ratio, constrains degradation kinetics and defines service windows between 60 and 180 days. Alkaline mercerization (6% NaOH) promoted critical morphostructural reorganization, balancing strength and ductility to extend Functional Service Life (FSL) to the level required for vegetative establishment. Resin treatments exhibited non-linear behavior: monolayer application delayed degradation (~120 days), whereas overlap configurations induced early delamination. Weibull analyses confirmed that specification based on the reliability percentile ($P_{10}$), rather than simple mean values, provides a robust criterion to align surface engineering with required service windows (90–150 days). Integrating microstructural characterization with reliability modeling supports deploying these materials in tropical soil bioengineering.

**Keywords.** Erosion control; Environmental pollution; Biodegradation kinetics; Ecosystem services; Weibull reliability.

## 1. Introduction

Soil degradation in tropical regions operates through mechanisms distinct from those observed in temperate contexts, primarily because rainfall intensity and elevated temperatures accelerate organic-matter mineralization. According to @Brady2009, this acceleration, combined with highly weathered Oxisols, increases nutrient losses via leaching.

In tropical biomes such as the Caatinga and Cerrado, soils with low natural fertility show high vulnerability to nutrient depletion driven by strong hydrological seasonality. As discussed by @Lammel2015, this biogeochemical depletion compromises both the physical matrix and key nutrient reservoirs required for agricultural productivity [@Cardoso2006].

The predominance of 1:1 clay minerals in tropical pedogenesis, coupled with low soil organic carbon, produces soils with minimal structural cohesion. @Bispo2017 demonstrated that this weakened structure amplifies erosion susceptibility through raindrop impact and particle transport by surface runoff during convective storms.

Shear strength in non-cohesive soils, quantified by the effective internal friction angle as a function of particle-size distribution and density [@Veylon2015], becomes especially deficient in Quartzarenic Neosols along tropical riverbanks. In these soils, @Mahannopkul2019 characterized low cohesion, high porosity, and limited mechanical resistance, and this geotechnical vulnerability becomes critical on steep slopes (e.g., >25°), where hydrological loading can reduce safety factors toward the failure threshold [@Nunes2022].

As noted by @Islam2013, this configuration promotes incipient instability during rainy periods when pore-pressure increases reduce effective normal stress, precipitating sliding failure; consequently, allowable bearing capacity of shallow foundations may be constrained to 50–100 kPa, restricting conventional reinforcement options.

Geotechnical vulnerability increases under anthropogenic pressure. According to @Borrelli2017, irreversible loss of the surface soil layer, which concentrates bioavailable phosphorus and nitrogen, combines with sedimentation-driven eutrophication in downstream fluvial ecosystems, degrading regional water quality. In the Brazilian semi-arid region, sediment yield on degraded slopes may reach 45 Mg·ha⁻¹ during the rainy season, exceeding pedogenic rates by two orders of magnitude and representing the dissipation of centuries of biogeochemical cycles without restoration prospects at human timescales [@Vannoppen2017].

Traditional technological responses have largely relied on petroleum-derived geosynthetics. As reviewed by @Holanda20251, polypropylene, polyethylene, and polyethylene terephthalate exhibit high strength and UV stabilization via benzotriazole, reinforcing dependence on non-renewable feedstocks.

Their durability can be described by three failure modes. Excessive-stress rupture occurs via plastic deformation followed by hardening through molecular orientation [@Carneiro2018], whereas creep manifests as progressive deformation under sustained load and results in gradual functionality loss over decades [@BarreiraPinto2023]. UV radiation under tropical irradiance (5–8 kWh·m⁻²·day⁻¹, spectra 280–350 nm) progressively reduces tensile strength, as addressed in ISO and ASTM specifications for geotextile performance [@ISO1996].

This paradigm entails a structural contradiction because materials designed for multi-decadal persistence in landfills and road sub-bases typically have projected service life between 30 and 50 years [@Koerner2016], generating long-term environmental liabilities when deployed in agroecological systems [@Bhatia2010]. In polypropylene geotextiles, @Ibanez2014 and @Konvalinkova2015 reported high recalcitrance under anaerobic conditions, with gradual mechanical fragmentation into microplastics (<5 mm) whose infiltration into soil food webs compromises microbial symbioses and induces rearrangements of soil microbiota.

@Bai2022 quantified mean densities of 349±137 particles·kg⁻¹ in covered soils after UV exposure, with annual emissions estimated in the thousands of tons for marine environments, evidencing trophic transfer in adjacent terrestrial and aquatic ecosystems. This limitation motivates controlled temporary persistence as a functional attribute: while synthetic geotextiles resist biodegradation for decades, @Chakravarthy2021 and @Midha2017 showed that lignocellulosic fibers degrade progressively over 6–18 months, compatible with establishment of permanent root systems.

Durability studies indicate that natural-fiber geotextiles treated with bituminous emulsions retain 82–85% of initial strength after 90 days of soil exposure [@Thakur2019], reinforcing that programmed degradation can be specified as functional behavior rather than treated as a drawback [@Pil2019].

According to @Rodriguez2023, lignocellulosic composition imposes an intrinsic functionality timeframe governed by microbial consortia and environmental oxidative stress, which can synchronize with vegetative establishment kinetics in soil bioengineering. @Almeida2023 and @Singh2024_vetiver showed that root networks can reach mechanical equivalence to synthetic reinforcement within 90–180 days.

Life-cycle assessments of the cradle-to-gate type suggest that bio-based geotextiles may display favorable environmental profiles across several impact categories relative to petrochemical alternatives, although relevant sensitivities remain (e.g., transport contributions and water-use trade-offs), making it inadequate to infer environmental performance from biodegradability alone [@Amadou2022_natural_geotextile_cost]. In this framing, durability engineering emerges as an approach to optimize timed functionality and reduce externalities when replacing conventional geosynthetics in tropical soil bioengineering [@Lorenzo2024_Typha].

To this end, this study evaluates the technical feasibility and functional durability of geotextiles produced from *Typha domingensis* and *Syagrus coronata*, using probabilistic modeling to propose engineering specifications based on chemical and mechanical degradation under real field conditions. Performance validation is anchored in Weibull statistics and linear regression models, ensuring traceability between microstructural changes and macroscopic failure modes.

The central hypothesis is that the lignin/cellulose ratio (L/C) acts as the primary predictive variable for degradation kinetics and Functional Service Life (FSL). Complementarily, surface-engineering interventions are expected to modulate the mechanical decay curve ($P_{10}$), enabling critical synchronization between material strength loss and the time required for vegetation root-system establishment.

## 2. Materials and Methods

The experimental design combined monotonic mechanical response quantification of natural fibers with scanning electron microscopy (SEM) morphologic characterization, keeping service-life inference tied to measurable metrics and normative test protocols. Surface engineering interventions included alkaline mercerization in NaOH (3%, 6%, and 9%) and polymeric coating with Hydronorth® resin at two areal dosages (0.0932 and 0.1864 mL·m⁻²), preserved as process variables during data consolidation.

For the set evaluating alkaline mercerization in *Typha domingensis* geotextiles, treatment was conducted by immersion in NaOH solution for 24 h at 3% (0.75 mol·L⁻¹), 6% (1.5 mol·L⁻¹), and 9% (2.25 mol·L⁻¹), with constant bath ratio; after reaction, material was washed with running water until neutralization and air-dried in a shaded, ventilated environment over a timescale of days. Photographic documentation of processing is shown in Figure 1.

![**Figure 1.** Photographic record of collection, processing, and drying of plant fibers in a shaded and ventilated environment.](../3-IMAGENS/metodologia_lc_k/coleta.png){width=90%}

Natural degradation monitoring was conducted on a tropical slope with 45° inclination at the Rural Campus of the Federal University of Sergipe, with installation in rectangular plots along the slope to reproduce field application and minimize edge effects by sampling central portions (Figure 2). Exposure occurred between May and November, a period characterized by cumulative precipitation of approximately 350 mm and mean daily UV-B irradiance of 6.5 kWh·m⁻²·day⁻¹, according to local monitoring.

![**Figure 2.** (a) Loom used to manufacture the geotextile and (b) experimental slope for installation and field exposure.](../3-IMAGENS/talude.png){width=90%}

To characterize biodegradation kinetics within a service window up to 180 days, sections of approximately 20 cm × 20 cm were removed at programmed intervals (0, 30, 60, 90, 120, 150, and 180 days), dried at 60 °C for 24 h before specimen preparation.

Because sampling and tests are destructive and material integrity conditions specimen preparation under the same protocol, the effective number of specimens per species × treatment × time varied over exposure, including combinations absent at late times.

Fibers were selected and prepared for mechanical tests and microstructural characterization, preserving the fibrous fraction of interest (Figure 3).

![**Figure 3.** Macroscopic aspect of the fibrous fraction and leaf blade used for sample preparation.](../3-IMAGENS/metodologia_lc_k/fibra_limbo.jpg){width=80%}

### Tensile and puncture tests in fibers

Tensile tests were conducted on specimens composed of fibers (and/or fiber bundles), clamped and subjected to monotonic loading in a universal testing machine, with initial grip separation of 110 mm and crosshead speed of 20 mm·min⁻¹.

Static puncture tests of the CBR type were treated as a complementary measure of integrity under concentrated solicitation, using circular specimens of 70 mm, a 50 mm clamping ring, a 17 mm punch, and test speed of 50 mm·min⁻¹.

### Lignin/Cellulose ratio (L/C)

The lignin/cellulose (L/C) ratio was quantified by Fourier Transform Infrared Spectroscopy (FTIR) using a PerkinElmer Spectrum Two instrument, ATR mode, 4000–400 cm⁻¹ range, 4 cm⁻¹ resolution, and 32 scans per spectrum. Spectral analysis focused on bands attributed to cellulose (1030 cm⁻¹) and lignin (1510 cm⁻¹), following the methodology described by @Pandey1999. The L/C ratio was estimated by the ratio between absorption intensities at these bands according to

\[L/C = \frac{I_{1510}}{I_{1030}}\]

where $I_{1510}$ and $I_{1030}$ are the absorption intensities at the respective bands.

### SEM and extraction of morphological descriptors

Fibrous surfaces were analyzed by SEM after gold sputtering using a Cressington coater (Kurt J. Lesker 108) and image acquisition in a HITACHI TM 3000 under vacuum with 15 kV electron beam, 50× magnification, and 8-bit quantization (histogram scale 255) to support subsequent digital processing.

Region-of-interest segmentation and damage quantification were operationalized by gray-level thresholding, in which darker regions were treated as damaged zones following the processing logic described in internal documentation.

Quantitative micrograph analysis was implemented in Python routines based on OpenCV and scikit-image. Intensity normalization preceded gradient-based orientation estimation (Sobel operators) and extraction of anisotropy descriptors via an orientation index defined as $IO = 1 - (\sigma_\theta/90^\circ)$, with typical Gaussian smoothing of 1.0 pixel and thresholding by the 75th percentile of gradient magnitude.

Porosity detection was treated as a segmentation problem with Gaussian smoothing of 2.0 pixels, threshold set to 0.7 times Otsu’s threshold, minimum area of 20 pixels, and morphological filling of 10 pixels. Connectivity and structural continuity characterization were supported by skeletonization (Zhang–Suen) and by skeletal density and junction metrics, with junction smoothing parameter of 2.0 pixels.

Surface texture was quantified by gray-level co-occurrence matrix (GLCM), using distances of 1, 2, 3, and 5 pixels and angles of 0°, 45°, 90°, and 135°, with 256 gray levels and symmetric normalization, targeting contrast, homogeneity, energy, and correlation.

### Statistical analyses and modeling

To quantify temporal trends and sensitivity to process variables under time-unbalanced sampling, tensile strength was described by ordinary least squares (OLS) linear models with exposure time as a continuous predictor (centered) and categorical factors for species and treatment level, including interaction terms. Inference was based on HC3 robust standard errors and term-wise Wald tests; additionally, Type-II ANOVA decomposition was reported along with effect-size estimates (partial η²).

In the analyzed set, the tensile dataset totaled N=154 observations in the resin experiment and N=127 observations in the NaOH experiment, reflecting the variable number of specimens per time and the presence of missing combinations at late times. Consolidation and analysis were carried out in Python (version 3.13), using `statsmodels` for modeling and tests, `scipy` for auxiliary routines, and `matplotlib/seaborn` for visualization.

## 3. Results and Discussion

### 3.1. Lignocellulosic Architecture and Chemical Profile

The mechanical performance and biodegradation trajectory of natural-fiber geotextiles tend to depend on the lignin-to-cellulose ratio that organizes the molecular scaffold of the plant cell wall. Cellulose establishes a semi-crystalline network associated with initial stiffness, whereas hemicelluloses and lignin modulate accessibility to water and degrading agents, conditioning the temporal kinetics of capacity loss [@Shaghaleh2018].

The resulting microfibrils, embedded in an amorphous matrix of hemicelluloses composed of branched heteropolysaccharides and in lignin formed by cross-linked phenylpropanoid oligomers, effectively reduce accessibility of glycosidic sites to enzymatic and chemical hydrolysis pathways [@Karim2023, @Poletto2012].

Differences in lignin/cellulose ratio and in the microstructural distribution of these constituents tend to translate into contrasting degradation trajectories and, consequently, into distinct Functional Service Life windows under comparable environmental conditions [@Haviland2024]. In this framing, lignin acts as a relatively more recalcitrant and hydrophobic component, modulating accessibility to water and degrading agents and influencing the rate of mechanical-capacity loss over time [@Nguyen2024].

**Figure 4.** Multilevel hierarchical architecture of lignocellulosic fibers: **(a)** schematic representation of cellulose polymer chains, **(b)** supramolecular organization of the crystalline core of cellulose microfibrils, **(c)** transverse section of the plant cell wall, and **(d)** tissue level and L/C ratio: schematic comparison of fiber bundles of *Typha* (low lignification) and *Syagrus* (high lignification).

![ ](../3-IMAGENS/fig_01.png)

Chemical characterization of *Syagrus coronata* fibers (Table 1) indicates 32% lignin versus 22% in *Typha domingensis*, and this compositional contrast translates into distinct degradation trajectories under field exposure. Untreated *Typha* fibers lose mechanical viability at 60 days of environmental exposure (63.2% reduction in tensile strength), whereas *Syagrus* maintains observable structural integrity up to 90 days, evidencing recalcitrance associated with higher lignin content [@Holanda2020].

The lignin/cellulose ratio (L/C) has been employed as a useful index to discuss recalcitrance [@Rodrigues2020]. Based on the experimental-data compilation in this manuscript (Table 3), an inverse exponential relationship between L/C and the degradation rate constant ($k$, day$^{-1}$) is observed:

$$
k = 0.032 \cdot e^{-2.1 \cdot (L/C)}
$$

For *Typha* (L/C = 0.46), this yields $k$ = 0.0118 day$^{-1}$, implying a half-life of 59 days under mesophilic conditions (25°C, 60% relative humidity). In contrast, *Syagrus* (L/C = 0.67) presents $k$ = 0.0082 day$^{-1}$ (half-life = 85 days), consistent with field observations in which untreated *Syagrus* geotextiles maintained structural integrity after 120 days, whereas *Typha* geotextiles failed at 60 days.

**Table 1.** Comparative chemical–mechanical profile of tropical lignocellulosic fibers for biodegradable geotextiles.

| Species | Cellulose (%) | Lignin (%) | L/C | Initial tensile (N/mm) | Strain (%) | k (day$^{-1}$) | t½ (days) | FSL P₁₀ (days)† |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| **Typha domingensis** | 48 | 22 | 0.46 | 107.6 ± 25.3 | 2.9 ± 2.1 | 0.0118 | 59 | 42 |
| **Juncus sp.** | n.d. | n.d. | n.d. | 72.6 ± 16.9 | n.d. | >0.015* | <46* | <30* |
| **Syagrus coronata** | 48‡ | 32 | 0.67 | 142.1 ± 31.6 | 2.9 ± 2.1 | 0.0082 | 85 | 38§ |

**Notes.** n.d. indicates “not determined”; FSL is based on the 10th percentile of Weibull failure (P₁₀). Values marked with an asterisk are estimated from a 97% loss at 60 days, whereas the symbol ‡ indicates an estimate consistent with the adopted L/C ratio (cellulose ≈ lignin/(L/C)); for internal consistency, L/C values and derived parameters ($k$, t½) should remain consistent among equation, table, and text.

However, the recalcitrance contrast summarized in Table 1 does not ensure linear durability extension across all combinations of architecture and loading, because abrupt structural collapse with approximately 65% strength loss within ~30 days has been reported for high-lignin configurations when the spatial distribution of this polymer within the cell wall favors fragile crack-initiation zones [@Silva2025].

This biphasic behavior, characterized by an initial phase of apparent stiffness retention followed by sudden failure [@Phan2025], suggests that the percolation geometry of the lignin phase, rather than only its global mass fraction, may influence biodegradation progression under shear and tensile stresses typical of vegetated slopes [@Zhang2024yao].

The relationship between chemical composition and temporal performance, schematized in Figure 2, describes a continuous pathway that starts from the L/C ratio, passes through degradation kinetics, and reaches the evolution of mechanical resistance over time. The diagram integrates degradation constants $k$ and half-lives $t_{1/2}$, strength-loss curves up to failure, and FSL estimates via the 10th percentile of Weibull failure models (P₁₀, with parameters β and η), as well as surface modification strategies by alkaline mercerization and polymeric coatings [@Lerpiniere2014] that shift this temporal curve.

**Figure 5.** Flow diagram integrating chemical composition, expressed by lignin/cellulose ratio, with temporal performance and Functional Service Life of geotextiles under different surface-treatment scenarios.
![Figure 5](../3-IMAGENS/fig_2.png)

*Note. The flowchart connects degradation constants $k$ and half-lives $t_{1/2}$ measured in the field, mechanical resistance trajectories up to failure, and Functional Service Life (FSL) derived from Weibull distributions at the design percentile P₁₀.*

Fourier Transform Infrared Spectroscopy (FTIR) links spectral signatures to susceptibility to chemical and biological cleavage. Bands at 1735 cm$^{-1}$ indicate hemicellulose susceptible to enzymatic hydrolysis; bands near 3300 cm$^{-1}$ indicate free hydroxyl groups favoring moist microenvironments; bands around 1600 cm$^{-1}$ quantify aromatic lignin. Peaks near 1590 cm$^{-1}$ characterize syringyl lignin with higher resistance to oxidative degradation. Bands in the 1234–896 cm$^{-1}$ region indicate cellulose crystalline ordering and a more robust physicochemical barrier against enzymatic cleavage.

**Figure 6.** FTIR spectra comparison between *Typha domingensis* and *Syagrus coronata*.
![Figure 6](../3-IMAGENS/figura_ftir_comparativa.png){width=100%}

*Note. The most relevant spectral differences are consistent with higher relative contribution of more hydrophilic fractions in *Typha* and higher aromatic contribution associated with lignin in *Syagrus*.*

This biochemical composition tends to be reflected in degradation kinetics. According to @Santos2023_PatenteTaboa, *Typha* loses 50% of initial strength in approximately 60 days under field conditions; in the experimental set analyzed here, *Syagrus* maintained functional integrity for periods exceeding 120 days, consistent with a slower degradation trajectory. In this set of results, the lignin/cellulose ratio (L/C) appears as a useful marker to describe recalcitrance contrasts and the pace of capacity loss, with *Typha* associated with faster degradation and *Syagrus* with slower degradation.

Although FTIR describes functional groups, crystalline organization assessed by X-ray diffraction (Figure 4) contributes to physical integrity. Segal et al. [@Segal1959] proposed a methodology indicating crystallinity indices of 52% for *Typha* versus 46% for *Syagrus*. According to Boerjan et al. [@Boerjan2003], this contrast suggests that higher lignin content in *Syagrus* can compensate for reduced crystallinity by filling the amorphous fraction and increasing rigidity. *Typha domingensis* fibers exhibit cellulose I peaks at 2θ ≈ 14.8° (plane 1-10/110), 16.4° (110), and 22.6° (200) [@Rowell1998].

In mechanical characterization, Fontes et al. [@Fontes2021] reported similar initial tensile strengths between species, with 3.14 N·mm$^{-2}$ for *Syagrus* and 3.57 N·mm$^{-2}$ for untreated *Typha*. Taken together, compositional and structural variations observed by FTIR/XRD/TGA are consistent with differences in microfibrillar integrity and initial mechanical performance.

**Figure 7.** X-ray diffractogram (XRD) of *Typha domingensis* and *Syagrus coronata* fibers.
![Figure 7](../3-IMAGENS/fig_drx_final.png){width=70%}

The higher thermal stability of *Syagrus*, associated with lignin content, can be reflected in a larger residual fraction. Thermogravimetric analyses under oxidative atmosphere (air, 10 °C·min$^{-1}$) indicate that *Syagrus* retains ~28% residual mass at 600 °C, versus ~21% for *Typha* [@Marchi2023].

### 3.2. Hydrophilicity, Biodegradation, and the Definition of Functional Service Life

The abundance of hydroxyl functional groups (-OH) on cellulose and hemicellulose surfaces tends to confer hydrophilic character to fibers, often associated with low water contact angles, which facilitates moisture ingress and creates microenvironments favorable to microbial colonization at early exposure stages in the field [@Chieng2017].

This fungal colonization is associated with extracellular cellulase activity, which cleaves β-1,4-glycosidic bonds and accelerates mass loss, connecting surface hydrophilicity to progressive reductions in load-bearing capacity [@deVries2010].

According to Schneider et al. [@Schneider2023], the biodegradation of lignocellulosic matrices results from two simultaneous mechanisms: enzyme-driven surface erosion from the cuticle and radial hyphal penetration forming microscopic tunnels and cavitation zones under tension. Nilsson and Daniel [@Nilsson1988] documented by electron microscopy that surface erosion dominates the first 30 days of exposure, later evolving into radial penetration that ruptures the lignified middle lamella and compromises cohesion between adjacent cells, a process consistent with mechanical behavior observed in tensile and puncture tests.

Thermogravimetric analysis (TGA), which measures mass loss with increasing temperature, allows tracking exposure-related changes. As reported by Cardoso et al. [@Cardoso2023_TGA_biomass], an initial shoulder between 220 and 280°C, attributed to hemicellulose pyrolysis, tends to decrease as degradation advances.

The main cellulose peak (300–360°C) shifts to lower temperatures as depolymerization progresses, whereas the fraction attributed to lignin above 400°C tends to remain more stable [@Liu2008]. This pattern is consistent with the interpretation of Leng et al. [@Leng2020_TGA_PKM] that lignin acts as a more recalcitrant residue, persisting after degradation and contributing to soil organic carbon accumulation.

Experimental data on natural geotextiles indicate that the lignin/cellulose ratio (L/C) does not uniquely govern initial strength, but it is associated with failure mode and, more consistently, with recalcitrance and capacity-loss kinetics over time. Holanda et al. [@Holanda2023] observed that configurations with higher lignin participation tend to exhibit higher initial tensile strength than those with lower L/C; however, this association does not, by itself, imply extended durability, because temporal performance also depends on microstructure, exposure conditions, and surface treatments.

The discrepancy between theoretical chemical recalcitrance and temporal performance reinforces that resistance to biodegradation depends not only on total lignin content but also on its three-dimensional organization in the cell wall, that is, how the aromatic scaffold is distributed relative to cellulose- and hemicellulose-rich regions.

Souza et al. [@Souza2019] demonstrated that lignin distribution is spatially heterogeneous across cell wall layers, concentrating in the middle lamella and cell corners, regions responsible for tissue cohesion. This heterogeneity defines zones of higher and lower enzymatic accessibility, modulating microorganism penetration and preferential crack-initiation locations.

In line with this, Blanchette [@Blanchette1995] describes lignin as a physical barrier to lignocellulolytic enzymes not only due to abundance but due to how it intercalates with cellulose and hemicellulose, which explains why materials with similar lignin contents can display different durabilities under the same exposure regime.

In this perspective, resistance to biological degradation results from the combination of lignin proportion and its three-dimensional distribution in the cell wall; integrated with effective L/C ratio, these parameters define a recalcitrance profile that conditions enzymatic accessibility and the temporal pattern of capacity loss. Carvalho et al. [@Carvalho2014] observed significant mechanical strength reductions under aging and soil exposure at intervals compatible with slope functional periods, showing that specifications based on mean values ignore the stochastic variability of biological materials and the progressive loss of capacity over time.

This deterministic approach tends to become inadequate when coefficients of variation exceed 25% and strength loss does not follow a linear trajectory, a scenario in which mean parameters no longer represent real failure risk.

According to @Curtin2000, Functional Service Life (FSL) can be treated as a probabilistic quantity representing the interval during which 90% of deployed geotextiles maintain load-bearing capacity above a critical threshold. In this formulation, FSL is bounded by the 10th percentile ($P_{10}$) of the Weibull failure distribution, described by

$$
P(t) = 1 - \exp\left[-\left(\frac{t}{\eta}\right)^\beta\right],
$$

where $\eta$ is the scale parameter associated with characteristic life, and $\beta$ describes failure mode. Applying this model to untreated fiber geotextiles yields, for low L/C configurations, $\beta$ values around 2.3 (wear-out failure) and $\eta$ near 68 days, resulting in P₁₀ = 42 days as FSL under field conditions, aligning the mechanical service window with the microbial colonization kinetics described above.

Surface engineering interventions can shift the failure distribution both in terms of reliability (P₁₀, adopted here as FSL) and in terms of characteristic life (the scale parameter, $\eta$). In the analyzed set, alkaline treatment with 6% NaOH is associated with P₁₀ on the order of 95 days, with $\eta$ around 142 days (Table 3). For a monolayer polymeric coating, $\eta$ can reach ~128 days, with P₁₀ on the order of ~92 days (Table 3), values compatible with the critical window for vegetative establishment in slope bioengineering.

Accordingly, chemical architecture, summarized by L/C ratio and lignin organization, combined with surface treatments, influences Weibull parameters used in design, linking microscopic degradation observed by SEM, TGA, and enzymatic analyses to slope-scale structural reliability [@Kaya2023].

### 3.3. Alkaline Mercerization and Polymeric Coatings

Mercerization with sodium hydroxide (NaOH) selectively removes lignin and hemicelluloses, exposing crystalline cellulose microfibrils and reducing fiber surface heterogeneity [@Verma2021]. This chemical–structural reorganization decreases defect density at the fiber–matrix interface, favors inter- and intrafibrillar rearrangement, and increases cellulose stability, yielding direct gains in interfacial adhesion when fibers are incorporated into composites [@Ikramullah2018].

In the dataset analyzed here, this morphostructural restructuring produced a non-monotonic relationship between mechanical resistance and alkaline concentration. Untreated fibers presented mean ultimate tensile strength (UTS) of 18.88 N·mm$^{-2}$, whereas 3% NaOH resulted in 17.62 N·mm$^{-2}$, a difference not statistically significant. The intermediate concentration of 6% NaOH increased UTS to 21.39 N·mm$^{-2}$, a 13.3% increase relative to control, accompanied by increased puncture resistance.

Working with date palm fibers (*Phoenix dactylifera*), Oushabi et al. [@Oushabi2017] reported a 76% increase in tensile strength after 5% NaOH, attributed to removal of non-cellulosic constituents and greater exposure of cellulose microfibrils. Consistent with this evidence, Narayana et al. [@Narayana2021] indicate that intermediate alkaline concentrations selectively remove amorphous lignin and hemicellulose fractions, reduce surface impurities, improve wettability, and enhance interfacial adhesion without compromising cellulose crystallinity, producing a more cohesive fibrous network and more efficient load transfer.

In parallel, recent studies on natural-fiber reinforced composites report mechanical gains and morphological changes, as well as non-linear dependence of performance on loading and treatment [@Kar2024; @Kar2025VNL], which, although not strictly within the geotextile scope, provide convergent support for interpreting that fibrous architecture and surface compatibilization modulate damage mechanisms and performance trajectory [@Aruchamy2024; @Ayrilmis2024; @Palanisamy2024].

At 9% NaOH, although UTS reaches 22.49 N·mm$^{-2}$, there are indications of surface corrosion and possible depolymerization, with greater brittleness and only modest puncture improvement (Table 2). There are reports that high-alkalinity treatments, after an initial phase of structural cleaning and crystalline rearrangement, may also degrade the cellulosic matrix [@Amior2022]. Prolonged exposure to concentrated NaOH solutions can induce alkaline hydrolysis of glycosidic bonds, reduce cellulose degree of polymerization, and compromise fiber structural integrity [@Nurazzi2021].

As observed by Bartos et al. [@Bartos2020], these results converge to an optimal concentration window around 6% NaOH, where the benefits of delignification and hemicellulose removal outweigh the risks of structural damage, improving mechanical performance without excessive loss of ductility.

This balance involves partial lignin removal, which may reduce microbial colonization sites, and preservation of high-degree-of-polymerization cellulose chains, whose degradation would compromise global strength [@Xu2013]. In the 180-day field dataset analyzed here, untreated fibers maintained functionality for ~60 days, whereas 6% NaOH prolonged structural viability to 142 days (FSL of 95 days at Weibull P₁₀ threshold). Under 9% NaOH, structural integrity was preserved with censoring throughout the 180-day period.

An ordinary least squares (OLS) linear model, decomposed by Type-II ANOVA, indicates that exposure time dominates UTS variability, while NaOH treatment and interaction terms retain additional effects, suggesting that surface engineering should be treated as a trajectory-control variable rather than merely an instantaneous strength gain (Figure 9).

**Figure 8.** Comparative scanning electron microscopy (SEM) of *Typha domingensis* and *Syagrus coronata* fibers under different treatments and exposure times.

![Comparative SEM images](../3-IMAGENS/figura_mev_originais.png){width=100%}

*Note. Subfigures (a–d) correspond to *Typha domingensis* (30 d untreated, 180 d untreated, 30 d double resin layer, and 180 d double layer), whereas (e–h) correspond to *Syagrus coronata* under the same conditions; 700× magnification and 100 µm scale bar.*

Morphometric analyses indicate that less recalcitrant fibers present porosity evolution characterized by progressive structural collapse, with initially rough surfaces evolving toward more uniform topographies as degradation products are deposited. This pattern contrasts with more lignified fibers, which exhibit deep grooves and longitudinal channels over time, compatible with degradation oriented by ligninolytic enzymatic complexes.

Polymeric coatings induced complex microstructural reorganization, with maximum porosities at intermediate exposure stages, followed by interfacial delamination under field conditions. Taken together, fracture density and damage severity were consistent with progressive failure driven by surface erosion followed by radial penetration, supporting Weibull distributions with shape parameter β > 1 for probabilistic characterization of durability.

Regarding strain at break (ε), results describe an inverse pattern relative to strength, with maintained elongation at 3% NaOH (2.86%, close to control at 2.95%) and progressive reductions at 6% and 9% NaOH (2.31% and 2.18%), evidencing ductility loss at higher concentrations, consistent with chemical damage accumulation and reduced degree of polymerization under elevated alkalinity [@Ray2002]. In the analyzed set, the 6% NaOH condition represents an operational optimum by balancing tensile strength, puncture resistance, and ductility, with P₁₀ on the order of ~95 days and $\eta$ around ~142 days (Table 3), while keeping ε above 2.3%.

In this context, quantitative morphometry suggests that the observed balance stems from nanometric transformations, with partial transition from cellulose I to cellulose II, increased surface roughness (+48.2%), and higher accessibility of hydroxyl groups [@mansikkamaki2007], yielding a more active surface in terms of interaction and transport.

Concomitantly, mercerization reorganizes the pore network by fusing small pores into cavities with larger mean area (+73.6%), increasing circularity (+5.9%) and reducing dimensional heterogeneity [@Jiao2014], such that total porosity grows moderately (+7.6%) despite a reduction in pore count (−42.1%), improving capillary transport efficiency rather than simply sealing channels [@Koistinen2024].

Whereas mercerization optimizes internal structure, external protection depends on barrier strategies. To quantify the temporal trend observed in Figure 9, simple linear regression was fitted between exposure time (days) and mean UTS (N/mm$^2$), by species and treatment condition (means by exposure time). In *Typha domingensis*, single-layer resin exhibited a steep linear decline between 30–120 days: each additional day of exposure reduced mean UTS by 0.084 N/mm$^2$ (β = −0.084 N/mm$^2$·day$^{-1}$, 95% CI [−0.120, −0.049], p = 0.009, f$^2$ = 53.45, R$^2$ = 0.982). The untreated control showed a weak trend (β = −0.034 N/mm$^2$·day$^{-1}$, 95% CI [−0.161, 0.094], p = 0.377, f$^2$ = 0.64, R$^2$ = 0.389), whereas the double-layer showed a moderate decline over the available interval (β = −0.046 N/mm$^2$·day$^{-1}$, 95% CI [−0.116, 0.025], p = 0.110, f$^2$ = 3.83, R$^2$ = 0.793).

In *Syagrus coronata*, regressions also yielded negative coefficients under resin conditions, but without robust statistical evidence when fitting by time points: untreated (β = −0.214 N/mm$^2$·day$^{-1}$, 95% CI [−1.750, 1.323], p = 0.328, f$^2$ = 3.12, R$^2$ = 0.757), single-layer (β = −0.162 N/mm$^2$·day$^{-1}$, 95% CI [−0.406, 0.083], p = 0.126, f$^2$ = 1.48, R$^2$ = 0.596), and double-layer (β = −0.221 N/mm$^2$·day$^{-1}$, 95% CI [−0.667, 0.224], p = 0.166, f$^2$ = 2.28, R$^2$ = 0.695). This pattern is compatible with a less linear trajectory (rapid initial drop followed by stabilization at low levels) and with gaps at late times, which reduces inferential power when fitting by time points; overall, it reinforces that exposure time governs UTS loss, whereas species and treatment modulate the curve shape (Figure 9).

**Figure 9.** Tensile strength (UTS, N/mm) under different treatment conditions: **(a)** resin coating (untreated/single layer/double layer) for *Typha domingensis* and *Syagrus coronata*; **(b)** alkaline mercerization with NaOH (0%, 3%, 6%, 9%) for *Typha domingensis* and *Syagrus coronata*.

![Figure 6a](../5-DADOS/MEV-ANALISE/resultados_en/fig_tensile_resin_english.png){width=80%}

![Figure 6b](../5-DADOS/MEV-ANALISE/resultados_en/fig_tensile_naoh_english.png){width=80%}

### 3.4. Implications for Specification of Tropical Geotextiles

Consolidating mercerization (NaOH) and resin coating results converts the relationship among L/C ratio, surface engineering, and Weibull parameters into a practical specification tool for natural geotextiles in tropical environments [@Sodagar2025]. As a baseline, the untreated condition presents an FSL (P₁₀) of 42 days, with tensile degradation rate $k = 0.0118$ day$^{-1}$. Treatment with 6% NaOH shifts this boundary to FSL (P₁₀) of ~95 days, with $k = 0.0073$ day$^{-1}$ (Table 3), representing an approximately 38% decrease in degradation rate. For a monolayer coating applied to *Syagrus*, $k = 0.0061$ day$^{-1}$ is observed, with $\eta$ reaching ~128 days and FSL (P₁₀) on the order of ~92 days (Table 3). At higher NaOH concentrations, the set suggests reduced degradation, but interpretation should consider the non-linear dependence of mercerization under elevated alkalinity, which can simultaneously reorganize the amorphous fraction and introduce chemical damage depending on the exposure regime.

These kinetic differences allow aligning treatment choice to the service window and project budget [@Vivek2020]. For works requiring structural support between 90 and 150 days, typical of annual crops and erosion control restricted to the rainy season, 6% NaOH provides a favorable combination of FSL (95 days at P₁₀) and low direct cost, without additional removal or disposal costs.

For perennial scenarios such as riverbank restoration or highway slope stabilization, single-layer resin, despite higher unit cost, becomes competitive because increasing characteristic life (to $\eta$ on the order of ~128 days, with FSL/P₁₀ on the order of ~92 days; Table 3) and improving reliability may compensate the initial investment. The double-layer configuration remains inadvisable under the evaluated conditions, because marginal gains in initial strength are accompanied by early delamination, moisture accumulation, and abrupt performance decline, illustrating how barrier oversizing can induce systemic failure rather than mitigate it.

Puncture resistance (ISO 12236) [@ISO12236] is critical for geotextile integrity on irregular substrates [@Cholewa2019]. NaOH-treated *Typha* maintained >25 N·mm$^{-2}$ for 120 days, exceeding equivalent geosynthetics (~18 N·mm$^{-2}$) due to stress redistribution by the fibrous mesh. Degradation follows a power law ($R_p \propto t^{-0.16}$), with maximum protection from alkaline treatment between 30–90 days, a vital interval for vegetation establishment [@Kumar2016]. Moderate treatments (6% NaOH) preserve ductility ($\epsilon \approx 2.3–2.9\%$), essential to absorb dynamic impacts on steep slopes, offering a robust compromise between strength gain (+13%) and operational deformability, superior to the embrittlement induced by higher concentrations (9%) [@Vivek2019].

## 4. Conceptual Framework of Reliability and Environmental Performance

The intrinsic variability of natural geotextiles supports stochastic modeling of performance decay. In this context, the Weibull distribution ($R(t) = e^{-(t/\eta)^\beta}$) represents structural heterogeneity, in which $\beta > 1$ (1.8–4.2) is associated with progressive wear-out failure (fatigue/hydrolysis), in contrast with approximately random failure ($\beta \approx 1$).

Moreover, surface engineering tends to increase $\beta$ (reducing variability) and $\eta$, extending service life [@Luqman2023]. Defined as the time to 10% failure (P₁₀), Functional Service Life can increase from 42 days (untreated *Typha*) to 95 days (6% NaOH) and 128 days (resin-coated *Syagrus*), covering the critical ~90-day window for vegetative anchorage.

As previously shown in Figure 8, SEM images document the temporal progression of surface degradation in both species. In *Typha domingensis*, surface porosity varied from 32.75% (ST 30d) to 73.09% (DC 30d), with non-monotonic behavior: an increase from 32.75% to 67.27% under tropical soil exposure (ST 30d → ST 180d), but a reduction from 73.09% to 68.49% under controlled degradation (DC 30d → DC 180d). Surface roughness showed the inverse pattern, peaking at 30 days (941.64 µm in ST; 581.04 µm in DC) and decreasing at 180 days (724.26 µm in ST; 528.27 µm in DC).

This pattern, high initial roughness followed by reduction, is consistent with an initial stage dominated by superficial damage and erosion/removal of more accessible material, followed by topographic reorganization associated with degradation advance and deposition/removal of products on the surface.

Accordingly, this interpretation is presented as a trend rather than a unique mechanism, because degradation pathways can alternate between surface erosion and radial penetration in lignocellulosic matrices, as described in Section 3.2. Fiber density varied from 25.41% (ST 30d) to 34.80% (DC 180d), reflecting progressive exposure of cellulose microfibrils as lignin/hemicellulose matrices degrade [@Singh2022].

In *Syagrus coronata*, progression was more gradual, with porosity increasing from 50.07% (ST 30d) to 63.77% (ST 180d), while roughness increased from 679.35 µm (ST 30d) to a maximum of 1012.67 µm (ST 180d) and 1174.66 µm (DC 30d), indicating formation of deep grooves under oriented degradation. Fiber density remained stable (30.50% to 33.24%), compatible with degradation progressing from surface to core under diffusional constraints on enzymes and more intense photo-chemical exposure at the periphery.

**Figure 11.** Quantitative analysis of fractures and damage severity by image processing with skeletonization: **(a)** *Typha* 30 days untreated, **(b)** *Typha* 180 days untreated, **(c)** *Typha* 30 days double layer, **(d)** *Typha* 180 days double layer, **(e)** *Syagrus* 30 days untreated, **(f)** *Syagrus* 180 days untreated, **(g)** *Syagrus* 30 days double layer, **(h)** *Syagrus* 180 days double layer.

![Figure 11](../3-IMAGENS/figura_analise_fraturas.png){width=100%}

*Note. The triple overlay combines the base grayscale image (α = 0.7), open-fracture regions detected by thresholding (values <50 gray levels) in red (α = 0.4), and the fracture skeleton in hot colormap (α = 0.6).*

Morphometric quantification of fractures revealed distinct dynamics between species. In *Typha domingensis*, under tropical soil exposure (ST), fracture counts varied from 237 (ST 30d) to 229 (ST 180d, stabilization of ~−3%), whereas under controlled degradation (DC) they decreased from 139 to 75 (−46%), suggesting that field exposure with variable hygrothermal cycles promotes more heterogeneous damage accumulation than controlled laboratory conditions [@Nezafatkhah2025_weathering_review]. Severity remained critical across all conditions (103.43–121.25%), consistent, within the analyzed set, with intense structural degradation throughout the exposure period [@Voyiadjis2007_microcrack_tensor].

In *Syagrus coronata*, field trajectory was more abrupt. Under ST, fractures increased from 47 (30d) to 211 (180d, +349%), with maximum severity of 126.25%, a pattern compatible with higher initial integrity followed by intensified damage when environmental conditions favor crack progression. Under DC, behavior was nearly stationary (45 → 43 fractures; ~−4%, severity ~103%), which may indicate that under uniform laboratory conditions the morphometric evolution of damage was substantially less pronounced within the analyzed interval.

Severity classification, operationalized by percentage damage thresholds (Mild <0.5%; Moderate 0.5–2%; Severe 2–5%; Critical >5%), places all species × treatment × time combinations within the critical domain, such that relevant differentiation lies in the kinetics of damage accumulation.

In this framework, Weibull interpretation is useful because the shape parameter $\beta$ governs the time evolution of the failure rate; $\beta>1$ implies increasing hazard and is typically associated with progressive wear [@Guo2014_palm_weibull], whereas $\beta\approx 1$ would be compatible with approximately random failures dominated by intrinsic defects. Therefore, the estimated $\beta$ values (2.3–4.2) are consistent with an accumulative damage regime.

In the analyzed dataset, the functional threshold P₁₀ typically occurred when fracture densities were already on the order of 10$^2$ fractures·field$^{-1}$, consistent with an increasing hazard regime ($\beta>1$) [@Wang2014_bamboo_weibull] and with interpreting FSL as a probabilistic quantity associated with accumulated capacity loss.

Fiber density remained relatively stable (28.75–36.10%) over exposure, indicating degradation predominantly from surface to core, compatible with diffusional enzyme limitations and higher photo-chemical exposure at the periphery [@Tian2018_hygrothermal], whereas Brunsek et al. [@Brunsek2023] quantify that cellulase activity in complex media such as soils is associated with degradation progression rate.

The correlation between fracture count and exposure time (R$^2$ = 0.76; p < 0.01) suggests good descriptive capacity of the model $\sigma(t) = \sigma_0 \cdot \exp[-k \cdot t]$ to estimate functional service life [@Datta2024]. Notably, *Syagrus* exhibited lower initial fracture density (47 vs 237 in *Typha* at 30d under ST). This aligns with the hypothesis that higher L/C ratio (0.67 vs 0.46) can retard degradation kinetics [@Grgas2023], whereas the contrast between ST (211 fractures at 180d) and DC (43 fractures) indicates that natural moisture and temperature cycles amplify damage propagation.

Despite damage progression under all conditions, results support strategic advantages of lignocellulosic fibers in temporary geotechnical applications. Statistical predictability of degradation (R$^2$ = 0.76; p < 0.01), anchored in parameters $k$, $\beta$, $\eta$, and P₁₀, enables controlled life-cycle engineering in which geotextiles carry structural function during the critical vegetative establishment period (90–150 days) and subsequently biodegrade, reducing post-service removal needs and mitigating long-term environmental impacts [@Prambauer2019].

In contrast with multi-decadal geosynthetics, whose weathering and abrasion can generate microplastic fragments and redistribute them through the soil–water system, lignocellulosic geotextiles tend to present progressive mass loss and mechanical capacity decay on the timescale of months to a few years, with kinetics sensitive to chemical architecture and exposure regime (moisture, temperature, radiation), which allows treating degradation as a design attribute, provided temporal reliability is explicitly modeled [@Zambrano2020].

Observed initial mechanical performance (UTS = 18–24 MPa at 30 days; Weibull modulus $m = 4.2$–5.8) should be interpreted as a function of loading scenario and design horizon, consistent with the concept of limited-life geotextiles and with the need to specify by temporal reliability rather than relying on single resistance thresholds [@Methacanon2010].

The operational window frequently required in erosion control and temporary stabilization, on the order of 120–150 days, has been associated with the interval in which pioneer vegetation establishes a functional root system in 60–90 days (Table 3) and gradually assumes the stabilizing function [@Gray1996]; however, extrapolation of this window to a specific sectoral fraction depends on systematic surveys and is therefore not adopted here.

In this framework, FSL ceases to be a fixed attribute and becomes a design variable, insofar as L/C ratio tends to shift degradation kinetics and thus the performance window, such that lower L/C ranges (≈0.35–0.45) are, on average, associated with shorter service regimes than higher ranges (≈0.50–0.65), without implying determinism because response depends on anatomical fraction, microstructure, and exposure regime [@Vikman2002].

**Table 3.** Synthesis of the L/C → $k$ → Weibull parameters (β, η, P₁₀) → FSL linkage across species and treatment conditions.

| Species/Treatment | β (shape) | η (scale, days) | P₁₀ (days) | k (rate, day$^{-1}$) | Failure mechanism |
| --- | :---: | :---: | :---: | :---: | --- |
| *Typha* untreated (control) | 2.3 | 68 | 42 | 0.0118 | Enzymatic hydrolysis + UV |
| *Typha* + NaOH 6% | 2.8 | 142 | 95 | 0.0073 | Retarded degradation via surface reorganization |
| *Typha* + NaOH 9% | 3.1 | 155 | 108 | 0.0062 | Reduced degradation, onset of embrittlement |
| *Syagrus* untreated (control) | 2.1 | 95 | 55 | 0.0095 | Slow hydrolysis (high lignin) |
| *Syagrus* + single-layer resin | 3.2 | 128 | 92 | 0.0061 | Effective interfacial protection |
| *Typha*–Ramie composite (UV aging) | 3.8 | 140 | 105 | 0.0052 | Photodegradation-driven aging |

**Legend.** β is the Weibull shape parameter; when β > 1 it is compatible with progressive wear-out failure, whereas β → 1 is compatible with approximately random failure; η is the scale parameter associated with characteristic life at 63.2% failure; P₁₀ is the time to 10% probability of failure (i.e., functional service life with 90% reliability); and k is the strength degradation rate.

Accordingly, integrating Weibull reliability metrics (FSL) with linear models and microstructural evidence from SEM supports an interpretive chain L/C → $k$ → β, η, P₁₀ → FSL and brings natural geotextiles closer to standards such as ASTM D4595 and the ISO 10318 series [@Franco2022]. This approach enables estimating variability and functional service life from accelerated aging tests and modeling adjusted to different climatic regimes.

Recent studies indicate the utility of Weibull modeling in quantifying mechanical reliability [@Wang2022] and of probabilistic modeling in forecasting degradation and failure in composites [@Bogdanov2023], offering a quantitative and reproducible framework for certification and quality control of lignocellulosic materials.

As an operational synthesis, strength loss can be treated as a time-dependent decay governed by an effective rate $k$, while site-specific exposure effects (e.g., moisture and radiation) can be incorporated as correction factors when sufficient calibration data are available. This maintains traceability between estimated parameters ($k$, $\beta$, $\eta$, P$_{10}$) and the exposure regime, avoiding fixed universal coefficients for environmental components without explicit calibration within the analyzed dataset.



## 5. Conclusions

This review synthesizes evidence that the chemical architecture of lignocellulosic fibers is among the factors most frequently associated with biodegradation kinetics in natural geotextiles. The inverse relationship between lignin/cellulose ratio and degradation rate is, in general, consistent with using biochemical characterization as a predictive tool in raw material selection, supporting screening of plant species by intrinsic recalcitrance and reducing reliance on long-duration field trials.

Redefining Functional Service Life (FSL) under a probabilistic perspective, grounded in the Weibull distribution, can be interpreted as a methodological advance over traditional deterministic approaches. By quantifying temporal reliability, this structure enables incorporating safety factors more transparently in bioengineering design, bringing natural fibers closer to standard geotechnical engineering practice.

Surface modification strategies indicate that optimizing mechanical performance and durability is not linear. Moderate alkaline treatments can promote structural gains without compromising flexibility, whereas polymeric coatings require balancing hydrophobicity and permeability to reduce delamination-driven failure. Cost-effectiveness considerations indicate that low-cost interventions can extend service life, making natural geotextiles competitive against synthetics in temporary applications.

Beyond mechanical reinforcement, lignocellulosic geotextiles can contribute to ecological restoration, supporting ecosystem services that extend beyond soil stabilization. With programmed fiber decomposition, there may be contributions to carbon sequestration, soil structure improvement, and increased edaphic biodiversity. In turn, synchronizing loss of geotextile strength with vegetation root-system development tends to favor a gradual transition from artificial stabilization to natural cohesion.

## References

::: {#refs}
:::
