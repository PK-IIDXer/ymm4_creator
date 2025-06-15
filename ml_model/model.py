import torch
import torch.nn as nn
from transformers import BertModel, BertTokenizer
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
import re
import unicodedata
from pathlib import Path
import logging
import json

logger = logging.getLogger(__name__)

class MathVideoGenerator(nn.Module):
    def __init__(self, bert_model_name: str = 'cl-tohoku/bert-base-japanese-whole-word-masking'):
        super().__init__()
        self.bert = BertModel.from_pretrained(bert_model_name)
        self.tokenizer = BertTokenizer.from_pretrained(bert_model_name)
        
        # 音声とTeXコンテンツ用の別々のエンコーダー
        self.voice_encoder = nn.Linear(768, 512)
        self.tex_encoder = nn.Linear(768, 512)
        
        # 出力層
        self.output_layer = nn.Sequential(
            nn.Linear(1024, 512),
            nn.ReLU(),
            nn.Dropout(0.1),
            nn.Linear(512, 256)
        )
        
    def forward(self, voice_input: Dict[str, torch.Tensor], tex_input: Dict[str, torch.Tensor]) -> torch.Tensor:
        # 音声テキストの処理
        voice_outputs = self.bert(**voice_input)
        voice_features = self.voice_encoder(voice_outputs.last_hidden_state[:, 0, :])
        
        # TeXコンテンツの処理
        tex_outputs = self.bert(**tex_input)
        tex_features = self.tex_encoder(tex_outputs.last_hidden_state[:, 0, :])
        
        # 特徴量の結合
        combined_features = torch.cat([voice_features, tex_features], dim=1)
        
        # 出力層
        return self.output_layer(combined_features)

