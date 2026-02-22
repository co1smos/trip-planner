#!/bin/bash

# 确保 .zshrc 存在
touch ~/.zshrc

MARKER="# === DevContainer Custom Config (Zsh) ==="

# 如果已经写入过，则不重复追加
if grep -qF "$MARKER" ~/.zshrc; then
  echo "Zsh custom setup already applied. Skipping append."
  exit 0
fi

# 将自定义配置追加到 .zshrc
cat << 'EOF' >> ~/.zshrc

# === DevContainer Custom Config (Zsh) ===
# ==============================================
#  Custom Config by DevContainer (Zsh)
# ==============================================

# --- 1. 解决 History 和 Venv 自动激活 ---
HISTFILE=$HOME/.zsh_history
HISTSIZE=10000
SAVEHIST=10000
setopt SHARE_HISTORY      # 多窗口实时同步历史
setopt APPEND_HISTORY
setopt EXTENDED_HISTORY
setopt HIST_IGNORE_DUPS

# 自动激活 .venv
function auto_activate_venv() {
    if [[ -d ".venv" ]]; then
        if [[ "$VIRTUAL_ENV" != "$(pwd)/.venv" ]]; then
            source .venv/bin/activate
        fi
    fi
}
autoload -U add-zsh-hook
add-zsh-hook chpwd auto_activate_venv
auto_activate_venv


# --- 2. Prefix Search (智能历史搜索) ---
autoload -U up-line-or-beginning-search
autoload -U down-line-or-beginning-search
zle -N up-line-or-beginning-search
zle -N down-line-or-beginning-search

bindkey "^[[A" up-line-or-beginning-search
bindkey "^[[B" down-line-or-beginning-search
bindkey "^[OA" up-line-or-beginning-search
bindkey "^[OB" down-line-or-beginning-search


# --- 3. Word Navigation (Mac 风格: Option + 左右键) ---
bindkey "^[[1;3C" forward-word
bindkey "^[[1;3D" backward-word
bindkey "\e[1;3C" forward-word
bindkey "\e[1;3D" backward-word
bindkey "\ef" forward-word
bindkey "\eb" backward-word


# --- 4. Pytest + debugpy aliases ---
# Normal test (show prints)
alias test='pytest -q -s'

# Debug pytest: wait for VS Code attach on port 5678
# Usage examples:
#   test-debug app/agent/test_runner.py
#   test-debug app/agent/test_runner.py::test_name
#   test-debug -k runner
alias test-debug='python -m debugpy --listen 0.0.0.0:5678 --wait-for-client -m pytest -q -s'

# Debug pytest: do NOT wait, attach anytime
alias test-debug-nowait='python -m debugpy --listen 0.0.0.0:5678 -m pytest -q -s'

# ==============================================

EOF

echo "✅ Zsh custom setup complete!"