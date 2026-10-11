#!/bin/bash
# 密钥防泄漏自检脚本
# 用法：在项目目录执行  ./check-secrets.sh
# 作用：一条命令确认「密钥文件不会被 git 拿走」，并指出问题出在哪一环。

set -u
cd "$(dirname "$0")" || exit 1

pass=0
fail=0
ok(){   echo "  ✅ $1"; pass=$((pass + 1)); }
bad(){  echo "  ❌ $1"; fail=$((fail + 1)); }

echo "── 1. .gitignore 文件名是否正确 ──"
if [ -f .gitignore ]; then
    ok "根目录存在 .gitignore"
else
    bad "根目录没有 .gitignore（常见原因：被误命名成『 .gitignore』，名字前多一个空格）"
fi

weird=$(ls -a | grep -E '^[[:space:]]' || true)
if [ -n "$weird" ]; then
    bad "发现文件名以空格开头的文件（Git 不会读取它）：$(printf '%s' "$weird" | tr '\n' ' ')"
else
    ok "没有『名字带空格』的文件"
fi

echo
echo "── 2. 密钥文件是否真的被忽略 ──"
found_env=0
for f in .env.development .env .env.local .env.production; do
    [ -e "$f" ] || continue
    found_env=1
    if git check-ignore -q "$f"; then
        ok "$f 已被忽略 —— 命中 $(git check-ignore -v "$f" | awk '{print $1}')"
    else
        bad "$f 未被忽略！现在执行 git add . 会把密钥加进仓库"
    fi
done
[ "$found_env" -eq 0 ] && echo "  · 未发现本地密钥文件（已跳过）"

if [ -e .env.example ]; then
    if git check-ignore -q .env.example; then
        bad ".env.example 被忽略了，但它是模板、需要提交"
    else
        ok ".env.example 未被忽略（正确，模板要进仓库）"
    fi
fi

echo
echo "── 3. 已跟踪文件中有没有『漏网』的密钥文件 ──"
leaked=$(git ls-files -i -c --exclude-standard || true)
if [ -n "$leaked" ]; then
    bad "以下已跟踪文件命中忽略规则（.gitignore 对它们已失效，必须处理）："
    printf '%s\n' "$leaked" | sed 's/^/       /'
    echo "       处理：git rm --cached <文件>，并到平台后台重置该密钥"
else
    ok "没有被跟踪的密钥文件"
fi

echo
echo "── 4. 当前暂存区有没有密钥文件 ──"
staged_bad=$(git diff --cached --name-only | grep -E '(^|/)\.env($|\.)' | grep -vE '\.example$' || true)
if [ -n "$staged_bad" ]; then
    bad "暂存区里有密钥文件：$(printf '%s' "$staged_bad" | tr '\n' ' ')"
else
    ok "暂存区干净"
fi

echo
if [ "$fail" -eq 0 ]; then
    echo "🎉 全部 $pass 项检查通过，可以放心提交。"
else
    echo "⚠️  有 $fail 项未通过，请先修复再执行 git add / git commit。"
    exit 1
fi
