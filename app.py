from flask import Flask
from flask import render_template, url_for, send_file
from flask import request

from os import mkdir, remove, path
from os import system as run

from hashlib import sha256
from datetime import datetime

import csv
import re

dir_path = path.dirname(path.realpath(__file__))

app = Flask(__name__)
latex_special = ['#', '$', '%', '^', '&', '_', '{', '}', '~']
regex_special = ['\\', '[', '^', '$', '.', '|', '?', '*', '+', '(', ')', '{', '}']
blank = 'standard'


@app.route('/')
def index():
    pretty_print_url = url_for('.pretty_print')
    return render_template('index.html', pretty_print_url=pretty_print_url)


@app.route('/print/', methods=['GET', 'POST'])
def pretty_print():
    if request.method == 'POST':
        code = sha256(str(datetime.now()).encode('ascii', 'ignore')).hexdigest()

        title = request.form['title']
        response = request.files['form_responses']
        response.save('%s/input/%s.csv' % (dir_path, code))
        mkdir('intermediate/%s/' % code)
        mkdir('output/%s/' % code)

        with open('blanks/%s.tex' % blank, encoding='utf8') as f:
            template = f.read()
        short_answer = re.search('%SHORT%(.*?)%SHORT%', template, flags=re.DOTALL).group(1)
        long_answer = re.search('%LONG%(.*?)%LONG%', template, flags=re.DOTALL).group(1)

        with open('input/%s.csv' % code, encoding='utf8') as csv_file:
            csv_reader = csv.DictReader(csv_file)
            field_names = csv_reader.fieldnames

            c = 0
            for row in csv_reader:
                c += 1
                answers = ''
                source = template.replace('[title]', title)

                for field in field_names:
                    answer = row[field]

                    answer = answer.replace('\\', '\\backslash')
                    for character in latex_special:
                        answer = answer.replace(character, '\\' + character)

                    answer_type = short_answer if len(field.split()) < 3 else long_answer
                    answers += answer_type.replace('[question]', field).replace('[answer]', answer)

                answers = answers.replace('\\', '\\\\')

                source = re.sub(r'%ANSWERS%(.*?)%ANSWERS%', answers, source, flags=re.DOTALL)

                with open('intermediate/%s/%d.tex' % (code, c), 'w', encoding='utf8') as new_source_file:
                    new_source_file.write(source)

                run('pdflatex -output-directory output/%s "intermediate/%s/%d.tex"' % (code, code, c))
                run('pdflatex -output-directory output/%s "intermediate/%s/%d.tex"' % (code, code, c))
                remove('output/%s/%d.log' % (code, c))
                remove('output/%s/%d.aux' % (code, c))
                remove('output/%s/%d.out' % (code, c))

            run('jar -cf output/%s.zip -C output/%s/ .' % (code, code))

        return send_file('%s/output/%s.zip' % (dir_path, code), as_attachment=True,
                         attachment_filename='%s.zip' % title.replace(' ', ''))


if __name__ == '__main__':
    app.run(host='0.0.0.0')
