# AGENTS.md

本仓库用于个人维护和迭代给 coding agent 使用的 skills。

## 约定

- 文档默认使用中文，代码和注释使用英文。
- git commit message 使用英文。
- skill 名称和目录名使用小写字母、数字和连字符。
- skill 名称优先描述能力或任务，不绑定当前实现细节、单一供应商或临时数据源，除非该外部系统本身就是 skill 的核心。
- 所有正式 skill 一律放在 `skills/<skill-name>/`，不要直接放在仓库根目录。
- skill 目录至少包含 `SKILL.md`，按需再添加 `agents/`、`scripts/`、`references/`、`assets/`。
- 保持结构简洁，只有在确实需要时再添加 `scripts/`、`references/`、`assets/`。
