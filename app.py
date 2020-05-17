from flask import Flask, Response, render_template, request, send_file
import bs4
from bs4 import BeautifulSoup as bs
import pandas as pd
import requests
import cgi

# app = Flask(__name__)
import os 
dir_path = os.path.dirname(os.path.realpath(__file__))
app = Flask(__name__, template_folder=dir_path)

@app.route('/ecfr_parser', methods=['GET'])
def ecfr_parser():
      return render_template('ecfr_parser.html')

@app.route('/ecfr_process', methods=['POST'])
def ecfr_process():
    if request.method == "POST":
        
        def parsing():
            form = cgi.FieldStorage()
            num =  form.getvalue('ecfr_number')

            url = f'https://www.govinfo.gov/bulkdata/ECFR/title-{num}/ECFR-title{num}.xml'
            xml = requests.get(url)
            soup = bs(xml.content, 'lxml')

            list_of_dicts = []
            
            chapters = soup.find_all('DIV3')
            for chapter in chapters:
                chapter_num = chapter.attrs['N']
                chapter_title = chapter.find('HEAD').text

                subchapters = chapter.find_all('DIV4')
                for subchapter in subchapters:
                    subchapter_num = subchapter.attrs['N']
                    subchapter_title = subchapter.find('HEAD').text

                    parts = subchapter.find_all('DIV5')
                    for part in parts:
                        part_num = part.attrs['N']
                        part_title = part.find('HEAD').text

                        sections = part.find_all('DIV8')
                        for section in sections:
                            section_num = section.attrs['N'][2:]
                            section_title = section.find('HEAD').text
                            section_text = section.find_all('P')

                            list_of_dicts.append({'chapter': chapter_num, 'chapter_title': chapter_title,
                                                    'subchapter': subchapter_num, 'subchapter_title': subchapter_title, 
                                                    'part': part_num, 'part_title': part_title, 'section': section_num, 
                                                    'section_title': section_title, 'section_text': str(section_text)})

                            df = pd.DataFrame(data=list_of_dicts, columns=['chapter', 'chapter_title', 'subchapter', 
                            'subchapter_title', 'part', 'part_title', 'section', 'section_title', 'section_text'])

                            for col in df.columns:
                                df[col] = df[col].str.strip()

                            regex = "\[+|\]+|<[A-Z]+>+|<\/[A-Z]+>+|\\n+"
                            df.section_text = df.section_text.str.replace(regex, '')

                            csv = df.to_csv('~/downloads/ecfr_download', index=False)

                            return csv

    # return send_file('app.py')
    # return render_template('ecfr_parser.html', data=parsing()) 
    return Response(parsing(), mimetype="text/csv", headers={"Content-disposition":
    "attachment; filename=ecfr_download.csv"})


if __name__ == "__main__":
    app.run(debug=True)