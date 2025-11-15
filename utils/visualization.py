"""
視覺化工具模組

提供生成情緒分析圖表的功能。
"""
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
from typing import List, Tuple, Optional
from collections import Counter

from config import Config
from utils.logging_config import get_logger
from utils.analysis import categorize_emotion, map_emotion_to_score

logger = get_logger(__name__)


def generate_emotion_wave_chart(
    emotions: List[str],
    output_path: str,
    title: str = "Emotion Wave Over Time",
    color: str = '#1f77b4',
    figsize: Tuple[int, int] = (10, 5)
) -> bool:
    """
    生成情緒波動折線圖
    
    Args:
        emotions: 情緒列表
        output_path: 輸出檔案路徑
        title: 圖表標題
        color: 線條顏色
        figsize: 圖表尺寸
        
    Returns:
        True 如果生成成功
    """
    try:
        if not emotions:
            logger.warning("No emotions provided for wave chart")
            return False
        
        # 將情緒映射為數值
        emotion_scores = [map_emotion_to_score(e) for e in emotions]
        
        # 建立圖表
        plt.figure(figsize=figsize)
        plt.plot(emotion_scores, label='Emotion Wave', color=color)
        plt.axhline(y=0, color='gray', linestyle='--')
        plt.yticks([-1, 0, 1], ['Negative', 'Neutral', 'Positive'])
        plt.title(title)
        plt.xlabel("Frame")
        plt.ylabel("Emotion")
        plt.legend()
        
        # 儲存圖表
        plt.savefig(output_path, format='jpg', dpi=100, bbox_inches='tight')
        plt.close()
        
        logger.info(f"Emotion wave chart saved to {output_path}")
        return True
        
    except Exception as e:
        logger.error(f"Error generating emotion wave chart: {e}", exc_info=True)
        return False


def generate_emotion_bar_chart(
    emotions: List[str],
    output_path: str,
    title: str = "Emotion Distribution",
    figsize: Tuple[int, int] = (8, 4)
) -> bool:
    """
    生成情緒分布長條圖
    
    Args:
        emotions: 情緒列表
        output_path: 輸出檔案路徑
        title: 圖表標題
        figsize: 圖表尺寸
        
    Returns:
        True 如果生成成功
    """
    try:
        if not emotions:
            logger.warning("No emotions provided for bar chart")
            return False
        
        # 計算各類情緒的比例
        positive_count = sum(
            1 for e in emotions 
            if categorize_emotion(e) == 'positive'
        )
        negative_count = sum(
            1 for e in emotions 
            if categorize_emotion(e) == 'negative'
        )
        neutral_count = sum(
            1 for e in emotions 
            if categorize_emotion(e) == 'neutral'
        )
        
        total = len(emotions)
        percentages = [
            negative_count / total,
            neutral_count / total,
            positive_count / total
        ]
        
        # 建立圖表
        categories = ['Negative', 'Neutral', 'Positive']
        colors = ['red', 'gray', 'green']
        
        plt.figure(figsize=figsize)
        bars = plt.bar(categories, percentages, color=colors)
        plt.title(title)
        plt.xlabel('Sentiment')
        plt.ylabel('Proportion')
        plt.ylim(0, 1)
        
        # 在長條上標註百分比
        for bar in bars:
            height = bar.get_height()
            plt.text(
                bar.get_x() + bar.get_width() / 2,
                height,
                f'{height:.2%}',
                ha='center',
                va='bottom',
                fontsize=10,
                color='black'
            )
        
        # 儲存圖表
        plt.savefig(output_path, format='jpg', dpi=100, bbox_inches='tight')
        plt.close()
        
        logger.info(f"Emotion bar chart saved to {output_path}")
        return True
        
    except Exception as e:
        logger.error(f"Error generating emotion bar chart: {e}", exc_info=True)
        return False


