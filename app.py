from flask import Flask, render_template, request

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
        from bs4 import BeautifulSoup as bs
        import pandas as pd
        import requests
        import cgi
        form = cgi.FieldStorage()
        num =  form.getvalue('ecfr_number')

        xml_bs = requests.get(f'https://www.govinfo.gov/bulkdata/ECFR/title-{num}/ECFR-title{num}.xml')
        soup = bs(xml_bs.content, 'xml')

        list_of_dicts_bs = []
        
        chapters_bs = soup.find_all('DIV3')
        for chapter_bs in chapters_bs:
            chapter_num_bs = chapter_bs.attrs['N']
            chapter_title_bs = chapter_bs.find('HEAD').text

            subchapters_bs = chapter_bs.find_all('DIV4')
            for subchapter_bs in subchapters_bs:
                subchapter_num_bs = subchapter_bs.attrs['N']
                subchapter_title_bs = subchapter_bs.find('HEAD').text

                parts_bs = subchapter_bs.find_all('DIV5')
                for part_bs in parts_bs:
                    part_num_bs = part_bs.attrs['N']
                    part_title_bs = part_bs.find('HEAD').text

                    sections_bs = part_bs.find_all('DIV8')
                    for section_bs in sections_bs:
                        section_num_bs = section_bs.attrs['N'][2:]
                        section_title_bs = section_bs.find('HEAD').text
                        section_text_bs = section_bs.find_all('P')

                        list_of_dicts_bs.append({'chapter': chapter_num_bs, 'chapter_title': chapter_title_bs,
                                                    'subchapter': subchapter_num_bs, 'subchapter_title': subchapter_title_bs, 
                                                    'part': part_num_bs, 'part_title': part_title_bs, 'section': section_num_bs, 
                                                    'section_title': section_title_bs, 'section_text': str(section_text_bs)})

        df_bs = pd.DataFrame(data=list_of_dicts_bs, columns=['chapter', 'chapter_title', 'subchapter', 
            'subchapter_title', 'part', 'part_title', 'section', 'section_title', 'section_text'])

        for col in df_bs.columns:
            df_bs[col] = df_bs[col].str.strip()

        regex_bs = "\[+|\]+|<[A-Z]+>+|<\/[A-Z]+>+|\\n+"
        df_bs.section_text = df_bs.section_text.str.replace(regex_bs, '')

        output = df_bs.to_csv('/downloads', index=False)

    return send_file()


if __name__ == "__main__":
    app.run(debug=True)