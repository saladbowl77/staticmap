import sqlite3
import hashlib
from datetime import datetime, timezone, timedelta
from io import BytesIO
import requests

class mapCache:
    def __init__(
        self,
        imageURL:str,
        expires:int = 90,
        dbname:str = 'mapdata.db',
        devMode:bool = False
    ):
        self.url = imageURL
        self.expires = expires
        self.dbname = dbname
        self.nowDT = datetime.now(timezone(timedelta(hours=9)))
        self.dev = devMode

    def saveMapImage(self):
        headers = {
            'User-Agent': 'Static Map 2',
            'Cache-Control': 'max-age=604800'
        }
        res = requests.get(self.url, headers=headers)
        if self.dev:
            print(res.status_code, self.url, type(res.content))

        # ファイルの拡張子を確認する print((res.headers['Content-Type'].split('/'))[1])
        if res.status_code == 200:
            return res.content
        else:
            return res.status_code 

    def mkDB(self, conn, cur):
        cur.execute('CREATE TABLE IF NOT EXISTS cacheData(id INTEGER PRIMARY KEY AUTOINCREMENT, imgID STRING, url STRING, byteData BLOB, expires STRING)')
        conn.commit()

    def saveCache(self, conn, cur):
        # テーブルの作成
        # 名前      | 型  | 内容
        # id       | int | 通し番号
        # imgID    | str | 画像のID
        # url      | str | キャッシュするurl
        # nyteData | non | 画像のバイナリデータ
        # expires  | str | キャッシュの残す日付(%Y/%m/%d %H:%M:%S %z)

        # imageIDの生成
        text = self.url + self.nowDT.strftime('%Y/%m/%d %H:%M:%S.%f %z')
        imageID = "I_" + hashlib.md5(text.encode()).hexdigest()
        # データ登録
        expiresDay = (self.nowDT + timedelta(days=self.expires)).strftime('%Y/%m/%d %H:%M:%S %z')
        mapData = mapCache.saveMapImage(self)
        if type(mapData) is int:
            return BytesIO()
        else:
            if self.dev:
                print(expiresDay)
            cur.execute(f'INSERT INTO cacheData(imgID, url, byteData, expires) VALUES(?, ?, ?, ?)', (imageID, self.url, mapData, expiresDay))
            # commit→データの反映
            conn.commit()
            return BytesIO(mapData)

    def loadMap(self):
        if self.expires == 0:
            mapData = mapCache.saveMapImage(self)
            return  BytesIO(mapData)
        else:
            conn = sqlite3.connect(self.dbname)
            cur = conn.cursor()
        
            mapCache.mkDB(self, conn, cur)

            # データ検索
            cur.execute(f'SELECT * FROM cacheData WHERE url = "{self.url}";')
            for row in cur:
                # debug info
                if self.dev:
                    print(f"--- list of {self.url} data ---")
                    print(f"image id    : {row[1]}\ncache limit : {row[4]}")
                    print("--- end ---")
                if datetime.strptime(row[4], "%Y/%m/%d %H:%M:%S %z") > self.nowDT:
                    cur.fetchall()
                    conn.close()
                    return BytesIO(row[3])
                elif datetime.strptime(row[4], "%Y/%m/%d %H:%M:%S %z") < self.nowDT:
                    cur.execute(f'DELETE FROM cacheData WHERE imgID = "{row[1]}";')
            mapData = mapCache.saveCache(self, conn, cur)
            conn.close()
            return mapData