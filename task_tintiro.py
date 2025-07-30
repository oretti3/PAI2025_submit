import os
import time
import keyboard
import sounddevice as sd
import numpy as np
import librosa
from faster_whisper import WhisperModel
from google import genai
import subprocess

def run_lerobot_record(task_name):

    hf_user = "oretti"
    if not hf_user:
        print("エラー: 環境変数 HF_USER が設定されていません。")
        return
    print(f"[SmolVLA] Task : {task_name} で実行します.")
    # 実行するコマンドをリストとして構築
    command = [
        'python', '-m', 'lerobot.record',
        '--robot.type=so101_follower',
        '--robot.port=/dev/ttyACM0',
        '--teleop.type=so101_leader',
        '--teleop.port=/dev/ttyACM1',
        '--robot.cameras={ front: {type: opencv, index_or_path: 0, width: 640, height: 480, fps: 30}, sub: {type: opencv, index_or_path: 2, width: 640, height: 480, fps: 30}}',
        f'--policy.path={hf_user}/so101_dice_5_smolvla_policy1',
        f'--dataset.repo_id={hf_user}/eval_so101_dice_3',
        f'--dataset.single_task={task_name}', 
        '--dataset.episode_time_s=30',
        '--dataset.num_episodes=1',
        '--resume=true','--play_sounds=false','--dataset.push_to_hub=false'
    ]
    try:
        # サブプロセスを実行
        result = subprocess.run(command, check=True, capture_output=True, text=True)
        print("[SmolVLA] 正常に終了しました")
        print("STDOUT:", result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"[SmolVLA] 実行中にエラーが発生しました")
        print("Exit Code:", e.returncode)
        print("STDOUT:", e.stdout)
        print("STDERR:", e.stderr)
    except FileNotFoundError:
        print("エラー: 'python'コマンドが見つかりません。仮想環境が有効になっていますか？")
        

DEVICE_IDX = 14
info       = sd.query_devices(DEVICE_IDX, kind='input')
ORIG_SR    = int(info['default_samplerate'])    # 例: 44100
CHANNELS   = info['max_input_channels']         # 例: 2
print(f"[Device] #{DEVICE_IDX} {info['name']} @ {ORIG_SR}Hz, {CHANNELS}ch")

sd.default.device = (DEVICE_IDX, None)
sd.default.dtype  = 'float32'

whisper = WhisperModel("base", device="cpu", compute_type="int8")
client = genai.Client()

SYSTEM_PROMPT = (
    "ユーザーの話し言葉から意図を読み取り、"
    "「play roll dice」か「reset the environments」、「Finish and clean up afterwards」のいずれか一つだけを返答してください。"
)

MAX_DURATION = 30  # 最長録音時間 (秒)
MAX_FRAMES   = int(ORIG_SR * MAX_DURATION)

while True:
    cmd = input("録音開始するには Enter、終了するには quit + Enter:")
    if cmd.strip().lower() == "quit":
        print("終了します。")
        break

    # 録音開始
    buf = sd.rec(MAX_FRAMES, samplerate=ORIG_SR, channels=CHANNELS, dtype="float32")
    input("録音停止するには Enter を押してください…\n")
    sd.stop()

    frames = buf.shape[0]

    stereo = buf[:frames]
    mono   = stereo.mean(axis=1)
    audio_16k = librosa.resample(mono, orig_sr=ORIG_SR, target_sr=16000)

    # Whisper 文字起こし
    segments, info = whisper.transcribe(audio_16k, beam_size=5)
    recognized = " ".join([seg.text for seg in segments]).strip()
    print(f"[Whisper] {recognized}")

    if not recognized:
        print("音声認識できませんでした。\n--- 次へ ---\n")
        continue

    # Gemini へ送信
    combined = f"[SYSTEM]\n{SYSTEM_PROMPT}\n\n[USER]\n\"{recognized}\""
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=combined
    )

    intent = response.text.strip()
    print(f"[Gemini]{intent}")
    
    # SmolVLA 実行
    run_lerobot_record(intent)

    print("--- 次のアクションへ ---\n") 
