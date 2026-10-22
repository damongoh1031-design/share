#!/usr/bin/env bash
# ============================================================================
# RDNA4 16GB 本地推理启动模板
# 目标硬件: RX 9060 XT 16GB (gfx1200) + 32GB DDR4 + 5800X3D
# 运行时:   llama.cpp (GGML_VULKAN=ON) + Mesa RADV
# 用法:     ./launch-examples.sh <profile>
#           profile: gemma12 | qwen35 | gemma26 | find-moe
# ============================================================================
set -euo pipefail

LLAMA_SERVER="${LLAMA_SERVER:-/opt/llama.cpp/build/bin/llama-server}"
MODEL_DIR="${MODEL_DIR:-/opt/models}"

# ---- 通用参数 --------------------------------------------------------------
# -ngl 999        所有层尽量上 GPU
# --jinja         必须: 启用各家的 chat template
# --cache-type-*  KV 量化, 16GB 卡上几乎无损且省一半 KV
COMMON=( -ngl 999 --jinja --cache-type-k q8_0 --cache-type-v q8_0 )

# ============================================================================
# A. Gemma4-12B QAT Balanced —— 推荐主力
#    6.87 GiB 全上显存, 滑窗 1024 让 128K 上下文几乎免费, 26-32 tok/s (MTP 40+)
# ============================================================================
gemma12() {
  exec "$LLAMA_SERVER" \
    -m "$MODEL_DIR/gemma4-12b-q4km.gguf" \
    -md "$MODEL_DIR/mtp-gemma-4-12B-it.gguf" --spec-type draft-mtp \
    --mmproj "$MODEL_DIR/gemma4-12b-mmproj.gguf" \
    "${COMMON[@]}" \
    -c 131072 \
    --temp 0.6 --top-k 64 --top-p 0.9 --min-p 0.05 --repeat-penalty 1.1 \
    --host 0.0.0.0 --port 8080
}

# ============================================================================
# B. Qwen3.6-35B-A3B Aggressive —— Agent / 中文 / 代码
#    17.44 GiB 超显存, 必须 --n-cpu-moe 卸载; 15-22 tok/s
#    注意: 官方要求 >=128K 上下文保思考质量, 此处 64K 是显存妥协
# ============================================================================
qwen35() {
  exec "$LLAMA_SERVER" \
    -m "$MODEL_DIR/qwen36-35b-iq4xs.gguf" \
    "${COMMON[@]}" \
    --n-cpu-moe "${N_CPU_MOE:-6}" \
    -c "${CTX:-65536}" \
    --temp 1.0 --top-k 20 --top-p 0.95 --presence-penalty 1.5 \
    --host 0.0.0.0 --port 8081
}

# ============================================================================
# C. Gemma4-26B-A4B QAT Balanced —— 视觉 / 知识备选 (不建议做主力)
#    15.64 GiB 顶满显存, 必须卸载; 25-40 tok/s (MTP 35-50)
# ============================================================================
gemma26() {
  exec "$LLAMA_SERVER" \
    -m "$MODEL_DIR/gemma4-26b-a4b-q4km.gguf" \
    -md "$MODEL_DIR/mtp-gemma-4-26B-A4B-it.gguf" --spec-type draft-mtp \
    --mmproj "$MODEL_DIR/gemma4-26b-a4b-mmproj.gguf" \
    "${COMMON[@]}" \
    --n-cpu-moe "${N_CPU_MOE:-8}" \
    -c "${CTX:-32768}" \
    --temp 0.6 --top-k 64 --top-p 0.9 --min-p 0.05 --repeat-penalty 1.1 \
    --host 0.0.0.0 --port 8082
}

# ============================================================================
# 辅助: 二分查找 --n-cpu-moe 的最小可行值
#   目标不是"最小卸载", 而是"不 OOM 且 kernel 不等待"
#   若从 N 加到 N+2 速度不变 -> 瓶颈不是显存, 停止加
# ============================================================================
find_moe() {
  local model="$1" lo=0 hi=24 mid
  echo "=== 二分查找 $model 的 --n-cpu-moe ==="
  while [ $((hi - lo)) -gt 2 ]; do
    mid=$(( (lo + hi) / 2 ))
    echo "--- 尝试 --n-cpu-moe $mid ---"
    if timeout 120 "$LLAMA_SERVER" -m "$model" -ngl 999 \
         --n-cpu-moe "$mid" -c 4096 --port 18099 \
         --no-webui >/tmp/moe_test.log 2>&1 &
    then
      sleep 45
      if grep -qi "failed to allocate\|out of memory" /tmp/moe_test.log; then
        echo "  OOM -> 提高卸载量"
        lo=$mid
      else
        local tps
        tps=$(grep -oP 'eval time.*?[\d.]+ tokens per second' /tmp/moe_test.log | tail -1 || echo "unknown")
        echo "  可行 ($tps)"
        hi=$mid
      fi
      pkill -f "port 18099" 2>/dev/null || true
    fi
  done
  echo "建议 --n-cpu-moe $hi"
}

case "${1:-help}" in
  gemma12)   gemma12   ;;
  qwen35)    qwen35    ;;
  gemma26)   gemma26   ;;
  find-moe)  find_moe "${2:?用法: $0 find-moe /path/to/model.gguf}" ;;
  *) sed -n '2,12p' "$0"; echo; echo "可用 profile: gemma12 | qwen35 | gemma26 | find-moe <model.gguf>" ;;
esac
