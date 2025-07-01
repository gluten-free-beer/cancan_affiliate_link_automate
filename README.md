# Automate Affiliate Link Conversion with CANDY

This is a simple script to batch process CANDY files and automate the workflow that converts affiliate links. Using Selenium driver, it will generate a json file with contents like:
```
{boid: 'https://***$$$'}
```

ℹ️ This script is intended for use by marketers and influencers. Improper use may lead to unintended consequences and is not supported. Please comply with regulations and refrain from using this facilitative tool to abuse or game any system.

### Supported platforms
- Amazon
- Aliexpress (coming soon)

### Workflow
- Put CANDY files in the "resources" folder. Both .json and .csv files are accepted.
- Call main.py and follow the prompts in the terminal. For the first time, you will need to log in. By default, Chrome browser is used.
- The generated links will be saved to ./output. Note that the output files will have the same filenames as the resource files, which makes them incremental. Delete the output files or supply --reset=1 for a fresh start. 