class DataProcessor:
    def __init__(self, csv_path: str):
        self.csv_path = csv_path
        self.required_fields = ['ymmp_path', 'tex_paths', 'instruction_type', 'speaker', 'text', 'file_path', 'frame', 'length', 'layer']
        self.numeric_fields = ['frame', 'length', 'layer', 'chapter', 'section']
        self.tokenizer = BertTokenizer.from_pretrained('cl-tohoku/bert-base-japanese-whole-word-masking')
        
    def normalize_text(self, text: str) -> str:
        """テキストの正規化を行う"""
        if not isinstance(text, str):
            return ""
            
        # 全角文字を半角に変換
        text = unicodedata.normalize('NFKC', text)
        
        # 特殊文字の処理
        text = re.sub(r'[\r\n\t]', ' ', text)
        text = re.sub(r'\s+', ' ', text)
        
        # 前後の空白を削除
        return text.strip()
    
    def normalize_math_content(self, tex_content: str) -> str:
        """数式コンテンツの正規化を行う"""
        if not isinstance(tex_content, str):
            return ""
        # 不要な空白を削除
        tex_content = re.sub(r'\s+', ' ', tex_content)
        # 数式環境の正規化
        tex_content = re.sub(r'\\begin\{.*?\}', r'\\begin{equation}', tex_content)
        tex_content = re.sub(r'\\end\{.*?\}', r'\\end{equation}', tex_content)
        return tex_content.strip()
    
    def validate_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """データの検証とクリーニングを行う"""
        # 必須フィールドのチェック
        missing_fields = [field for field in self.required_fields if field not in df.columns]
        if missing_fields:
            raise ValueError(f"必須フィールドが不足しています: {missing_fields}")
        
        # 数値フィールドの検証
        for field in self.numeric_fields:
            if field in df.columns:
                df[field] = pd.to_numeric(df[field], errors='coerce')
                df[field] = df[field].fillna(0)
        
        # ファイルパスの検証
        if 'file_path' in df.columns:
            df['file_path'] = df['file_path'].apply(lambda x: str(Path(x)) if pd.notna(x) else '')
        
        return df
    
    def load_data(self) -> pd.DataFrame:
        """CSVファイルからデータを読み込む"""
        try:
            df = pd.read_csv(self.csv_path)
            df = self.validate_data(df)
            logger.info(f"データを読み込みました: {len(df)}行")
            return df
        except Exception as e:
            logger.error(f"データの読み込みに失敗しました: {str(e)}")
            raise
    
    def preprocess_text(self, text: str) -> str:
        """テキストの前処理を行う"""
        return self.normalize_text(text)
    
    def create_dataset(self) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """データセットを作成する"""
        df = self.load_data()
        
        # 音声データと画像データを分離
        voice_data = df[df['instruction_type'] == 'voice'].copy()
        image_data = df[df['instruction_type'] == 'image'].copy()
        
        # テキストの前処理
        voice_data['text'] = voice_data['text'].apply(self.preprocess_text)
        
        # tex_pathsで示されるファイルの内容を読み込んでtex_content列を作成
        def read_tex_file(path):
            def try_open(p, encodings):
                for enc in encodings:
                    try:
                        with open(p, encoding=enc) as f:
                            return f.read()
                    except Exception:
                        continue
                return ''
            try:
                if pd.isna(path) or not str(path).strip():
                    return ''
                contents = []
                for p in str(path).split(','):
                    p = p.strip()
                    if not p:
                        continue
                    # utf-8, cp932, euc-jpの順で試す
                    contents.append(try_open(p, ['utf-8', 'cp932', 'euc-jp']))
                return '\n'.join(contents)
            except Exception as e:
                logger.warning(f"TeXファイルの読み込みに失敗: {path} ({e})")
                return ''
        image_data['tex_content'] = image_data['tex_paths'].apply(read_tex_file)
        # エスケープ修正
        image_data['tex_content'] = image_data['tex_content'].apply(lambda x: re.sub(r'\\begin\{.*?\}', r'\\begin{equation}', x))
        image_data['tex_content'] = image_data['tex_content'].apply(lambda x: re.sub(r'\\end\{.*?\}', r'\\end{equation}', x))
        image_data['tex_content'] = image_data['tex_content'].apply(self.normalize_math_content)
        
        # データの並び替え
        voice_data = voice_data.sort_values(['chapter', 'section', 'frame'])
        image_data = image_data.sort_values(['chapter', 'section', 'frame'])
        
        return voice_data, image_data
    
    def create_training_data(self, voice_data: pd.DataFrame, image_data: pd.DataFrame) -> Dict[str, torch.Tensor]:
        """学習用データを作成する"""
        # 音声データと画像データをペアにする
        paired_data = []
        for _, voice_row in voice_data.iterrows():
            # 同じチャプターとセクションの画像データを探す
            matching_images = image_data[
                (image_data['chapter'] == voice_row['chapter']) & 
                (image_data['section'] == voice_row['section'])
            ]
            if not matching_images.empty:
                # 最も近いフレームの画像を選択
                frame_diffs = (matching_images['frame'] - voice_row['frame']).abs()
                closest_idx = frame_diffs.idxmin()
                closest_image = matching_images.loc[closest_idx]
                paired_data.append({
                    'voice_text': voice_row['text'],
                    'image_tex': closest_image['tex_content']
                })
        
        if not paired_data:
            raise ValueError("ペアになるデータが見つかりませんでした。")
        
        # ペアになったデータをエンコード
        voice_texts = [pair['voice_text'] for pair in paired_data]
        image_texs = [pair['image_tex'] for pair in paired_data]
        
        # 音声データのエンコード
        voice_encodings = self.tokenizer(
            voice_texts,
            padding=True,
            truncation=True,
            max_length=512,
            return_tensors='pt'
        )
        
        # 画像データのエンコード
        image_encodings = self.tokenizer(
            image_texs,
            padding=True,
            truncation=True,
            max_length=512,
            return_tensors='pt'
        )
        
        return {
            'voice': voice_encodings,
            'image': image_encodings
        }

def train_model(model: MathVideoGenerator, train_loader: torch.utils.data.DataLoader, 
                optimizer: torch.optim.Optimizer, criterion: nn.Module, device: torch.device,
                scheduler: Optional[torch.optim.lr_scheduler._LRScheduler] = None) -> float:
    """モデルの学習を行う"""
    model.train()
    total_loss = 0
    
    for batch in train_loader:
        optimizer.zero_grad()
        
        # バッチデータの準備
        voice_input_ids, voice_attention_mask, image_input_ids, image_attention_mask = [b.to(device) for b in batch]
        
        # モデルの出力
        outputs = model(
            {'input_ids': voice_input_ids, 'attention_mask': voice_attention_mask},
            {'input_ids': image_input_ids, 'attention_mask': image_attention_mask}
        )
        
        # 損失の計算（この例では音声と画像の特徴量の差分を損失として使用）
        loss = criterion(outputs, torch.zeros_like(outputs))  # 仮のターゲット
        
        # バックプロパゲーション
        loss.backward()
        optimizer.step()
        
        if scheduler is not None:
            scheduler.step()
        
        total_loss += loss.item()
    
    return total_loss / len(train_loader) 