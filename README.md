# gitauto_request
gitauto_request

## ブロック崩しゲーム

A Python implementation of Brick Breaker featuring enhanced visual effects.  
https://qiita.com/seigot/items/bc1bb29950e0a4ccb32a  

環境構築

```
python -m venv venv
source venv/bin/activate
pip install pygame
```

実行

```
python brick_breaker9.py
```

## etc..
## Simple Navigation App

A Python-based navigation application using TkinterMapView and OpenRouteService.

環境構築

```
python -m venv venv
source venv/bin/activate
pip install tkintermapview requests
```

実行

```
python simple_nav_app.py
```

注意:
1. OpenRouteService APIキーが必要です (https://openrouteservice.org/ で取得できます)
2. スクリプト内の 'YOUR_API_KEY' を取得したAPIキーに置き換えてください

機能:
- マップ表示 (OpenStreetMapベース)
- クリックによる出発地点・目的地の設定
- OpenRouteServiceを使用した経路探索
