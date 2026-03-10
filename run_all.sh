#!/usr/bin/bash

# MalGuard 完整运行脚本
# 按数据预处理——提取特征——训练的顺序执行

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

# 时间记录文件 (CSV格式)
TIMING_FILE="$SCRIPT_DIR/timing_results.csv"

echo "=========================================="
echo "   MalGuard 完整运行脚本"
echo "=========================================="
echo ""

# 记录开始时间
START_TIME=$(date +%s)
START_DATETIME=$(date "+%Y-%m-%d %H:%M:%S")

# 初始化CSV文件
echo "step_num,step_name,status,duration_seconds,start_time,end_time" > "$TIMING_FILE"

# 写入函数：记录步骤时间
log_step() {
    local step_num=$1
    local step_name=$2
    local status=$3  # "start" 或 "end" 或 "skip"
    local duration=$4
    local step_start=$5
    local step_end=$6

    if [ "$status" = "end" ]; then
        echo "$step_num,\"$step_name\",$status,$duration,$step_start,$step_end" >> "$TIMING_FILE"
    else
        echo "$step_num,\"$step_name\",$status,,," >> "$TIMING_FILE"
    fi
}

# 解析参数
SKIP_STEP_1=true
SKIP_STEP_2=true
SKIP_STEP_3=true
SKIP_STEP_4=true
SKIP_STEP_5=false
SKIP_STEP_6=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --skip-all)
            SKIP_STEP_1=true
            SKIP_STEP_2=true
            SKIP_STEP_3=true
            SKIP_STEP_4=true
            SKIP_STEP_5=true
            SKIP_STEP_6=true
            shift
            ;;
        --run-all)
            SKIP_STEP_1=false
            SKIP_STEP_2=false
            SKIP_STEP_3=false
            SKIP_STEP_4=false
            SKIP_STEP_5=false
            SKIP_STEP_6=false
            shift
            ;;
        *)
            echo "未知参数: $1"
            echo "用法: $0 [--skip-all] [--run-all]"
            exit 1
            ;;
    esac
done

# Step 1: 构建API调用图并计算中心性
echo "=========================================="
echo "Step 1: 构建API调用图并计算中心性"
echo "=========================================="
STEP_START=$(date +%s)
STEP_START_STR=$(date "+%Y-%m-%d %H:%M:%S")

if [ "$SKIP_STEP_1" = true ]; then
    echo "[跳过] 如需运行: cd API-call-graph && python cal_cen_new.py"
    log_step 1 "构建API调用图并计算中心性" "skip"
else
    cd API-call-graph
    python cal_cen_new.py
    cd ..
    STEP_END=$(date +%s)
    STEP_END_STR=$(date "+%Y-%m-%d %H:%M:%S")
    STEP_DURATION=$((STEP_END - STEP_START))
    log_step 1 "构建API调用图并计算中心性" "end" $STEP_DURATION "$STEP_START_STR" "$STEP_END_STR"
    echo "耗时: ${STEP_DURATION}秒"
fi
echo ""

# Step 2: 计算所有包的平均中心性
echo "=========================================="
echo "Step 2: 计算所有包的平均中心性"
echo "=========================================="
STEP_START=$(date +%s)
STEP_START_STR=$(date "+%Y-%m-%d %H:%M:%S")

if [ "$SKIP_STEP_2" = true ]; then
    echo "[跳过] 如需运行: cd API-call-graph && python cal_final_cen.py"
    log_step 2 "计算所有包的平均中心性" "skip"
else
    cd API-call-graph
    python cal_final_cen.py
    cd ..
    STEP_END=$(date +%s)
    STEP_END_STR=$(date "+%Y-%m-%d %H:%M:%S")
    STEP_DURATION=$((STEP_END - STEP_START))
    log_step 2 "计算所有包的平均中心性" "end" $STEP_DURATION "$STEP_START_STR" "$STEP_END_STR"
    echo "耗时: ${STEP_DURATION}秒"
fi
echo ""

# Step 3: 选取Top 500敏感API
echo "=========================================="
echo "Step 3: 选取Top 500敏感API"
echo "=========================================="
STEP_START=$(date +%s)
STEP_START_STR=$(date "+%Y-%m-%d %H:%M:%S")

if [ "$SKIP_STEP_3" = true ]; then
    echo "[跳过] 如需运行: cd API-call-graph && python top500-ex.py"
    log_step 3 "选取Top 500敏感API" "skip"
