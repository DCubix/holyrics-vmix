import requests, os, re
import configparser as cfg

from timeloop import Timeloop
from datetime import timedelta

tl = Timeloop()

@tl.job(interval=timedelta(seconds=1))
def data_sync():
    if not os.path.exists('config.ini'):
        raise Exception('config file not found')

    conf = cfg.ConfigParser()
    conf.read('config.ini')

    url = f"http://{conf['holyrics']['host']}:{conf['holyrics']['port']}"

    os.makedirs('files', exist_ok=True)
    if not os.path.exists('files/music.txt'):
        with open('files/music.txt', 'w', encoding='utf-8') as fp:
            fp.write('')
    
    if not os.path.exists('files/bible.csv'):
        with open('files/bible.csv', 'w', encoding='utf-8') as fp:
            fp.write(f'verse,text\n" "," "')

    res = requests.get(f"{url}/stage-view/text.json", timeout=5)
    if res.ok:
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
            header = re.sub(r'<desc>', '', header)
            header = re.sub(r'<\/desc>', '', header)
            text_search = re.search(r'<ctt>(.*)<\/ctt>', ob['text'], re.IGNORECASE)
            text = ''
            if text_search:
                text = text_search.group(1)
            
            text = text.replace('\n', ' ')
            text = text.replace('\r', '')

            with open('files/bible.csv', 'w', encoding='utf-8') as fp:
                fp.write(f'verse,text\n{header},"{text}"')


if '__main__' in __name__:
    tl.start(block=True)
    print('Server is running!')
