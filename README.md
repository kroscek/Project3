# PDF-Search-Engine
This script will produce relevant summary of the choosen PDF file. First, it will strip-off all the PDF pages into a single page. This single page will be treated as a single document so that it can be processed with Vector Relation. Then it will use textract package to extract all texts in a single PDF page. After the query being given by the user (query can be more than 2 words), it will return the summary. You can read the summary in terminal or at your home file with the name file: summary_{your query}.txt.

## Required Packages:
- textract
- PyPDF2
- pdftk on Ubuntu

## How to Use?
1. Type python search_engine.py
2. Enter your PDF file path
3. Enter your query. Note that the query can be more than two words
4. To exit, press CTRL+C
