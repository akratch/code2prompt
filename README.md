# Code2LLM CLI Tool

A utility for generating LLM-friendly context files from codebases with intelligent filtering and structure visualization.

## Features

- Recursive directory traversal
- Gitignore-style pattern matching
- File size limits
- Visual directory tree with ignored/size-exceeded annotations
- Markdown output with syntax highlighting
- Context description integration

## Installation

```bash
pip install pathspec
```

## Usage

```bash
python code2llm.py [OPTIONS]
```

### Options

| Flag | Description | Default |
|------|-------------|---------|
| `--target-dir` | Directory to process | `.` (current dir) |
| `--ignore-file` | Path to ignore rules file | `.context.ignore` |
| `--output` | Output file path | `context.md` |
| `--max-size` | Maximum file size in bytes | `102400` (100KB) |
| `--context-file` | Path to optional context description file | None |

### Example Commands

1. Basic usage:
   ```bash
   python code2llm.py
   ```

2. Process specific directory with custom ignore rules:
   ```bash
   python code2llm.py --target-dir ./src --ignore-file .custom-ignore
   ```

3. Generate output with 2MB size limit and project description:
   ```bash
   python code2llm.py --max-size 2097152 --context-file project-info.md
   ```

## .context.ignore Example

```gitignore
# Common ignore patterns
*.env
*.log
*.bin
*.hex
*.pdf
*.jpg
*.png
*.zip
.DS_Store

# Directories
node_modules/
__pycache__/
.vscode/
dist/
build/
```

## Output Structure

1. **Context Overview** (optional):  
   Contains content from --context-file
   
2. **Codebase Structure**:  
   Visual directory tree showing all files with ignored/size-exceeded annotations
   
3. **File Contents**:  
   All included files with syntax-highlighted content

## Best Practices

- Use `--context-file` to provide architectural overview
- Keep generated files under 1MB for chat-based LLMs
- Regularly update `.context.ignore` as project evolves
- Combine with manual context descriptions for best results