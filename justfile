# Initialize a new best practice file
# Usage: just new-bp <category> [scenario]
# Examples:
#   just new-bp explore                    -> bp_explore.md
#   just new-bp modify api-migration       -> bp_modify_api-migration.md
#   just new-bp python django              -> bp_python_django.md

new-bp category scenario="":
    #!/usr/bin/env bash
    set -euo pipefail
    
    if [ -z "{{scenario}}" ]; then
        filename="bp_{{category}}.md"
    else
        filename="bp_{{category}}_{{scenario}}.md"
    fi
    
    target="references/$filename"
    
    if [ -f "$target" ]; then
        echo "Error: $target already exists"
        exit 1
    fi
    
    cp references/bp_template.md "$target"
    echo "Created $target"
    echo "Next steps:"
    echo "  1. Edit $target"
    echo "  2. Add entry to references/bp.md"
