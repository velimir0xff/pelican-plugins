# Authors

This plugins adds attributes to the author objects, which are defined in the `AUTHORS` settings variable.

Example:
```python
AUTHORS = {
    'buzz': {
        'avatar_url': '/images/buzz-avatar.png',
        'bio': 'Space Ranger',
        'location': 'United States'
    },
    'woody': {
        'avatar_url': '/images/woody-avatar.png',
        'bio': 'Cowboy',
        'location': 'USA'
    }
}
```

With this plugin you can use author's info later in the theme templates:
```jinja
<img class="author-thumb" src="{{ article.author.avatar_url }}" alt="{{ article.author }}" nopin="nopin">
```
