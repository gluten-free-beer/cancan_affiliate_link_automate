# Automate Affiliate Link Conversion for CANDY

This is a simple script to batch process CANDY files (Licorice, Taffy, Mint, etc.) and automate the workflow that converts canonical product URLs to affiliate links. Using Selenium driver, it will generate a json file with contents like:
```
{"brm1spnz43acb4f16648": "https://amzn.to/44HXXXX"}
```

ℹ️ This script is made for professional use by marketers and influencers. Improper use may lead to unintended consequences and is not supported. Please comply with regulations and refrain from using this facilitative tool to abuse or game any system.

### Supported platforms
- Amazon
- Aliexpress
- Gumroad

### Workflow
- Put CANDY files in the "resources" folder. Both .json and .csv files are accepted.
- Call main.py and follow the prompts in the terminal. For the first time or for some specific platforms, you will need to log in. By default, Chrome browser is used.
- The generated links will be saved to ./output. Note that the output files will have the same filenames as the resource files, which makes them incremental. Delete the output files or supply --reset=1 for a fresh start.
- Use the .env file for configuration.