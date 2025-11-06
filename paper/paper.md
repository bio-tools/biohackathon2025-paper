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
 - name: Health-RI, Jaarbeursplein 6, 3521 AL,  Utrecht, The Netherlands
   index: 5
   ror: 02xcmp898
 - name: Health Data Research UK, London, UK
   index: 6
   ror: 04rtjaj74
 - name: Institution 1, address, city, country
   index: 7
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

Research software metadata can be found across many code repositories and software registries. Here, we describe the tooling for a bidirectional bridge between the software development platform GitHub and the ELIXIR bio.tools registry of life sciences software tools and data resources. The developed bridge maps and improves metadata records across these two platforms, thereby benefitting both and helping make the research software more FAIR. Specifically, the tooling enables production of high-quality, rich bio.tools entries from the content already available in GitHub repositories, and using bio.tools records to suggest improvements to GitHub repositories through pull requests or issues, including adding missing information and standardized descriptions for increased compliance with Software Management Plans. The bidirectional bridge makes extensive use of existing APIs (GitHub, bio.tools, Europe PMC) and LLMs to enrich metadata in both platforms. By automating metadata extraction, improvement suggestion, and integration, the tooling reduces the manual overhead required to FAIRify research software, lowering barriers for researchers to contribute or maintain well-annotated, reusable software.

# Introduction

bio.tools [@Ison2016;@Ison2019] is a curated registry designed to support the discovery, annotation, and interoperability of bioinformatics software and databases. By offering persistent identifiers, bio.tools enhances the findability and reusability of computational resources in line with FAIR principles [@Wilkinson2016;@Barker2022]. To ensure semantic consistency and machine readability, the registry also allows for the addition of rich and standardized metadata that follows its own schema (i.e., *biotoolsSchema* [Ison2021]) and leverages the EDAM ontology [@Ison2013]. This allows a given registry entry to describe general information (e.g., software name, homepage), contextual metadata (e.g., topic area, publications), software functions (i.e., operations), inputs, and outputs.
The platform serves as a community-driven hub that links software curators, developers and users with repositories and complementary infrastructures such as Galaxy [@GalaxyCommunity2024], OpenEBench [@Capella-Gutierrez2017], and WorkflowHub [@Gustafsson2025]. Through these functions, bio.tools acts as a central resource for organizing and connecting the bioinformatics software ecosystem, promoting transparency, interoperability, and sustainable reuse in the life sciences.


GitHub is the leading platform for collaborative software development and version control, hosting almost 400 million public, open source, software repositories [@GitHubStaff2025], and serving as a socio-technical infrastructure for the collaborative development, dissemination, and maintenance of research software [@Braga2022;@Chen2025]. Built on version control by Git, it provides transparent tracking of code development, simultaneously enhancing reproducibility and accountability in collaborative scientific enterprises. GitHub provides a number of features useful to collaborative research software development, such as pull requests (for contributing to projects), issues (for communication around specific features or bugs), and discussion threads (for general communication). By hosting public repositories, GitHub promotes FAIR research software [@Barker2022;@DelPico2024] and open access to source code, documentation, and even data. Integration with scholarly tools, such as Zenodo, OSF, or Software Heritage, and continuous integration systems further embeds software into open science practices, while its accessibility and community norms support training and capacity building in reproducible research methods. Collectively, these features position GitHub as a cornerstone platform for open, transparent, and sustainable research software development across disciplines.


As a registry, bio.tools makes software more FAIR by supporting a faithful representation of the development repository (i.e., GitHub), and providing opportunities to further enrich and build upon the information available for software. Herein, we describe the construction and implementation of a bidirectional bridge framework that allows for synchronisation between GitHub software repositories and their respective bio.tools entries. This project therefore addresses key barriers to maintaining software metadata and supports FAIR practices by embedding curation directly into existing workflows. By automating metadata extraction, suggestion, and integration, the bridge reduces the manual overhead required to FAIRify research software, and lowers the barrier for contributing well-annotated, reusable tools.


Please separate paragraphs with a double line.


## Elements of the bidirectional bridge


## GitHub $\rightarrow$ bio.tools

