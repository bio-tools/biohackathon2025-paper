---
title: 'Bidirectional bridge: GitHub $\rightleftarrows$ bio.tools'
tags:
  - GitHub
  - bio.tools
  - software metadata
authors:
  - name: Mariia Steeghs-Turchina
    orcid: 0000-0002-0852-4752
    affiliation: 1
  - name: Anna Niehues
    orcid: 0000-0002-9839-5439
    affiliation: 1
  - name: Ana Mendes
    orcid: 0009-0008-5170-0927
    affiliation: 2
  - name: Erik Jaaniso
    orcid: 0009-0003-4246-6546
    affiliation: 3
  - name: Ove Johan Ragnar Gustafsson
    orcid: 0000-0002-2977-5032
    affiliation: 4
  - name: Walter Baccinelli
    orcid: 0000-0001-8888-4792
    affiliation: 5
  - name: Vedran Kasalica
    orcid: 0000-0002-0097-1056
    affiliation: 5
  - name: Sam Cox
    orcid: 0000-0002-9841-9816
    affiliation: 6
  - name: Ivan Topolsky
    orcid: 0000-0002-7561-0810
    affiliation: 7
  - name: Magnus Palmblad
    orcid: 0000-0002-5865-8994
    affiliation: 1
  - name: Veit Schwämmle
    orcid: 0000-0002-9708-6722
    affiliation: 2
affiliations:
 - name: Leiden University Medical Center, Albinusdreef 2, 2333 ZA, Leiden, The Netherlands
   index: 1
   ror: 05xvt9f17
 - name: University of Southern Denmark, Campusvej 55, 5230, Odense, Denmark
   index: 2
   ror: 03yrrjy16
 - name: Institute of Computer Science, University of Tartu, Narva mnt 18, 51009 Tartu, Estonia
   index: 3
   ror: 03z77qz90
 - name: Australian BioCommons, University of Melbourne, 21 Bedford St, North Melbourne, Victoria, Australia
   index: 4
   ror: 01ej9dk98
 - name: Health-RI, Jaarbeursplein 6, 3521 AL, Utrecht, The Netherlands
   index: 5
   ror: 02xcmp898
 - name: Health Data Research UK, London, UK
   index: 6
   ror: 04rtjaj74
 - name: Computational Biology Group, SIB Swiss Institute of Bioinformatics, Mattenstrasse 26, 4058 Basel, Switzerland
   index: 7
   ror: 002n09z45
date: 04 November 2025
bibliography: paper.bib
authors_short: 'Steeghs-Turchina et al. (2025) Bidirectional bridge: GitHub $\rightleftarrows$ bio.tools'
group: BioHackrXiv
event: BioHackathon Europe 2025
biohackathon_name: "BioHackathon Europe 2025"
biohackathon_url:   "https://biohackathon-europe.org/"
biohackathon_location: "Berlin, Germany, 2025"
git_url: "https://github.com/bio-tools/biohackathon2025-paper"
---


# Abstract

Research software metadata can be found across many code repositories and software registries. Here, we describe the tooling for a bidirectional bridge between the software development platform GitHub and the ELIXIR bio.tools registry of life sciences software tools and data resources. The developed bridge maps and improves metadata records across these two platforms, thereby benefitting both and helping make the research software more FAIR: findable, accessible, interoperable, and reusable. Specifically, the bridge enables production of high-quality, rich bio.tools entries from the content already available in GitHub repositories, and uses bio.tools records to suggest improvements to GitHub repositories through pull requests or issues. This includes adding missing information and standardized descriptions for increased compliance with Software Management Plans. The bidirectional bridge makes extensive use of existing APIs (GitHub, bio.tools, Europe PMC) and large language models (LLMs) to enrich metadata on both platforms. By automating metadata extraction, improvement suggestion, and integration, the bridge reduces the manual overhead required to FAIRify research software, lowering barriers for researchers to contribute or maintain well-annotated, reusable software.


