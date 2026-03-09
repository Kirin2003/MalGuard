#! /bin/bash

# 清除 MalGuard 项目中的所有中间结果文件
# 运行此脚本后，重新运行代码时不会受中间结果影响

echo "=== 正在清除中间结果文件 ==="
echo ""

# API-call-graph 目录的中间文件
echo "清除 API-call-graph 目录的中间文件..."
rm  ./API-call-graph/closeness_sensitive_api.json
rm  ./API-call-graph/output_top_500_closeness_centrality.json
rm  ./API-call-graph/gpt_prompt_result_closeness.json
rm  ./API-call-graph/check_api_diff.log

# model_training/misclassified_analysis 目录的错分分析文件
echo "清除错分分析文件..."
rm  ./model_training/misclassified_analysis/*.txt

# model_training/models 目录的训练模型
echo "清除训练模型文件..."
rm  ./model_training/models/*/*.pkl
rm  ./model_training/models/*/*.txt

# model_training 的结果文件
echo "清除模型训练结果文件..."
rm  ./model_training/monthly_results.csv

echo ""
echo "=== 清除完成 ==="
echo ""
echo "已清除的文件类型:"
echo "  - JSON 中间结果文件 (closeness_sensitive_api.json 等)"
echo "  - LOG 日志文件"
echo "  - TXT 错分分析文件"
echo "  - PKL 训练模型文件"
echo "  - CSV 结果文件"
