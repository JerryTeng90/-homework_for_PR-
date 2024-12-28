import os
import argparse
import logging
import numpy as np
from sklearn.metrics import classification_report, confusion_matrix
import matplotlib.pyplot as plt
import seaborn as sns
import pickle

from data.data_reader import DataReader
from preprocessors.svm_preprocessor import SVMPreprocessor
from models.adaboost_svm import AdaBoostSVM
from utils.print_utils import print_test_results, print_section_header

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

def test_model(args, language):
    """
    测试模型
    Args:
        args: 参数
        language: 语言类型
    """
    # 加载测试数据
    data_reader = DataReader()
    test_texts, test_labels = data_reader.load_test_data(language)
    
    # 加载预处理器和模型
    model_path = os.path.join('checkpoints', language, 'adaboost_svm.pkl')
    preprocessor_path = os.path.join('checkpoints', language, 'adaboost_svm_preprocessor.pkl')
    
    preprocessor = SVMPreprocessor.load(preprocessor_path)
    model = AdaBoostSVM.load(model_path)
    
    # 特征提取
    logger.info('Extracting features...')
    X_test = preprocessor.transform(test_texts)
    
    # 预测
    test_pred = model.predict(X_test)
    test_prob = model.predict_proba(X_test)
    
    # 计算损失（使用交叉熵）
    epsilon = 1e-15  # 防止log(0)
    test_prob = np.clip(test_prob, epsilon, 1 - epsilon)
    test_loss = -np.mean(np.sum(np.eye(2)[test_labels] * np.log(test_prob), axis=1))
    
    # 使用统一的输出格式
    print_test_results(
        language=language,
        loss=test_loss,
        predictions=test_pred,
        labels=test_labels,
        model_name='adaboost_svm'
    )

def main():
    parser = argparse.ArgumentParser(description='Test AdaBoost-SVM model for sentiment classification')
    parser.add_argument('--batch_size', type=int, default=32, help='Batch size for testing')
    args = parser.parse_args()
    
    # 测试中英文模型
    for language in ['en', 'cn']:
        print_section_header(language)
        try:
            test_model(args, language)
        except Exception as e:
            logger.error(f'Error testing {language} model: {str(e)}')
            continue

if __name__ == '__main__':
    main()