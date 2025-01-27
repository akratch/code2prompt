#!/usr/bin/env python3
import argparse
from pathlib import Path
import pathspec
from typing import Dict, Any, List

class TreeNode:
    def __init__(self, name: str, is_dir: bool = False):
        self.name = name
        self.is_dir = is_dir
        self.children: List[TreeNode] = []
        self.ignored = False
        self.size_exceeded = False

def build_directory_tree(root: Path, ignore_spec: pathspec.PathSpec, max_size: int, target_dir: Path) -> TreeNode:
    node = TreeNode(root.name, is_dir=True)
    
    for entry in root.iterdir():
        rel_path = entry.relative_to(target_dir)
        ignored = ignore_spec.match_file(rel_path)
        size_exceeded = entry.is_file() and entry.stat().st_size > max_size
        
        if entry.is_dir():
            child = build_directory_tree(entry, ignore_spec, max_size, target_dir)
            child.ignored = ignored
            node.children.append(child)
        else:
            child = TreeNode(entry.name)
            child.ignored = ignored
            child.size_exceeded = size_exceeded
            node.children.append(child)
    
    return node

def format_tree(node: TreeNode, prefix: str = "", is_last: bool = True) -> str:
    connector = "└── " if is_last else "├── "
    result = prefix + connector
    
    if node.is_dir:
        result += f"📁 {node.name}"
    else:
        result += f"📄 {node.name}"
    
    if node.ignored or (not node.is_dir and node.size_exceeded):
        reasons = []
        if node.ignored:
            reasons.append("ignored")
        if node.size_exceeded:
            reasons.append("size exceeded")
        result += f" ({', '.join(reasons)})"
    
    result += "\n"
    
    if node.is_dir:
        children = sorted(node.children, key=lambda x: (x.is_dir, x.name), reverse=True)
        for i, child in enumerate(children):
            extension = "    " if is_last else "│   "
            new_prefix = prefix + extension
            result += format_tree(child, new_prefix, i == len(children)-1)
    
    return result

def main():
    parser = argparse.ArgumentParser(
        description='Generate a LLM-friendly context file from codebase',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument('--target-dir', type=str, default='.',
                       help='Directory to process')
    parser.add_argument('--ignore-file', type=str, default='.context.ignore',
                       help='Path to ignore rules file')
    parser.add_argument('--output', type=str, default='context.md',
                       help='Output file path')
    parser.add_argument('--max-size', type=int, default=102400,
                       help='Maximum file size in bytes (100KB default)')
    parser.add_argument('--context-file', type=str,
                       help='Path to optional context description file')

    args = parser.parse_args()
    
    target_dir = Path(args.target_dir).resolve()
    ignore_file = Path(args.ignore_file)
    
    # Load ignore patterns
    if ignore_file.exists():
        with open(ignore_file, 'r', encoding='utf-8') as f:
            ignore_spec = pathspec.PathSpec.from_lines('gitwildmatch', f)
    else:
        ignore_spec = pathspec.PathSpec([])
    
    # Collect valid files and build tree
    included_files = []
    tree_root = build_directory_tree(target_dir, ignore_spec, args.max_size, target_dir)
    
    for file_path in target_dir.rglob('*'):
        if file_path.is_dir() or file_path.is_symlink():
            continue
            
        rel_path = file_path.relative_to(target_dir)
        if ignore_spec.match_file(rel_path):
            continue
            
        if file_path.stat().st_size > args.max_size:
            continue
            
        included_files.append(file_path)
    
    # Generate output
    with open(args.output, 'w', encoding='utf-8') as out_file:
        # Add context description
        if args.context_file:
            with open(args.context_file, 'r', encoding='utf-8') as cf:
                out_file.write(f"# Context Overview\n\n{cf.read()}\n\n")
        
        # Directory tree section
        out_file.write("# Codebase Structure\n\n")
        out_file.write("```\n")
        out_file.write(format_tree(tree_root))
        out_file.write("```\n\n")
        
        # File contents section
        out_file.write("# File Contents\n\n")
        for path in sorted(included_files):
            rel_path = path.relative_to(target_dir)
            try:
                content = path.read_text(encoding='utf-8')
            except UnicodeDecodeError:
                continue
            
            out_file.write(f"## File: {rel_path}\n")
            out_file.write(f"```{path.suffix.lstrip('.')}\n")
            out_file.write(f"{content}\n")
            out_file.write("```\n\n")

if __name__ == '__main__':
    main()