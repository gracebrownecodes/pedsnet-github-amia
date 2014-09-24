# Development of PEDSNet Data Extraction Code Using GitHub
### Abstract and supporting code for an AMIA 2015 submission

#### Output Files:
- The data retrieved from GitHub, plus custom activity data, in json format as `raw_data.json`
- GitHub activity summary data by repository as `repo_summary_data.csv`
- The organization-wide weekly github activity data used to create the figure as `org_weekly_data.csv`
- The correlations between variables shown in the figure as `corr_matrix.csv`
- The figure used in the abstract as `activity_fig.png`
- The latest version of the abstract as `abstract.md`, `abstract.docx` and `abstract.pdf`

#### Script Files:
- A python script that retrieves data from GitHub, adds some custom activity statistics, and generates the first three output files as `retrieve_data.py`
- An R script that analyzes the retrieved data from `org_weekly_data.csv` and generates the fourth and fifth output files as `analyze_data.R`
- A convenient bash script for installing python dependencies and running both scripts as `run.sh` 

#### Running the Analysis:
- Requirements:
    - Tested on Python 2.7.7, probably compatible with Python versions > 2.4 and < 3
    - Tested on R version 3.1.1, compatibility with other versions not estimated
- Copy `.config.json.sample` to `.config.json`, add either username and password or token to the auth object, and define a GitHub organization for which you want to run the analysis
- The next step will overwrite the output files, so move them if you want to save them
- Source `run.sh` (a python virtualenv is suggested since python dependencies will be installed)
- The output files here have been manually de-identified by removing site-specific repositories' names and contributors' names, but this identifying data will be output by the scripts when the analysis is re-run
- The averages and standard deviations in the `org_weekly_data.csv` file as well as the average age and total lines calculations in the `repo_summary_data.csv` where added manually using MS Excel, so those data will not be automatically generated when the analysis is re-run
