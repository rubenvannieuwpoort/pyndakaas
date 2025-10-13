# Pyndakaas

An extensible static site generator written in Python.

## Features

- **Extensible Handler System**: Register custom file handlers for different content types
- **Flexible Renderer System**: Support for multiple rendering engines (Markdown, etc.)
- **Template Support**: Jinja2-based templating with metadata support
- **File Metadata**: JSON frontmatter parsing for rich content metadata
- **Glob Matching**: Template functions for filtering and selecting files

## Installation

```bash
pip install pyndakaas
```

For development:

```bash
git clone https://github.com/rubenvannieuwpoort/pyndakaas
cd pyndakaas
pip install -e .
```

## Quick Start

```python
from pathlib import Path
from pyndakaas import process_dir, Handler, handler

# Define a custom handler
@handler()
class MarkdownHandler(Handler):
    @staticmethod
    def should_handle(input_path: Path) -> bool:
        return input_path.suffix == '.md'
    
    def template(self) -> str | None:
        return 'post'
    
    def body(self) -> str:
        # Your markdown rendering logic here
        return f"<p>{self.source}</p>"

# Process directory
process_dir(Path('src'), Path('output'))
```

## File Format

Source files use JSON frontmatter followed by content:

```
{
    "title": "My Post",
    "author": "John Doe",
    "template": "custom-layout"
}

# My Content

This is the actual content that will be processed.
```

The `template` field in frontmatter will override the handler's default template specified in the `template` method of the handler.

## Handlers

Handlers define how different file types are processed:

- `should_handle()`: Static method to identify files this handler should process
- `suffix()`: Method returning output file extension (defaults to '.html')
- `body()`: Method returning processed content
- `template()`: Method returning template name to use (or None to don't use a template and instead output the processed content)

## Templates

Templates are Jinja2 files in the `templates/` directory. They receive:

- `front_matter`: Parsed JSON frontmatter from the source file  
- `body`: Processed content from the handler's `body()` method
- `folder`: Globber instance for filtering files relative to current file
- `root`: Globber instance for filtering files relative to the root of the input directory

## License

MIT License - see LICENSE file for details.