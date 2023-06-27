import time
import requests
from bs4 import BeautifulSoup
import urllib.request
from urllib.parse import urlparse
import os

# ポスターを保存するフォルダを指定します。
download_folder = '/Users/masa/CVPR2023_poster'

# ログインページURLと認証情報をセットします。
login_url = 'https://cvpr2023.thecvf.com/accounts/login'
credentials = {
    'username': 'XXXXXXXXXXXXXXXXXXXXXXXX',
    'password': 'YYYYYYYYYYYYYYYYYYYYYYYY',
    'this_is_the_login_form': '1',
    'nextp': '/'
}

# CVPR2023のポスターセッションの情報
page_baseurl = 'https://cvpr2023.thecvf.com/virtual/2023/session/'
page_list = ['23307', '23308', '23309', '23310', '23311', '23312']

                        
# セッションを作成します。
with requests.Session() as session:
    # 最初にログインページにGETリクエストを送ります。
    response = session.get(login_url)
    soup = BeautifulSoup(response.text, 'html.parser')

    # CSRFトークンを抽出します。
    csrfmiddlewaretoken = soup.find('input', attrs={'name': 'csrfmiddlewaretoken'}).get('value')

    # 認証情報にCSRFトークンを追加します。
    credentials['csrfmiddlewaretoken'] = csrfmiddlewaretoken

    # POSTリクエストを送ります。
    post = session.post(login_url, data=credentials, headers={'Referer': login_url})

    # ログイン後、リンクが含まれる各ページにアクセスします。
    for page in page_list:
        url = page_baseurl + page
        response = session.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')

        print(f"accessing {url}")

        # mkdir
        dir=os.path.join(download_folder, page)
        os.makedirs(dir, exist_ok=True)
        
        # ポスターページへのリンクを見つけます。
        for link in soup.find_all('a', href=True):
            if "/virtual/2023/poster/" in link.get('href'):
                poster_url = "https://cvpr2023.thecvf.com" + link.get('href')

                # ポスターページにアクセスします。
                response = session.get(poster_url)
                soup = BeautifulSoup(response.text, 'html.parser')

                # "/media/PosterPDFs"を含むリンクを見つけます。
                for img_link in soup.find_all('a', href=True):
                    if "/media/PosterPDFs" in img_link.get('href'):
                        # 完全なURLを作成します。
                        full_url = "https://cvpr2023.thecvf.com" + img_link.get('href')
                        
                        # クエリパラメータを削除します。
                        parsed_url = urlparse(full_url)
                        clean_image_url = parsed_url.scheme + '://' + parsed_url.netloc + parsed_url.path
                        
                        # 画像をダウンロードします。
                        image_name = os.path.join(dir, os.path.basename(clean_image_url))

                        # If the image is already downloaded, skip
                        if os.path.exists(image_name):
                            print(f"{image_name} already exists, skipping...")
                            continue
                        
                        print(f'downloading {clean_image_url}')
                        urllib.request.urlretrieve(clean_image_url, image_name)
                        time.sleep(5)
