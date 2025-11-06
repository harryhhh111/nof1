# CLAUDE.md 备份说明

## ⚠️ 重要说明

**CLAUDE.md 主文件已移动到项目根目录！**

### 当前文件位置
- **主文件**: `/home/claude_user/nof1/CLAUDE.md` ← **这是官方指导文件**
- 备份文件: `/home/claude_user/nof1/docs/CLAUDE.md`
- 旧文件: `/home/claude_user/nof1/docs/project/CLAUDE.md`

### 原则
**CLAUDE.md 必须在项目根目录**，因为这是指导 Claude Code 行为的重要文件。

### 验证方法
```bash
# 确认在根目录
ls -l /home/claude_user/nof1/CLAUDE.md

# 查看内容
head -20 /home/claude_user/nof1/CLAUDE.md
```

### 引用方式
在 README.md 或其他文档中：
```markdown
[开发文档](CLAUDE.md#section-name)
```

**注意**: 引用时使用相对路径，不需要 `docs/` 前缀！
