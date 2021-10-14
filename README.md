# Wiki Template I/O

This repository contains helper scripts for [AutoWikiBrowser](https://en.wikipedia.org/wiki/Wikipedia:AutoWikiBrowser) to automatically push/pull templates to/from a wiki.

## Setup

1. Download and setup AutoWikiBrowser according to the [official instructions](https://en.wikipedia.org/wiki/Wikipedia:AutoWikiBrowser#(2)_Download).
2. Clone this repository anywhere on the same machine.
3. Install Python 3.6.2 or above, then run the following command to download required packages:
   ```
   python -m pip install -r requirements.txt
   ```

## Usage

### Pulling from wiki to Excel

1. Find the name of the template you want to process (without prefix and suffix).
2. Open AutoWikiBrowser and log in your account.
3. Use the `Make List` feature to select the pages you wish to import from. For convenience, it is recommended that you use a system to group all pages that contain the template so that you could generate the list of pages automatically.
4. Select `Tools > External Processing`. In the dialog box:
    - Enable the `Enabled` and `Skip if no change` options.
    - Click on `Select program/script` and select `main_minimized.bat.lnk` in this repository.
    - Set `Arguments/Parameters` to `pull <template_name> "%%fullpagename%%" "%%file%%"` where `<template_name>` is the name of the template.
    - You can choose any valid path for `Input/Output file`, as long as it does not overwrite other content.
5. Go to the `Skip` tab and perform the following:
    - Enable `No changes were made` in the `General skip options` section.
6. Go to the `Start` tab and start the bot to read from the wiki.
7. An Excel file with the same name as the template should be generated under `data` in this repository.

### Pushing to wiki from Excel

1. Find the name of the template you want to process (without prefix and suffix).
2. Create the list of page names to process and save them to a file using this command:
   ```
   python main.py list-pages <template_name> > <file_path>
   ```
   where `<template_name>` is the name of the template, and `<file_path>` is the path to the save file (e.g., `temp.txt`).
3. Open AutoWikiBrowser and log in your account.
4. Use the `Make List` feature to import the text file created in Step 2. If there are existing pages in the wiki not included in the Excel file that you wish to delete templates from, add them to the list as well.
5. Select `Tools > External Processing`. In the dialog box:
    - Enable the `Enabled` and `Skip if no change` options.
    - Click on `Select program/script` and select `main.bat` in this repository.
        - If you do not wish a new window to pop up each time the script is run, you can instead select a shortcut to the script that is configured to run in minimized mode. You can configure a shortcut as such by right-clicking it and modifying the setting under `Properties > Shortcut > Run` to "Minimized".
    - Set `Arguments/Parameters` to `push <template_name> "%%fullpagename%%" "%%file%%"` where `<template_name>` is the name of the template.
    - You can choose any valid path for `Input/Output file`, as long as it does not overwrite other content.
6. Go to the `Skip` tab and perform the following:
    - Enable `No changes were made` in the `General skip options` section.
    - Select `Don't care` in the `Page` section.
7. Go to the `Start` tab and start the bot to update the wiki.

## Specifications

### Excel file

Excel files containing template data are located in the `data` directory under this repository. Each file has the same name as the corresponding template (without prefix and suffix).

Each file contains at least one spreadsheet. For templates without suffixes in their names, the first spreadsheet stores its data. For templates with suffixes in their names, the spreadsheet with the same name as that of the suffix stores its data.

For illustration, consider an Excel file named `Item.xlsx` and having three spreadsheets: `main`, `info` and `extra`. According to the specifications, the `main` spreadsheet holds data for `Template:Item` (and/or `Template:Item/main`), the `info` spreadsheet holds data for `Template:Item/info`, while the `extra` spreadsheet holds data for `Template:Item/extra`.

Each spreadsheet begins with a header row containing `_pageName` (the `{{FULLPAGENAME}}` of the parent page) and `_indexInPage` (the index of the template instance with respect to the list containing all instances of this template in the page), with the remaining fields corresponding to the template's parameters. Each entry in the spreadsheet corresponds to an instance of the template.
