import json
from typing import List, Dict, Any, Optional
import os
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class YMMPGenerator:
    def __init__(self):
        self.scene_data = []
        self.current_scene = 0
        self.current_layer = 0
        self.metadata = {
            "version": "4.0",
            "generator": "MathVideoGenerator",
            "generator_version": "1.0.0"
        }
        
    def create_scene(self, duration: float, content: Dict[str, Any]) -> None:
        """新しいシーンを作成する"""
        try:
            scene = {
                "id": self.current_scene,
                "duration": duration,
                "content": content,
                "animations": []
            }
            self.scene_data.append(scene)
            self.current_scene += 1
        except Exception as e:
            logger.error(f"シーンの作成に失敗しました: {str(e)}")
            raise
    
    def add_voice_content(self, text: str, speaker: str, duration: float, frame: int) -> None:
        """音声コンテンツを追加する"""
        try:
            content = {
                "type": "voice",
                "text": text,
                "speaker": speaker,
                "position": {"x": 0, "y": 0},
                "font_size": 24,
                "layer": self.current_layer
            }
            
            # フェードイン/アウトアニメーション
            animations = [
                {
                    "type": "fade",
                    "start": 0,
                    "end": 0.5,
                    "from": 0,
                    "to": 1
                },
                {
                    "type": "fade",
                    "start": duration - 0.5,
                    "end": duration,
                    "from": 1,
                    "to": 0
                }
            ]
            
            self.create_scene(duration, content)
            self.scene_data[-1]["animations"] = animations
            self.current_layer += 1
            
        except Exception as e:
            logger.error(f"音声コンテンツの追加に失敗しました: {str(e)}")
            raise
    
    def add_image_content(self, file_path: str, tex_content: str, duration: float, frame: int) -> None:
        """画像コンテンツを追加する"""
        try:
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"ファイルが見つかりません: {file_path}")
            
            content = {
                "type": "image",
                "file_path": file_path,
                "tex_content": tex_content,
                "position": {"x": 0, "y": 0},
                "scale": 1.0,
                "layer": self.current_layer
            }
            
            # スケールアニメーション
            animations = [
                {
                    "type": "scale",
                    "start": 0,
                    "end": 0.5,
                    "from": 0.8,
                    "to": 1.0
                }
            ]
            
            self.create_scene(duration, content)
            self.scene_data[-1]["animations"] = animations
            self.current_layer += 1
            
        except Exception as e:
            logger.error(f"画像コンテンツの追加に失敗しました: {str(e)}")
            raise
    
    def create_chapter_section(self, chapter: Optional[int] = None, section: Optional[int] = None) -> None:
        """チャプターとセクションの情報を追加する"""
        if chapter is not None or section is not None:
            metadata = {}
            if chapter is not None:
                metadata["chapter"] = chapter
            if section is not None:
                metadata["section"] = section
            
            if self.scene_data:
                self.scene_data[-1]["metadata"] = metadata
    
    def generate_ymmp(self, output_path: str) -> None:
        """YMMPファイルを生成する"""
        try:
            # 出力ディレクトリの作成
            output_dir = os.path.dirname(output_path)
            if output_dir and not os.path.exists(output_dir):
                os.makedirs(output_dir)
            
            ymmp_data = {
                "metadata": self.metadata,
                "scenes": self.scene_data
            }
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(ymmp_data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"YMMPファイルを生成しました: {output_path}")
            
        except Exception as e:
            logger.error(f"YMMPファイルの生成に失敗しました: {str(e)}")
            raise
    
    def process_model_output(self, model_output: List[Dict[str, Any]]) -> None:
        """モデルの出力を処理してYMMPファイルを生成する"""
        try:
            for item in model_output:
                if item["type"] == "voice":
                    self.add_voice_content(
                        text=item["content"],
                        speaker=item.get("speaker", "default"),
                        duration=item["duration"],
                        frame=item.get("frame", 0)
                    )
                elif item["type"] == "image":
                    self.add_image_content(
                        file_path=item["file_path"],
                        tex_content=item.get("tex_content", ""),
                        duration=item["duration"],
                        frame=item.get("frame", 0)
                    )
                
                # チャプターとセクションの情報を追加
                if "chapter" in item or "section" in item:
                    self.create_chapter_section(
                        chapter=item.get("chapter"),
                        section=item.get("section")
                    )
                    
        except Exception as e:
            logger.error(f"モデル出力の処理に失敗しました: {str(e)}")
            raise 