else
    cd API-call-graph
    python top500-ex.py
    cd ..
    STEP_END=$(date +%s)
    STEP_END_STR=$(date "+%Y-%m-%d %H:%M:%S")
    STEP_DURATION=$((STEP_END - STEP_START))
    log_step 3 "选取Top 500敏感API" "end" $STEP_DURATION "$STEP_START_STR" "$STEP_END_STR"
    echo "耗时: ${STEP_DURATION}秒"
fi
echo ""

# Step 4: 使用GPT分析敏感API
echo "=========================================="
echo "Step 4: 使用GPT分析敏感API"
echo "=========================================="
STEP_START=$(date +%s)
STEP_START_STR=$(date "+%Y-%m-%d %H:%M:%S")

if [ "$SKIP_STEP_4" = true ]; then
    echo "[跳过] 项目已提供预处理结果: gpt_prompt_result_closeness.json"
    log_step 4 "使用GPT分析敏感API" "skip"
else
    cd API-call-graph
    python GPT-prompt.py
    cd ..
    STEP_END=$(date +%s)
    STEP_END_STR=$(date "+%Y-%m-%d %H:%M:%S")
    STEP_DURATION=$((STEP_END - STEP_START))
    log_step 4 "使用GPT分析敏感API" "end" $STEP_DURATION "$STEP_START_STR" "$STEP_END_STR"
    echo "耗时: ${STEP_DURATION}秒"
fi
echo ""

# Step 5: 提取特征向量
echo "=========================================="
echo "Step 5: 提取特征向量"
echo "=========================================="
STEP_START=$(date +%s)
STEP_START_STR=$(date "+%Y-%m-%d %H:%M:%S")

if [ "$SKIP_STEP_5" = true ]; then
    echo "[跳过] 如需运行: cd fea_ex && python fea_vec_ex.py"
    log_step 5 "提取特征向量" "skip"
else
    cd fea_ex
    python fea_vec_ex.py
    cd ..
    STEP_END=$(date +%s)
    STEP_END_STR=$(date "+%Y-%m-%d %H:%M:%S")
    STEP_DURATION=$((STEP_END - STEP_START))
    log_step 5 "提取特征向量" "end" $STEP_DURATION "$STEP_START_STR" "$STEP_END_STR"
    echo "耗时: ${STEP_DURATION}秒"
fi
echo ""

# Step 6: 合并特征向量为训练数据
echo "=========================================="
echo "Step 6: 合并特征向量为训练数据"
echo "=========================================="
STEP_START=$(date +%s)
STEP_START_STR=$(date "+%Y-%m-%d %H:%M:%S")

if [ "$SKIP_STEP_6" = true ]; then
    echo "[跳过] 如需运行: cd fea_ex && python combine.py"
    log_step 6 "合并特征向量为训练数据" "skip"
else
    cd fea_ex
    python combine.py
    cd ..
    STEP_END=$(date +%s)
    STEP_END_STR=$(date "+%Y-%m-%d %H:%M:%S")
    STEP_DURATION=$((STEP_END - STEP_START))
    log_step 6 "合并特征向量为训练数据" "end" $STEP_DURATION "$STEP_START_STR" "$STEP_END_STR"
    echo "耗时: ${STEP_DURATION}秒"
fi
echo ""

# Step 7: 模型训练与测试
echo "=========================================="
echo "Step 7: 模型训练与测试"
echo "=========================================="
echo "请在 Jupyter Notebook 中运行: model_training/test_model.ipynb"
log_step 7 "模型训练与测试(Jupyter)" "skip"
echo ""

# 记录总时间
END_TIME=$(date +%s)
END_DATETIME=$(date "+%Y-%m-%d %H:%M:%S")
TOTAL_DURATION=$((END_TIME - START_TIME))
TOTAL_MINUTES=$((TOTAL_DURATION / 60))
TOTAL_SECONDS=$((TOTAL_DURATION % 60))

# 追加总时间到CSV
echo "" >> "$TIMING_FILE"
echo "total,,,$TOTAL_DURATION,$START_DATETIME,$END_DATETIME" >> "$TIMING_FILE"

echo "=========================================="
echo "   运行完成!"
echo "=========================================="
echo "总耗时: ${TOTAL_DURATION}秒 (${TOTAL_MINUTES}分${TOTAL_SECONDS}秒)"
echo "时间记录已保存到: $TIMING_FILE"