# Introduction

[bio.tools](https://bio.tools/) [@Ison2016;@Ison2019] is a curated registry designed to support the discovery, annotation, and interoperability of bioinformatics software and databases. By offering persistent identifiers, bio.tools enhances the findability and reusability of computational resources in line with FAIR principles [@Wilkinson2016;@Barker2022]. The registry also offers the opportunity to add rich and standardized metadata to entries, including EDAM ontology concepts [@Ison2013][@Lamothe2022]. A given registry entry can therefore describe general information (e.g. software name, homepage), contextual metadata (e.g. topic area, publications), software functions (i.e. operations), inputs, and outputs. To ensure semantic consistency and machine readability this metadata follows its own schema: *biotoolsSchema* [Ison2021]. <br>
The platform serves as a community-driven "hub" that links software curators, developers and users with repositories and complementary infrastructures such as Galaxy [@GalaxyCommunity2024], OpenEBench [@Capella-Gutierrez2017], and WorkflowHub [@Gustafsson2025]. Through these functions, bio.tools acts as a central resource for organizing and connecting the bioinformatics software ecosystem, promoting transparency, interoperability, and sustainable reuse in the life sciences.


[GitHub](https://github.com/) is the leading repository and platform for collaborative software development and version control, hosting almost 400 million public, open source, software repositories [@GitHubStaff2025]. Built on version control by Git, it provides transparent tracking of code development, simultaneously enhancing reproducibility and accountability in collaborative scientific enterprises. GitHub also serves as a socio-technical infrastructure, in that its features support collaboration, documentation, dissemination, and maintenance of research software [@Braga2022;@Chen2025]. <br> 
GitHub provides a number of features useful to collaborative research software development, such as pull requests (*for contributing to projects*), issues (*for communication around specific features or bugs*), and discussion threads (*for general communication*). By hosting public repositories, GitHub promotes FAIR research software [@Barker2022;@DelPico2024] and in combination with open licenses can provide open access to source code, documentation, and even data. Integration with scholarly tools, such as [Zenodo](https://zenodo.org/), [Open Science Framework (OSF)](https://osf.io/), or [Software Heritage](https://www.softwareheritage.org/) [@dicosmo2017], as well as continuous integration systems, further embeds software into open science practices, while GitHub's accessibility and community norms support both training and capacity building in reproducible research methods. Collectively, these features position GitHub as a cornerstone platform for open, transparent, and sustainable research software development across disciplines.


As a registry, bio.tools makes software more FAIR by supporting a faithful representation of the development repository (i.e., GitHub) and providing opportunities to further enrich and build upon the contextual information available for software. <br> Herein, we describe the construction and implementation of a bidirectional bridge framework that allows for synchronisation between GitHub software repositories and their respective bio.tools entries. This project in part builds on previous work [@Szmigiel2025] and addresses key barriers to maintaining software metadata and supports FAIR practices by embedding curation directly into existing workflows. By automating metadata extraction, suggestion, and integration the bridge reduces the manual overhead required to FAIRify research software, and lowers the barrier for contributing well-annotated, reusable tools.


# Elements of the bidirectional bridge


## GitHub $\rightarrow$ bio.tools

The bridge uses the GitHub API to extract and distil metadata (i.e. tool name, programming languages, license, publications) from a set of example repositories and produces a bio.tools-compatible metadata file that can enrich bio.tools entries (see **Figure 1**). This approach is beneficial because it semi-automates the update of a registry entry, including the addition of rich metadata, and simultaneously reduces the maintenance burden for RSEs while streamlining the path to FAIR software.


## bio.tools $\rightarrow$ GitHub

The bridge also uses bio.tools entry metadata to automatically suggest enhancements to GitHub repositories via issues and pull requests (*where possible*). This approach is beneficial because it allows curated entry information from bio.tools to enrich the original source repository for software, adding missing metadata where needed.


![High level design of the project](assets/bidirectional_bridge_diagram.png)


# Results


## Repository & registry statistics

At the end of the BioHackathon week (November 7, 2025), there were 30,608 resources described in bio.tools. Of these, 13,774 or 45.0% entries had at least one GitHub URL. Of these, 13,391 (or 97.2% of all entries with GitHub URLs) pointed to a valid public GitHub repository. From these GitHub repositories, XX,XXX descriptions, XX,XXX GitHub topics, XX,XXX licenses, XX,XXX README.md files, X,XXX CITATION.cff files and XXX,XXX quantitative metrics related to maturity were fetched from GitHub.


According to the GitHub “Octoverse 2025” report, there were approximately 395 million public and open-source repositories in GitHub in October 2025. The share of GitHub repositories covered by bio.tools is thus vanishingly small (see **Figure 2**). Even for a scientific topic such as "machine learning", there are 166,684 GitHub repos matching the GitHub topic, compared to 3,421 tools in bio.tools with the corresponding EDAM topic.


![Venn diagram of bio.tools and GitHub, with the intersect representing bio.tools entries with at least one valid GitHub URL.](assets/venn_github_biotools_truncated.svg)


## Metadata maturity

The correlation between software metadata in GitHub and bio.tools maturity level is rather poor. The principal component analysis (PCA) in **Figure 3** illustrates the relationship between maturity-related metrics in GitHub and the 'maturity' in the corresponding bio.tools entry. All of these GitHub metrics are highly correlated. For example, a project with more contributors and subscribers is also likely to have more forks, commits, and pulls: this is not surprising. <br>
While there is some separation between 'Emerging' and 'Mature' tools, the main suggestion from these results is that a fair number of 'Emerging' tools should probably be updated to 'Mature'. The first principal component has nearly equal loadings for all metrics, where as the second seizes on the average time to close issues and number of contributors. <br>
Of all bio.tools entries 611 are labeled as 'Emerging', 3,532 as 'Mature' and 120 as 'Legacy', with 26,345 having no indicated maturity level. Out of the bio.tools entries with valid GitHub repos, 1,386 tools are labeled as 'Mature', 339 as 'Emerging' and 18 as 'Legacy'.

![Principal component analysis (PCA) of bio.tools entries with a GitHub repo based on the numbers of contributors, forks (and network count), commits, pulls, releases, open issues, subscribers, watchers, stargazers, and the average time to close issues. The colors represent the bio.tools 'maturity' level, i.e. 'Emerging', 'Mature' or 'Legacy'.](assets/PCA.svg)


## Implementation of bridge framework



# Discussion and/or Conclusion

While the main goals of this hackathon project was to establish a bidirectional bridge for transporting (or translating?)software metadata from GitHub to bio.tools and vice versa, a number of insights were inevitably gained in the process, for example on the quality and completeness of the metadata in both platforms. A number of challenges were also observed to be harder than expected, such as transferring multiple topics from bio.tools to GitHub.


# Future work

The bidirectional bridge connects a commonly used software development platform (GitHub) with the life sciences tool registry bio.tools. The underlying framework of the bridge has been designed following a modular and scalable approach. This will enable connecting other development platform or registries in the future by adding respective metadata schema mappings. Other extension possibilities include language or framework (e.g., bioconda, Bioconductor) specific mappings. As both platforms evolve independently, it will also be important to regularly and automatically test that the bridge is still traversible.


# GitHub repository and data repositories

* GitHub repository: https://github.com/bio-tools/biohackathon2025


# Acknowledgements

The authors acknowledge the ELIXIR and all organizers and participants of ELIXIR BioHackathon Europe 2025 in Berlin, Germany, for helping make this project a success. We particularly thank those participants who contributed their GitHub repositories or bio.tools entries for testing of the biodirectional GitHub $\rightleftarrows$ bio.tools bridge.


# References
