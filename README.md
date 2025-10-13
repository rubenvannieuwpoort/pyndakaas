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

`pyndakaas` is meant to be used by calling `process_dir` with an input directory, output directory, and optionally a templates directory (if not provided, 'templates' is used). It uses Jinja templates. It is easiest to show how it works by example.

`build.py`:
```
import markdown
from pyndakaas import Handler, handler, process_dir

from pathlib import Path


@handler()
class Markdown(Handler):
    @staticmethod
    def should_handle(source_path: Path) -> bool:
        return source_path.suffix == '.md'

    def template(self) -> str:
        return 'post'

    def body(self) -> str:
        return markdown.markdown(self.source)


# Using default 'templates' directory
process_dir(Path('src'), Path('build'))
```

`src/posts/example.md`:
```
{
	"title": "This is the title of my first post"
}

# Hello, blog

I wanted to write a blog and `pyndakaas` makes it super easy!
```

`src/index.html`:
```
{
	"title": "Welcome to my blog!",
	"template": "index"
}
```

`templates/post.jinja`:
```
<html lang="en">
<head>
	<title>{{front_matter.title}}</title>
</head>
<body>
{{body}}
</body>
</html>
```

`templates/index.jinja`:
```
<html lang="en">
<head>
	<title>My blog</title>
</head>
<body>
	<p>
		My posts:
		{% for post in root.glob('posts/*.md') %}
		<ul>
			<li><a href="{{post.output_path}}">{{ post.front_matter.title }}</a></li>
		</ul>
		{% endfor %}
	</p>
</body>
</html>
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
