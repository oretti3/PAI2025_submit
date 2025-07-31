# ちんちろロボ (Chinchiro Robo) - 音声で対話するマルチモーダル・マニピュレーションロボット

[![ちんちろロボ デモ](https://img.youtube.com/vi/YOUR_YOUTUBE_VIDEO_ID/0.jpg)](https://www.youtube.com/watch?v=YOUR_YOUTUBE_VIDEO_ID)
*(画像をクリックするとデモ動画を再生します。YOUR_YOUTUBE_VIDEO_IDを実際の動画IDに置き換えてください)*

本プロジェクトは、Physical AI講座の最終課題として制作した、音声対話を通じて操作可能なマルチモーダル・マニピュレーションロボットです。ユーザーが「サイコロを振って」と話しかけるだけで、ロボットがその意図を理解し、実際にサイコロを振る一連の動作を実行します。

## 概要

「ちんちろロボ」は、近年のPhysical AI分野における重要技術を統合し、人間とロボットのより直感的で自然なインタラクションを探求するプロジェクトです。具体的には、以下の技術を組み合わせています。

- **音声認識 (Speech Recognition)**: [Faster-Whisper](https://github.com/SYSTRAN/faster-whisper) を用いて、ユーザーの音声を高速・高精度にテキスト化します。
- **意図解釈 (Intent Recognition)**: [Google Gemini API](https://ai.google.dev/) を活用し、テキスト化された自然言語の曖昧な指示から、ロボットが実行すべきタスク（例: `play_roll_dice`）を特定します。
- **行動生成 (Action Generation)**: [LeRobot](https://huggingface.co/lerobot) フレームワーク上で動作するVLA (Vision-Language-Action) モデルである [SmolVLA](https://huggingface.co/blog/smolvla) を使い、カメラ映像と言語指示に基づき、ロボットアームの具体的な動作を生成します。

## システム構成図

本システムの処理フローは以下の通りです。

![システム概要図](https://raw.githubusercontent.com/your_username/your_repository_name/main/path/to/your/diagram.png)
*(ここにレポートにあるシステム概要図の画像をリポジトリにアップロードし、そのURLにリンクを書き換えてください)*

1. ユーザーが音声で指示を出す。
2. **Faster-Whisper** が音声をテキストに変換。
3. **Gemini API** がテキストから意図を抽出し、標準化されたタスクコマンドを生成。
4. **SmolVLA** がタスクコマンドとカメラ映像を基にロボットの動作を決定し、実行。

## 環境構築

本プロジェクトは、`LeRobot`の環境といくつかのPythonライブラリに依存します。

### 1. 前提条件
- Ubuntu 22.04
- Python 3.10+
- `conda` または `venv` による仮想環境管理を推奨

### 2. リポジトリのクローン

（ここに `git clone` のコマンドが入ります）

### 3. LeRobotおよび依存ライブラリのインストール
新しい仮想環境を作成し、その中で作業することをお勧めします。

（ここに `conda` と `pip install` のコマンドが入ります）

`requirements.txt` の内容は以下の通りです。

（ここに `requirements.txt` の内容が入ります）

### 4. APIキーの設定
本プロジェクトはGemini APIを使用します。以下の手順でAPIキーを設定してください。
1. [Google AI Studio](https://aistudio.google.com/app/apikey) でAPIキーを取得します。
2. 環境変数としてAPIキーを設定します。

（ここに `export` コマンドが入ります）

### 5. ハードウェアのセットアップ
- **ロボットアーム**: `myCobot 280 (so101)` をリーダーアーム・フォロワーアームとして2台使用します。
  - フォロワーアーム: `/dev/ttyACM0`
  - リーダーアーム: `/dev/ttyACM1`
- **カメラ**:
  - 俯瞰カメラ (front): `/dev/video0`
  - 手元カメラ (sub): `/dev/video2`
- **マイク**: `task_tintiro.py`内の`DEVICE_IDX`を使用するマイクのデバイスインデックスに設定してください。

## 使い方

### 1. メインデモの実行

環境構築完了後、以下のコマンドでメインプログラムを実行します。音声指示に応じてロボットが動作します。

（ここに `python task_tintiro.py` のコマンドが入ります）

プログラムが起動したら、ターミナルの指示に従ってEnterキーを押し、ロボットに話しかけてください。

### 2. LeRobot 開発コマンド集

本プロジェクトの開発（データ収集、学習など）で使用した`LeRobot`のコマンド例です。

#### テレオペ動作確認
リーダーアームとフォロワーアームが正しく連動するかを確認します。

（ここにテレオペ動作確認のコマンドが入ります）

#### データセット収集
ロボットを操作し、学習用のデモンストレーションデータを収集します。

（ここにデータセット収集のコマンドが入ります）

#### 学習
収集したデータセットを用いてSmolVLAモデルのポリシーを学習させます。

（ここに学習のコマンドが入ります）

#### 推論テスト
学習済みポリシーを用いて、単一タスクの推論を実行します。

（ここに推論テストのコマンドが入ります）

## (おまけ) アテンションマップの可視化

レポートに掲載したアテンションマップは、以下のリポジトリを用いて可視化しました。

- **リポジトリ**: [villekuosmanen/physical-Al-interpretability](https://github.com/villekuosmanen/physical-Al-interpretability)

### セットアップと実行
1. 上記リポジトリをクローンし、手順に従って環境をセットアップします。
2. 以下のコマンドで、学習済みポリシーと評価用データを用いてアテンションを可視化します。

（ここにアテンションマップ可視化のコマンドが入ります）
