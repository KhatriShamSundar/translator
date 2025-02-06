import requests
from bs4 import BeautifulSoup
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

def synon(word):
    word = word.replace("!", "").replace(".", "").replace("(", "").replace(")", "").replace("[", "").replace("]", "").replace("-", "").replace(",", "")
    wordcopy = word
    word = word.lower().strip()

    if len(word.split(" ")) > 1:
        word = word.replace("they ", "").replace("in ", "").replace("the ", "").replace("of ", "").replace("most ", "").replace("all ", "").replace("and ", "").replace("to ", "").replace("be ", "").replace("you ", "").replace("we ", "").replace("for ", "").replace(" us", "").replace("did ", "").replace("not ", "").replace("there ", "").replace(" is ", "")

    res = []
    for i in word.split(" "):
        link = f'https://api.dictionaryapi.dev/api/v2/entries/en/{i}'
        response = requests.get(link)
        try:
            definitions = []
            data = response.json()
            for entry in data:
                for meaning in entry["meanings"]:
                    for definition in meaning["definitions"]:
                        definitions.append(definition["definition"])
            if len(definitions) > 0:
                if len(definitions) > 3:
                    res.extend(definitions[:2])
                else:
                    res.extend(definitions)

        except Exception:
            response = requests.get(f'https://api.api-ninjas.com/v1/thesaurus?word={i}', headers={"Content-Type": "text", "X-Api-Key": "xU7F4ZB9wCsPXGTh456ZfQ==LfCJSJy5T1fb9HEL"})
            data = response.json()
            val = []
            if data.get('synonyms', None):
                val.extend(data.get('synonyms', None))
            if data.get('definition', None):
                val.extend(data.get('definition', None))

            if len(val) > 0:
                if len(val) > 3:
                    res.extend(val[:2])
                else:
                    res.extend(val)
    if res:
        return ",".join(res)
    else:
        return str(wordcopy)


def fetch_verse_translation(chapter, verse):
    url = f'https://api.alquran.cloud/v1/ayah/{chapter}:{verse}/en.asad'
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        if data['status'] == 'OK':
            return data['data']['text']
    return None


def fetch_morphology_table(chapter, verse):
    url = f'https://corpus.quran.com/wordbyword.jsp?chapter={chapter}&verse={verse}'
    response = requests.get(url)

    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        morphology_table = soup.find('table', class_='morphologyTable')

        if morphology_table:
            for img in soup.find_all('img', src=True):
                if img['src'].startswith('/wordimage?id=') or img['src'].startswith('/images/verses/'):
                    img['src'] = 'https://corpus.quran.com' + img['src']

            header_row = morphology_table.find('tr')
            if header_row:
                new_header = soup.new_tag('th')
                new_header.string = "Synonyms"
                header_row.append(new_header)

            for row in morphology_table.find_all('tr')[1:]:
                htmldata = row.find('td')
                textdata = htmldata.find_all(text=True)[-1]
                new_cell = soup.new_tag('td')
                conv = synon(textdata)
                new_cell.string = conv
                row.append(new_cell)

            return str(morphology_table)

    return None


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/get_data', methods=['POST'])
def get_data():
    chapter = request.form['chapter']
    verse = request.form['verse']

    translation = fetch_verse_translation(chapter, verse)
    if translation is None:
        return jsonify({'error': 'Failed to fetch the translation.'})

    morphology_table = fetch_morphology_table(chapter, verse)
    if morphology_table is None:
        return jsonify({'error': 'Failed to fetch the morphology table.'})

    return jsonify({
        'translation': translation,
        'morphology_table': morphology_table
    })


if __name__ == "__main__":
    app.run(debug=True)
