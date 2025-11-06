# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 📚 文档分类规范 (重要)

### CLAUDE.md 内容范围
✅ **ONLY** 包含以下内容：
- 指导 Claude Code 行为的内容
- 项目特定的工作流程要求
- 重要的规范和原则
- 强制执行的规则
- 文档分类规范

### ❌ 禁止内容
❌ **以下内容禁止出现在 CLAUDE.md**：
- 项目概述和介绍 → 移至 `README_ROOT.md`
- 常用命令和使用说明 → 移至 `docs/user/`
- 架构和技术说明 → 移至 `docs/dev/`
- API文档和接口说明 → 移至 `docs/user/API_DOCUMENTATION.md`
- 配置说明和参数 → 移至 `docs/dev/`
- 测试说明 → 移至 `docs/dev/DEVELOPMENT.md`
- 安装和部署指南 → 移至 `docs/user/INSTALL.md`
- 快速开始指南 → 移至 `docs/user/QUICKSTART.md`

### 文档位置规范
| 文档类型 | 位置 | 文件名 |
|---------|------|--------|
| 项目总览 | 根目录 | README_ROOT.md |
| AI开发指南 | 根目录 | CLAUDE.md |
| 用户指南 | `docs/user/` | *.md |
| 开发者文档 | `docs/dev/` | *.md |
| 项目文档 | `docs/project/` | *.md |

**⚠️ 重要**: 违反此规范的内容将被立即分离和重构。

## 🔒 Handling Access Restrictions

### When Websites Block Direct Access

Some websites (especially financial/exchange platforms like Binance) actively block automated requests from unknown sources. If direct `WebFetch` fails:

**Error Example:**
```
Claude Code is unable to fetch from https://developers.binance.com/...
```

**Solutions:**

1. **Use MCP Web Fetch Tool** (Recommended for Binance/exchange documentation)
```python
# Search for the documentation first
mcp__web_search.search_query = "binance demo trading API documentation site:binance.com"

# Then fetch specific pages
WebFetch(url="...", prompt="Extract technical details about base URL, authentication, and configuration")
```

2. **Alternative Access Methods**
   - Use search engines to find cached versions
   - Look for mirror sites or GitHub mirrors
   - Access via alternative search indices

3. **For Binance Specifically**
   - Use GitHub mirrors: https://github.com/binance/binance-spot-api-docs
   - Use community documentation
   - Check CCXT library documentation for integration examples

## 🔄 版本控制要求

### ⚠️ 重要：每次更新必须推送GitHub

**所有代码、文档、配置更新必须立即推送到GitHub**，不得在本地未提交状态过夜。

### Git工作流程
```bash
# 1. 添加所有更改
git add .

# 2. 提交更改（包含详细说明）
git commit -m "$(cat << 'EOF'
📚 docs: 更新所有文档以反映项目最新状态

- 更新CLAUDE.md：添加Robust启动脚本信息
- 更新README.md：重新组织，突出核心特性
- 新增DATABASE_GUIDE.md：完整数据库使用指南
- 更新QUICKSTART_TESTNET.md：添加最佳实践
- 更新docs/user/*：补充启动脚本和使用说明
- 强调start_nof1.sh作为推荐启动方式

🤖 Generated with [Claude Code](https://claude.com/claude-code)
EOF
)"

# 3. 推送到GitHub
git push origin main

# 4. 验证推送成功
git status
```

### 提交消息规范
- **格式**: `type(scope): description`
- **类型**:
  - `docs` - 文档更新
  - `feat` - 新功能
  - `fix` - 错误修复
  - `refactor` - 代码重构
  - `test` - 测试相关
- **示例**:
  - `docs: 更新快速开始指南`
  - `feat: 新增Testnet交易功能`
  - `fix: 修复数据获取模块错误`

### ❌ 禁止的行为
- ❌ 在本地保留未提交的更改过夜
- ❌ 一次性提交过多不相关的更改
- ❌ 使用无意义的提交消息（如"update", "fix", "asdf"）
- ❌ 提交敏感信息（API密钥、密码等）

### ✅ 强制要求
- ✅ 每次文档更新后立即推送
- ✅ 代码修改后立即推送
- ✅ 配置变更后立即推送
- ✅ 提交消息必须清晰描述更改内容
- ✅ 大型更改分多次提交，便于追踪
