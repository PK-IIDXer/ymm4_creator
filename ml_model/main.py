import torch
from model import MathVideoGenerator, DataProcessor, train_model
from ymmp_generator import YMMPGenerator
import argparse
from torch.utils.data import DataLoader
import os
from torch.optim.lr_scheduler import CosineAnnealingWarmRestarts
import logging

# ロギングの設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    parser = argparse.ArgumentParser(description='数学解説動画生成システム')
    parser.add_argument('--csv_path', type=str, required=True, help='入力CSVファイルのパス')
    parser.add_argument('--output_path', type=str, required=True, help='出力YMMPファイルのパス')
    parser.add_argument('--model_path', type=str, help='学習済みモデルのパス（オプション）')
    parser.add_argument('--batch_size', type=int, default=32, help='バッチサイズ')
    parser.add_argument('--epochs', type=int, default=10, help='学習エポック数')
    parser.add_argument('--learning_rate', type=float, default=1e-5, help='学習率')
    parser.add_argument('--warmup_epochs', type=int, default=2, help='ウォームアップエポック数')
    args = parser.parse_args()

    # デバイスの設定
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    logger.info(f'使用デバイス: {device}')

    # データの読み込みと前処理
    logger.info('データの読み込みを開始します...')
    data_processor = DataProcessor(args.csv_path)
    voice_data, image_data = data_processor.create_dataset()
    
    # 学習データの作成
    logger.info('学習データの作成を開始します...')
    encodings = data_processor.create_training_data(voice_data, image_data)
    
    # データローダーの作成
    train_dataset = torch.utils.data.TensorDataset(
        encodings['voice']['input_ids'],
        encodings['voice']['attention_mask'],
        encodings['image']['input_ids'],
        encodings['image']['attention_mask']
    )
    train_loader = DataLoader(
        train_dataset, 
        batch_size=args.batch_size, 
        shuffle=True,
        num_workers=4,
        pin_memory=True
    )

    # モデルの初期化
    logger.info('モデルの初期化を開始します...')
    model = MathVideoGenerator().to(device)
    if args.model_path and os.path.exists(args.model_path):
        model.load_state_dict(torch.load(args.model_path))
        logger.info(f'学習済みモデルを読み込みました: {args.model_path}')

    # オプティマイザと損失関数の設定
    optimizer = torch.optim.AdamW(
        model.parameters(),
        lr=args.learning_rate,
        weight_decay=0.01
    )
    criterion = torch.nn.MSELoss()
    
    # 学習率スケジューラーの設定
    scheduler = CosineAnnealingWarmRestarts(
        optimizer,
        T_0=args.epochs // 2,  # 最初のリスタートまでのエポック数
        T_mult=2,  # リスタートごとの周期の倍率
        eta_min=args.learning_rate * 0.1  # 最小学習率
    )

    # モデルの学習
    logger.info('モデルの学習を開始します...')
    best_loss = float('inf')
    for epoch in range(args.epochs):
        loss = train_model(model, train_loader, optimizer, criterion, device, scheduler)
        logger.info(f'エポック {epoch+1}/{args.epochs}, 損失: {loss:.4f}')
        
        # ベストモデルの保存
        if loss < best_loss:
            best_loss = loss
            torch.save(model.state_dict(), f'best_model_epoch_{epoch+1}.pt')
            logger.info(f'ベストモデルを保存しました（損失: {loss:.4f}）')

    # YMMPファイル生成
    logger.info('YMMPファイルの生成を開始します...')
    ymmp_generator = YMMPGenerator()
    
    # モデルの推論とYMMPファイル生成
    model.eval()
    with torch.no_grad():
        # 音声データの処理
        for voice_item in voice_data.itertuples():
            ymmp_generator.add_voice_content(
                text=voice_item.text,
                speaker=voice_item.speaker,
                duration=voice_item.length,
                frame=voice_item.frame
            )
            # チャプターとセクションの情報を追加
            ymmp_generator.create_chapter_section(
                chapter=voice_item.chapter,
                section=voice_item.section
            )
        
        # 画像データの処理
        for image_item in image_data.itertuples():
            ymmp_generator.add_image_content(
                file_path=image_item.file_path,
                tex_content=image_item.remark,
                duration=image_item.length,
                frame=image_item.frame
            )

    # YMMPファイルの生成
    ymmp_generator.generate_ymmp(args.output_path)
    logger.info(f'YMMPファイルを生成しました: {args.output_path}')

if __name__ == '__main__':
    main() 