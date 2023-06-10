import requests, os, re
import configparser as cfg

from timeloop import Timeloop
from datetime import timedelta

tl = Timeloop()

def fetch(url, timeout=1):
    try:
        return requests.get(url, timeout=timeout)
    except:
        return None

@tl.job(interval=timedelta(milliseconds=700))
def data_sync():
    if not os.path.exists('config.ini'):
        raise Exception('config file not found')

    conf = cfg.ConfigParser()
    conf.read('config.ini')

    url = f"http://{conf['holyrics']['host']}:{conf['holyrics']['port']}"
    holyricsUrl = f'{url}/stage-view/text.json'

    print(f'Lendo {holyricsUrl}...')

    os.makedirs('files', exist_ok=True)
    if not os.path.exists('files/music.txt'):
        with open('files/music.txt', 'w', encoding='utf-8') as fp:
            fp.write('')
    
    if not os.path.exists('files/bible.csv'):
        with open('files/bible.csv', 'w', encoding='utf-8') as fp:
            fp.write(f'verse,text\n" "," "')

    res = fetch(holyricsUrl, 0.5)
    if res and res.ok:
        ob = res.json()
        ob = ob['map']
        
        type = ob['type'] # BIBLE, MUSIC
        if type == 'MUSIC':
            text = ob['text']
            text = re.sub(r'<[^>]*>', '', text)
            text = text.replace('\n', ' ')
            text = text.replace('\r', '')
            with open('files/music.txt', 'w', encoding='utf-8') as fp:
                fp.write(text)
        elif type == 'BIBLE':
            header = ob['header']
            header = re.sub(r'<[^>]*>', '', header)
            text_search = re.search(r'<ctt>(.*)<\/ctt>', ob['text'], re.IGNORECASE)
            text = ''
            if text_search:
                text = text_search.group(1)

            text = text.replace('“', '"')
            text = text.replace('”', '"')

            text = text.replace('"', '""')

            with open('files/bible.csv', 'w', encoding='utf-8') as fp:
                fp.write(f'verse,text\n{header},"{text}"')
        print('OK!')
    else:
        print('SEM RESPOSTA!')

if '__main__' in __name__:
    tl.start(block=True)
    print('Server is running!')
