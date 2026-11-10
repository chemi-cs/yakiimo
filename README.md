# 焼き芋で学ぶ Python 入門：Binderバックアップ

授業のメインは **[公開済みのJupyterLite教材](https://chemi-cs.github.io/yakiimo-lite/lab/index.html)** です。
このリポジトリには、その教材と同じ内容を通常のPython環境で動かすBinder用バックアップを用意しています。

## 予備の教材を開く

**[Binderで最新版の教材を開く](https://mybinder.org/v2/gh/chemi-cs/yakiimo/main?urlpath=%2Fdoc%2Ftree%2Fyakiimo_python_junior.ipynb)**

1. 上のリンクを開き、環境の準備が終わるまで待ちます。初回や更新直後は数分以上かかることがあります。
2. `yakiimo_python_junior.ipynb` が開いたら、カーネルが **Python 3 (ipykernel)** になっていることを確認します。
3. 上から順に、セルを選んで **Shift + Enter** で実行します。化学パートでは最初に準備セルを実行します。
4. 編集内容を残す場合は、終了前にNotebookをダウンロードしてください。Binderの保存は一時的です。

ログインや、生徒のPCへのPythonのインストールは不要です。
もしファイル一覧が開いた場合は、`yakiimo_python_junior.ipynb` を選んでください。
従来の `test.ipynb` と `講義テキスト.ipynb` は、過去の教材としてそのまま残しています。今回のバックアップには新しいファイル名を使います。

## 同期元と違い

- 同期元：[chemi-cs/yakiimo-lite の公開版](https://github.com/chemi-cs/yakiimo-lite/blob/2e7c630615f400452cf310a8015c7e99609affdd/content/yakiimo_python_junior.ipynb)
- 同期元コミット：`2e7c630615f400452cf310a8015c7e99609affdd`
- 教材は94セル、うち実行するコードは45セルです。導入デモ、練習1〜8、ヒント・解答、グラフ、分子表示、温度制御の説明を含みます。
- Binder用の変更は、実行環境の説明、ライブラリの準備セル、SVG表示の互換処理、実機用コードを実行しない旨の注意です。演習・例題・分子の計算は公開版を引き継いでいます。
- JupyterLiteではPyodide上で動きますが、Binderではサーバー上のPython 3.12と通常のRDKit 2026.3.6を使います。WebAssembly用wheelは使用しません。
- 画像 `1.2.png` と構造データ `5wqs.pdb` は、公開版と同一です。
- 出典のコミット、ファイルのハッシュ、変換箇所は `BINDER_SOURCE.json` に記録しています。

## 授業前の確認

Binderは無料の共有サービスです。起動時間や可用性は保証されないため、授業当日に使うPCと校内ネットワークで事前に起動してください。
更新後は再ビルドが必要になるため、授業直前の更新は避けてください。
これはJupyterLiteが使えないときの予備ですが、どちらもインターネット接続が必要です。

確認する項目：

- 温度判定と練習問題が実行できること。
- 化学の準備セルにRDKitの準備完了メッセージが出ること。
- 麦芽糖の分子式 `C12H22O11`、分子量 `342.3`、2D構造式が表示されること。
- 麦芽糖と酵素の3D表示をドラッグで回せること。3DにはブラウザのWebGLと外部JavaScriptの読み込みが必要です。

温度制御のPico用コードは説明用のMarkdownです。Binderからヒーターを動かす機能はありません。
Binderにはパスワード、個人情報、機密資料などを入れないでください。

詳しい制限：[Binder公式の利用ガイド](https://mybinder.readthedocs.io/en/latest/about/user-guidelines.html)

## 管理者向け：更新と検証

Binderは `.binder/requirements.txt` と `.binder/runtime.txt` を読みます。
`.binder/` があるため、ルートの従来の `requirements.txt` はBinderの環境構築には使用されません。
ルートの設定と過去のNotebookは、従来のローカル利用向けに残しています。

今回の授業で実行するNotebookは、必ず新しい名前を使ってください。

```bash
python -m pip install -r .binder/requirements.txt ipykernel
python scripts/validate_notebook.py --execute
```

検証では、Notebookの形式、45コードセルの構文、画像・構造データ、麦芽糖の分子式・分子量・SVG・3D座標、酵素ビューアーの生成、エタノールと水への変更を確認します。
ブラウザでの3D表示や校内ネットワークの確認は、これとは別に行ってください。
Binderのビルド時とGitHub Actionsでも同じ検証を実行します。

JupyterLite教材を将来更新したときは、検証済みの `yakiimo-lite` を手元に用意し、次のように同期します。自動で変更が同期される仕組みではありません。

```bash
python scripts/prepare_binder.py ../yakiimo-lite
python scripts/validate_notebook.py --source-checkout ../yakiimo-lite --execute
```

差分を確認し、検証後にGitHubへ保存してください。元教材の構成が変わった場合、変換スクリプトは停止するので、変換箇所を見直します。
通常のBinderリンクは `main` の最新コミットを使います。授業で版を固定したい場合は、URL中の `main` を検証済みコミットの完全なSHAへ置き換えます。
