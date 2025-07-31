# ちんちろロボ - 音声で対話するマルチモーダル・マニピュレーションロボット

本プロジェクトは、Physical AI講座の最終課題として制作した、音声対話を通じて操作可能なマルチモーダル・マニピュレーションロボットです。ユーザーが「サイコロを振って」と話しかけるだけで、ロボットがその意図を理解し、実際にサイコロを振る一連の動作を実行します。

## 概要

「ちんちろロボ」は、以下の技術を組み合わせています。

- **音声認識 (Speech Recognition)**: [Faster-Whisper](https://github.com/SYSTRAN/faster-whisper) を用いて、ユーザーの音声を高速・高精度にテキスト化します。
- **意図解釈 (Intent Recognition)**: [Google Gemini API](https://ai.google.dev/) を活用し、テキスト化された自然言語の曖昧な指示から、ロボットが実行すべきタスク（例: `play_roll_dice`）を特定します。
- **行動生成 (Action Generation)**: [LeRobot](https://huggingface.co/lerobot) フレームワーク上で動作するVLA (Vision-Language-Action) モデルである [SmolVLA](https://huggingface.co/blog/smolvla) を使い、カメラ映像と言語指示に基づき、ロボットアームの具体的な動作を生成します。

## システム構成図

本システムの処理フローは以下の通りです。

![システム概要図](https://github.com/oretti3/PAI2025_submit/blob/main/bin/system_img.png?raw=true)

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
```bash
git clone https://github.com/oretti3/PAI2025_submit.git
```
### 3. LeRobotおよび依存ライブラリのインストール
新しい仮想環境を作成し、その中で作業することをお勧めします。

```bash
cd PAI2025_submit
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

git clone https://github.com/huggingface/lerobot.git
cd lerobot
pip install -e .
pip install -e ".[feetech]"  
pip install -e ".[smolvla]"
```

`requirements.txt` の内容は以下の通りです。
```bash
sounddevice
numpy
librosa
faster-whisper
google-generativeai
keyboard
```

### 4. APIキーの設定
本プロジェクトはGemini APIを使用します。以下の手順でAPIキーを設定してください。
1. [Google AI Studio](https://aistudio.google.com/app/apikey) でAPIキーを取得します。
2. 環境変数としてAPIキーを設定します。

```bash
export GOOGLE_API_KEY='YOUR_API_KEY'
```

### 5. ハードウェアのセットアップ
- **ロボットアーム**: `so-101` をリーダーアーム・フォロワーアームとして2台使用します。
  - フォロワーアーム: `/dev/ttyACM0`
  - リーダーアーム: `/dev/ttyACM1`
- **カメラ**:
  - 俯瞰カメラ (front): `/dev/video0`
  - 手元カメラ (sub): `/dev/video2`
- **マイク**: `task_tintiro.py`内の`DEVICE_IDX`を使用するマイクのデバイスインデックスに設定してください。

## 使い方

### 1. メインデモの実行

環境構築完了後、以下のコマンドでメインプログラムを実行します。音声指示に応じてロボットが動作します。

```bash
cd PAI2025_submit
python task_tintiro.py
```

プログラムが起動したら、ターミナルの指示に従ってEnterキーを押し、ロボットに話しかけてください。

### 2. LeRobot 開発コマンド集

本プロジェクトの開発（データ収集、学習など）で使用した`LeRobot`のコマンド例です。

#### テレオペ動作確認
リーダーアームとフォロワーアームが正しく連動するかを確認します。

```bash
python -m lerobot.teleoperate \
  --robot.type=so101_follower \
  --robot.port=/dev/ttyACM0 \
  --robot.type=so101_leader \
  --robot.port=/dev/ttyACM1 \
  --robot.cameras="{ front: {type: opencv, index_or_path: 0, width: 640, height: 480, fps: 30}, sub: {type: opencv, index_or_path: 2, width: 640, height: 480, fps: 30}}" \
  --display_data=true
```

#### データセット収集
ロボットを操作し、学習用のデモンストレーションデータを収集します。

```bash
python -m lerobot.record \
  --robot.type=so101_follower \
  --robot.port=/dev/ttyACM0 \
  --robot.type=so101_leader \
  --robot.port=/dev/ttyACM1 \
  --robot.cameras="{ front: {type: opencv, index_or_path: 0, width: 640, height: 480, fps: 30}, sub: {type: opencv, index_or_path: 2, width: 640, height: 480, fps: 30}}" \
  --display_data=true \
  --dataset.repo_id=${HF_USER}/so101_dice_5 \
  --dataset.episode_time_s=30 \
  --dataset.reset_time_s=5 \
  --dataset.num_episodes=10 \
  --dataset.single_task="Let's play with dice" \
  --resume=true
```

#### 学習
収集したデータセットを用いてSmolVLAモデルのポリシーを学習させます。

```bash
python src/lerobot/scripts/train.py \
  --policy.path=lerobot/smolvla_base \
  --dataset.repo_id=${HF_USER}/eval_so101_dice_5 \
  --policy.path=${HF_USER}/so101_dice_5_smolvla_policy1 \
  --batch_size=64 \
  --steps=50000
```

#### 推論テスト
学習済みポリシーを用いて、単一タスクの推論を実行します。

```bash
python -m lerobot.record \
  --robot.type=so101_follower \
  --robot.port=/dev/ttyACM0 \
  --robot.type=so101_leader \
  --robot.port=/dev/ttyACM1 \
  --robot.cameras="{ front: {type: opencv, index_or_path: 0, width: 640, height: 480, fps: 30}, sub: {type: opencv, index_or_path: 2, width: 640, height: 480, fps: 30}}" \
  --display_data=true \
  --dataset.push_to_hub=false \
  --dataset.repo_id=${HF_USER}/eval_so101_dice_5 \
  --policy.path=${HF_USER}/so101_dice_5_smolvla_policy1 \
  --dataset.episode_time_s=30 \
  --dataset.num_episodes=1 \
  --dataset.single_task="Let's play with dice" \
  --resume=true
```

## (おまけ) アテンションマップの可視化

レポートに掲載したアテンションマップは、以下のリポジトリを用いて可視化しました。

- **リポジトリ**: [villekuosmanen/physical-Al-interpretability](https://github.com/villekuosmanen/physical-AI-interpretability)

### セットアップと実行
1. 上記リポジトリをクローンし、手順に従って環境をセットアップします。
2. 以下のコマンドで、学習済みポリシーと評価用データを用いてアテンションを可視化します。


```bash
mkdir analysis_results
mkdir pretrained_model

wget https://huggingface.co/oretti/so101_dice_3_act_policy1/raw/main/config.json -O ./pretrained_model/config.json
wget https://huggingface.co/oretti/so101_dice_3_act_policy1/raw/main/train_config.json -O ./pretrained_model/train_config.json
wget https://huggingface.co/oretti/so101_dice_3_act_policy1/resolve/main/model.safetensors -O ./pretrained_model/model.safetensors

python -m examples.visualise_original_data_attention --dataset-repo-id oretti/so101_dice_3 --episode-id 18 --policy-path ./pretrained_model --output-dir ./analysis_results
```
