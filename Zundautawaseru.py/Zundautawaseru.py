#ロック風にずんだもんに自分の音声ファイルを歌わせる方法
import os
import librosa
from music21 import converter, note, stream
import numpy as np

# 音域の制限
MIN_PITCH = 45  # MIDIのA3
MAX_PITCH = 79  # MIDIのhihiD（D5）

# ロック風スケール（A, B, C, D, E, F#, G）
ROCK_SCALE = [45, 47, 48, 50, 52, 54, 55, 57, 59, 60, 62, 64, 66, 67, 69, 71, 72, 74, 76, 78]

def adjust_pitch_to_scale(pitch):
    """音域を調整し、スケールに合わせる"""
    while pitch < MIN_PITCH:
        pitch += 12  # 1オクターブ上げる
    while pitch > MAX_PITCH:
        pitch -= 12  # 1オクターブ下げる

    # スケールに最も近い音を選択
    closest_pitch = min(ROCK_SCALE, key=lambda x: abs(x - pitch))
    return closest_pitch

def select_mode_per_frame(pitches, magnitudes):
    """各フレームの音高から最頻値を選択"""
    valid_pitches = pitches[pitches > 0]  # 0以上の音高のみ選択

    if len(valid_pitches) == 0:
        # 有効な音高がない場合は None を返す
        return None

    # 最頻値を手動で計算
    unique, counts = np.unique(valid_pitches, return_counts=True)
    pitch_mode = unique[np.argmax(counts)]  # 最頻値を取得
    return pitch_mode

def audio_to_midi(audio_path, midi_output_path):
    """音声ファイルをMIDIファイルに変換"""
    print("音声を読み込んでいます...")
    y, sr = librosa.load(audio_path, sr=None)  # サンプリングレートを元の音声に合わせる
    print("音声の特徴を抽出中...")
    pitches, magnitudes = librosa.piptrack(y=y, sr=sr)

    midi_notes = []
    for frame in range(pitches.shape[1]):
        pitch = select_mode_per_frame(pitches[:, frame], magnitudes[:, frame])
        if pitch is not None:
            midi_pitch = librosa.hz_to_midi(pitch)  # HzをMIDI番号に変換
            adjusted_pitch = adjust_pitch_to_scale(midi_pitch)
            midi_notes.append(int(adjusted_pitch))

    print(f"{len(midi_notes)}個のノートを検出しました")

    # MIDIに変換して保存
    midi_stream = stream.Stream()
    for pitch in midi_notes:
        midi_stream.append(note.Note(pitch, quarterLength=0.25))  # 16分音符
    midi_stream.write('midi', fp=midi_output_path)
    print("MIDIファイルが生成されました:", midi_output_path)

def midi_to_pdf(midi_path, pdf_path):
    """MIDIファイルを五線譜のPDFに変換"""
    print("MIDIファイルを楽譜に変換しています...")
    midi_score = converter.parse(midi_path)

    # 五線譜をPDFに出力
    print("PDFに出力中...")
    midi_score.write('musicxml.pdf', fp=pdf_path)
    print("楽譜PDFが生成されました:", pdf_path)

# 音声ファイルパス
audio_path = r"視聴者様の音声ファイルのパスをここに入れるのだ"  # 音声ファイル
midi_output_path = r"C:\Users\user\Desktop\output.mid"  # MIDI出力パス
pdf_output_path = r"C:\Users\user\Desktop\sheet_music.pdf"  # PDF出力パス

# 音声からMIDI、MIDIから五線譜PDFを生成
audio_to_midi(audio_path, midi_output_path)
midi_to_pdf(midi_output_path, pdf_output_path)