The bridge uses the GitHub API to extract and distil metadata (i.e. tool name, programming languages, license, publications) from a set of example repositories and produces a bio.tools-compatible metadata file that can enrich bio.tools entries. This approach is beneficial because it semi-automates the update of a registry entry, including the addition of rich metadata, and simultaneously reduces the maintenance burden for RSEs while streamlining the path to FAIR software.


## bio.tools $\rightarrow$ GitHub

The bridge also uses bio.tools entry metadata to automatically suggest enhancements to GitHub repositories via issues and pull requests (*where possible*). This approach is beneficial because it allows curated entry information from bio.tools to enrich the original source repository for software, adding missing metadata where needed.


## Subsection level 2

Please keep sections to a maximum of three levels, even better if only two levels.

### Subsection level 3

Please keep sections to a maximum of three levels.

## Tables, figures and so on

Please remember to introduce tables (see Table 1) before they appear on the document. We recommend to center tables, formulas and figure but not the corresponding captions. Feel free to modify the table style as it better suits to your data.

Table 1
| Header 1 | Header 2 |
| -------- | -------- |
| item 1 | item 2 |
| item 3 | item 4 |

Remember to introduce figures (see Figure 1) before they appear on the document. 
 
Figure 1. A figure corresponding to the logo of our BioHackrXiv preprint.

# Other main section on your manuscript level 1

Feel free to use numbered lists or bullet points as you need.
* Item 1
* Item 2

Figure 1 below illustrate the relationship between maturity-related metrics in GitHub and the 'maturity' in the corresponding bio.tools entry. All of these GitHub metrics are highly correlated, e.g. a project with more contributors and subscribers are also likely to have more forks, commits and pulls. This is not surprising. While there is some separation between 'Emerging' and 'Mature' tools, the main suggestion from these results is that a fair number of 'Emerging' tools should probably be annotated as 'Mature' by now. The first principal components has nearly equal loadings for all metrics, where as the second seizes on the average time to close issues and number of contributors.

![Principal component analysis (PCA) of bio.tools entries with a GitHub repo based on the numbers of contributors, forks (and network count), commits, pulls, releases, open issues, subscribers, watchers, stargazers, and the average time to close issues. The colors represent the bio.tools 'maturity' level, i.e. 'Emerging', 'Mature' or 'Legacy'.](PCA.svg)

# The PCA figure could be shrunk to one panel in a 4-panel figure with additional statistics and results.
# We could add a Venn diagram of tools bio.tools, GitHub repos and the intersect?
# According to the GitHub “Octoverse 2025” report, there are approximately 395 million public and open-source repositories
# 

# Discussion and/or Conclusion

We recommend to include some discussion or conclusion about your work. Feel free to modify the section title as it fits better to your manuscript.

# Future work

The bidirectional bridge connects a commonly used software development platform (GitHub) with the life sciences tool registry bio.tools. The underlying framework of the bridge has been designed following a modular and scalable approach. This will enable connecting other development platform or registries in the future by adding respective metadata schema mappings. Other extension possibilities include language or framework (e.g., bioconda, Bioconductor) specific mappings.

And maybe you want to add a sentence or two on how you plan to continue. Please keep reading to learn about citations and references.

For citations of references, we prefer the use of parenthesis, last name and year. If you use a citation manager, Elsevier – Harvard or American Psychological Association (APA) will work. If you are referencing web pages, software or so, please do so in the same way. Whenever possible, add authors and year. We have included a couple of citations along this document for you to get the idea. Please remember to always add DOI whenever available, if not possible, please provide alternative URLs. You will end up with an alphabetical order list by authors’ last name.

# Jupyter notebooks, GitHub repositories and data repositories

* GitHub repository: https://github.com/bio-tools/biohackathon2025


* Please add a list here
* Make sure you let us know which of these correspond to Jupyter notebooks. Although not supported yet, we plan to add features for them
* And remember, software and data need a license for them to be used by others, no license means no clear rules so nobody could legally use a non-licensed research object, whatever that object is

# Acknowledgements

The authors acknowledge the ELIXIR and all organizers and participants of ELIXIR BioHackathon Europe 2025 in Berlin, Germany, for helping make this project a success. We particularly thank those participants who contributed their GitHub repositories or bio.tools entries for testing of the biodirectional GitHub $\rightleftarrows$ bio.tools bridge.


# References