def generate_combined_wave_chart(
    emotions1: List[str],
    emotions2: List[str],
    output_path: str,
    label1: str = "Camera 1",
    label2: str = "Camera 2",
    title: str = "Combined Emotion Wave",
    figsize: Tuple[int, int] = (10, 5)
) -> bool:
    """
    生成雙攝影機情緒波動對比圖
    
    Args:
        emotions1: 第一個攝影機的情緒列表
        emotions2: 第二個攝影機的情緒列表
        output_path: 輸出檔案路徑
        label1: 第一條線的標籤
        label2: 第二條線的標籤
        title: 圖表標題
        figsize: 圖表尺寸
        
    Returns:
        True 如果生成成功
    """
    try:
        if not emotions1 or not emotions2:
            logger.warning("Insufficient data for combined wave chart")
            return False
        
        # 將情緒映射為數值
        scores1 = [map_emotion_to_score(e) for e in emotions1]
        scores2 = [map_emotion_to_score(e) for e in emotions2]
        
        # 建立圖表
        plt.figure(figsize=figsize)
        plt.plot(scores1, label=label1, color='#1f77b4')
        plt.plot(scores2, label=label2, color='#ff7f0e')
        plt.axhline(y=0, color='gray', linestyle='--')
        plt.yticks([-1, 0, 1], ['Negative', 'Neutral', 'Positive'])
        plt.title(title)
        plt.xlabel("Frame")
        plt.ylabel("Emotion")
        plt.legend()
        
        # 儲存圖表
        plt.savefig(output_path, format='jpg', dpi=100, bbox_inches='tight')
        plt.close()
        
        logger.info(f"Combined wave chart saved to {output_path}")
        return True
        
    except Exception as e:
        logger.error(f"Error generating combined wave chart: {e}", exc_info=True)
        return False


def generate_demographics_title(
    ages: List[int],
    genders: List[Tuple[str, float]]
) -> str:
    """
    生成包含人口統計資訊的圖表標題
    
    Args:
        ages: 年齡列表
        genders: (性別, 信心度) 元組列表
        
    Returns:
        格式化的標題字串
    """
    try:
        if not ages or not genders:
            return "Emotion Analysis"
        
        # 計算平均年齡
        avg_age = round(np.mean(ages))
        
        # 找出最常見的性別
        gender_counts = Counter(gender for gender, _ in genders)
        most_common_gender = gender_counts.most_common(1)[0][0]
        
        # 計算平均性別信心度
        avg_confidence = np.mean([conf for _, conf in genders])
        
        title = (
            f"Emotion Analysis "
            f"(Avg Age: {avg_age}, "
            f"Gender: {most_common_gender} {avg_confidence:.2f}%)"
        )
        
        return title
        
    except Exception as e:
        logger.error(f"Error generating demographics title: {e}")
        return "Emotion Analysis"


def generate_all_charts(
    emotions: List[str],
    ages: List[int],
    genders: List[Tuple[str, float]],
    camera_name: str = "Camera",
    output_dir: Optional[str] = None
) -> bool:
    """
    生成所有圖表（波動圖 + 長條圖）
    
    Args:
        emotions: 情緒列表
        ages: 年齡列表
        genders: 性別列表
        camera_name: 攝影機名稱
        output_dir: 輸出目錄（如未指定則使用當前目錄）
        
    Returns:
        True 如果所有圖表都生成成功
    """
    try:
        if output_dir is None:
            output_dir = Path.cwd()
        else:
            output_dir = Path(output_dir)
            output_dir.mkdir(parents=True, exist_ok=True)
        
        # 生成標題
        title_base = generate_demographics_title(ages, genders)
        
        # 生成波動圖
        wave_path = output_dir / f"{camera_name}_Emotion_Wave.jpg"
        wave_success = generate_emotion_wave_chart(
            emotions,
            str(wave_path),
            title=f"{title_base} - Wave"
        )
        
        # 生成長條圖
        bar_path = output_dir / f"{camera_name}_Emotion_Bar.jpg"
        bar_success = generate_emotion_bar_chart(
            emotions,
            str(bar_path),
            title=f"Sentiment Analysis - {camera_name}"
        )
        
        return wave_success and bar_success
        
    except Exception as e:
        logger.error(f"Error generating all charts: {e}", exc_info=True)
        return False
