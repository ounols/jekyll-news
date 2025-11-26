# News Jekyll Theme

A beautiful, modern Jekyll theme inspired by the Mria design. This theme features a clean layout, responsive design, and support for blog posts, videos, authors, and more.

## Features

- 🎨 Modern, clean design
- 📱 Fully responsive
- 📝 Blog posts with categories and tags
- 🎥 Video support
- 👥 Author pages
- 🔍 Search functionality
- 📧 Newsletter subscription
- 🎯 SEO optimized
- ⚡ Fast and lightweight

## Installation

1. Install Jekyll and dependencies:
```bash
bundle install
```

2. Build the site:
```bash
bundle exec jekyll build
```

3. Serve locally:
```bash
bundle exec jekyll serve
```

Visit `http://localhost:4000` to see your site.

## Usage

### Creating Posts

Create new posts in the `_posts` directory with the following format:

```markdown
---
layout: post
title: "Your Post Title"
date: 2024-01-01
categories: [category1, category2]
author: Author Name
excerpt: "A brief excerpt of your post"
---

Your post content here...
```

### Adding Authors

Create author files in the `_authors` directory:

```markdown
---
name: Author Name
image: /assets/images/authors/author.jpg
bio: Author biography
social:
  twitter: https://twitter.com/author
  instagram: https://instagram.com/author
---
```

### Adding Videos

Create video files in the `_videos` directory:

```markdown
---
layout: post
title: "Video Title"
date: 2024-01-01
categories: [video, category]
author: Author Name
video_url: https://youtube.com/watch?v=...
image: /assets/images/videos/video.jpg
---
```

## Configuration

Edit `_config.yml` to customize your site:

- Site title and description
- Navigation menu
- Social media links
- Pagination settings
- And more...

## Structure

```
.
├── _config.yml          # Site configuration
├── _layouts/            # Layout templates
├── _includes/           # Reusable components
├── _posts/              # Blog posts
├── _authors/            # Author profiles
├── _videos/             # Video content
├── assets/              # CSS, JS, images
│   ├── css/
│   └── js/
└── index.html           # Homepage
```

## License

This theme is inspired by the Mria design. Feel free to use and modify as needed.

## Credits

- Design inspiration: Mria by Artem Sheludko
- Built with Jekyll

