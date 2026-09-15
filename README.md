# Novel Style Extractor

面向中文长篇小说的文风提取 Skill。它把几十万字甚至更长的小说语料转换成一个标准化 `style_bundle`，供另一个“小说续写 Skill”按需加载。

它不是微调模型，也不会要求续写时把整本小说塞进上下文。流程分为两层：Python 在本地做可解释的中文 stylometry；ZCode Agent 再根据统计结果和分层抽样片段提炼叙事距离、节奏、对白、动作、情绪、景物、高潮组织等文学规则。

## 设计来源

实现借鉴三类公开项目的思路，但采用 clean-room 代码：

- `ngpepin/stylometric-transfer`：显式 JSON style fingerprint、可量化校准和风格评分。
- `Hiro-Inagawa/write-like-me`：生成规则 / 纠错规则分离、exemplar、验证流程。
- `jnoecker/mowen`：中文 stylometry、字符 n-gram 等思路。

详见 `THIRD_PARTY_NOTICES.md`。本项目不复制 `stylometric-transfer` 的受限许可证代码。

## 输出

一次完整提取会产生：

```text
style_bundle/
├── manifest.json
├── style-profile.json
├── global-style.md
├── avoid-style.md
├── loader-contract.md
├── scenes/
│   ├── dialogue.md
│   ├── action.md
│   ├── emotion.md
│   ├── scenery.md
│   ├── narration.md
│   └── high_tension.md
└── exemplars/
    ├── dialogue.md
    ├── action.md
    ├── emotion.md
    ├── scenery.md
    ├── narration.md
    └── high_tension.md
```

续写 Skill 平时只加载 `global-style.md`、`avoid-style.md`、一个场景模块和对应少量 exemplars；完整 `style-profile.json` 只在诊断偏移时加载。

## ZCode 安装

仓库已经按 ZCode Skill/Plugin 目录组织。

全局安装：

```bash
python install_zcode.py --global
```

项目级安装：

```bash
python install_zcode.py --project /path/to/your/novel-project
```

覆盖旧版本：

```bash
python install_zcode.py --global --force
```

也可以直接把 `skills/novel-style-extractor/` 复制到：

```text
~/.zcode/skills/novel-style-extractor/
```

或当前工作区：

```text
<workspace>/.zcode/skills/novel-style-extractor/
```

安装后在 ZCode 的 Settings → Skills 中刷新并启用，然后在聊天里调用 `$novel-style-extractor`。

## 支持语料

基础版只依赖 Python 标准库，支持：

- TXT
- Markdown
- DOCX（直接读取 OOXML，无需 `python-docx`）
- 包含上述文件的目录
- ZIP 语料包

## 本地快速测试

```bash
python skills/novel-style-extractor/tests/test_pipeline.py
```

## 手动运行分析

```bash
python skills/novel-style-extractor/scripts/analyze_corpus.py /path/to/novel \
  --work-dir .style-work \
  --max-samples 8
```

之后让 `$novel-style-extractor` 根据 `.style-work/analysis.json` 和 `.style-work/samples.jsonl` 完成深层文风归纳并生成 `style_bundle`。

## 与续写 Skill 对接

对接规则在：

```text
skills/novel-style-extractor/references/continuation-integration.md
```

核心原则是让“文风提取”和“剧情续写”保持解耦：前者只生产 `style_bundle`，后者只消费这个固定协议。这样以后换小说、换作者或重新提取风格时，不需要重写续写 Skill。

## License

MIT。
