# Skills

AI 助手技能集合 — 为 OpenCode / Claude 等编码代理提供领域专用指令。

## 结构

```
skills/
├── compose-ui-optimizer/   # Kotlin + Compose + MVI 代码优化技能
│   ├── SKILL.md            # 主指令文件
│   ├── scripts/            # Python 校验脚本
│   ├── evals/              # 评估测试用例
│   └── references/         # 参考文档
└── ppt-logic-builder/      # PPT 逻辑构建技能
    ├── SKILL.md
    └── references/
```

## 技能

| 技能 | 说明 |
|------|------|
| **compose-ui-optimizer** | Kotlin + Jetpack Compose + MVI 架构代码审查与重构。提供健康评分、优化建议、注释保留校验和编译验证。 |
| **ppt-logic-builder** | 结构化 PPT 逻辑构建。先梳理叙事框架，再生成幻灯片。支持说服型与汇报型两种结构。 |

## 使用

在每个技能目录下都有 `SKILL.md`，将其加载到 AI 助手的 skill 系统中即可激活对应的领域行为。

## 运行校验

```bash
# compose-ui-optimizer 脚本
python3 compose-ui-optimizer/scripts/validate-comments.py <原始文件> <新文件>
python3 compose-ui-optimizer/scripts/check-self.py <ViewModel.kt> <Screen.kt>
```
