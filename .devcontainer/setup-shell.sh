#!/bin/bash

# 确保 .zshrc 存在 (Oh My Zsh 应该已经创建了它，这里是为了保险)
touch ~/.zshrc

# 将自定义配置追加到 .zshrc
cat << 'EOF' >> ~/.zshrc

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
# 挂载到目录切换钩子
autoload -U add-zsh-hook
add-zsh-hook chpwd auto_activate_venv
auto_activate_venv


# --- 2. Prefix Search (智能历史搜索) ---
# 效果：输入 'git' 按向上键，只显示 git 开头的历史命令
autoload -U up-line-or-beginning-search
autoload -U down-line-or-beginning-search
zle -N up-line-or-beginning-search
zle -N down-line-or-beginning-search

# 绑定上下箭头键
bindkey "^[[A" up-line-or-beginning-search
bindkey "^[[B" down-line-or-beginning-search
# 兼容部分终端模式
bindkey "^[OA" up-line-or-beginning-search
bindkey "^[OB" down-line-or-beginning-search


# --- 3. Word Navigation (Mac 风格: Option + 左右键) ---
# 让 Option(Alt)+Left/Right 跳过一个单词
bindkey "^[[1;3C" forward-word   # Option+Right
bindkey "^[[1;3D" backward-word  # Option+Left
# 兼容转义序列
bindkey "\e[1;3C" forward-word
bindkey "\e[1;3D" backward-word
# 兼容 Esc+f / Esc+b 模式
bindkey "\ef" forward-word
bindkey "\eb" backward-word

# ==============================================
EOF

echo "✅ Zsh custom setup complete!"