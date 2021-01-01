#!/usr/bin/env python
# coding: utf-8

import pdfplumber
import pandas as pd
import sys

#filenames hard coded, from my original drafting of script
#pdf_file = "ltcf_20201229.pdf"
#out_file = "ltcf_20201229.csv"

#arguments currently configured as if it's being called from commandline with python fl-ltcf-parser.py (pdf name) (csv name)

pdf_file = str(sys.argv[1])
if len(sys.argv) > 2:
    out_file = str(sys.argv[2])
else:
    filecore = str(sys.argv[1]).split(".")[0]
    out_file = filecore + ".csv"

pdf = pdfplumber.open(pdf_file)

table_settings = {
    "vertical_strategy": "lines",
    "horizontal_strategy": "lines",
}

#helper method that apparently breaks sometimes
#def get_bbox(page):
#    r0 = page.rects[0]
#    r1 = page.rects[1]
#    return (r1['x0'],r0['y0'],r1['x1'],r0['y1'])

bbox = (43,36,567,756)

pages = pdf.pages
page = pages[1]
table1 = page.crop(bbox).extract_table(table_settings)
#im = page.to_image(resolution=150)
#im.reset().debug_tablefinder(table_settings).save("page2.png")

ltcf_df = pd.DataFrame(table1[3:], columns=table1[1])
print(page)

for page in pages[2:]:
    #bbox = get_bbox(page)
    table = page.crop(bbox).extract_table(table_settings)
    df = pd.DataFrame(table, columns=table1[1])
    #im = page.to_image(resolution=150)
    #png_file = "page" + str(page.page_number) + ".png"
    #im.reset().debug_tablefinder(table_settings).save(png_file)
    print(page)
    ltcf_df = ltcf_df.append(df)
    #print(df)

ltcf_df["Update Time (UTC)"] = ltcf_df["Update Time (UTC)"].str.replace("\ue353",":")

for column in ["Update Time (UTC)","Positive\nResidents"]:
    ltcf_df[column] = ltcf_df[column].str.replace(".","")
ltcf_df["Positive\nResidents"] = ltcf_df["Positive\nResidents"].str.replace(" ","")

#Drop duplicates that result from rows being split across the bottom & top of a page
ltcf_df_nodupes = ltcf_df.drop_duplicates()

#Strip blank rows that sometimes occur
ltcf_df_final = ltcf_df_nodupes[ltcf_df_nodupes["Facility Name"].str.strip().astype(bool)]

ltcf_df_final.to_csv(out_file,index=False)