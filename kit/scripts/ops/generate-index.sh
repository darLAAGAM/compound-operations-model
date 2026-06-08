#!/bin/bash
# Auto-generate _index.md for every directory in the brain Context Tree
# Run after Knowledge Mining or manually

BRAIN_DIR="/root/aurelio-v2/brain/knowledge"

generate_index() {
    local dir="$1"
    local dirname=$(basename "$dir")
    local index_file="$dir/_index.md"
    
    # Count .md files (excluding _index.md)
    local count=$(find "$dir" -maxdepth 1 -name "*.md" ! -name "_index.md" 2>/dev/null | wc -l)
    
    # Count subdirectories
    local subdirs=$(find "$dir" -maxdepth 1 -mindepth 1 -type d 2>/dev/null | wc -l)
    
    if [ "$count" -eq 0 ] && [ "$subdirs" -eq 0 ]; then
        return
    fi
    
    # Generate index
    cat > "$index_file" << HEADER
# ${dirname^}
**Files:** $count | **Subdirs:** $subdirs | **Updated:** $(date +%Y-%m-%d)

HEADER

    # List subdirectories
    if [ "$subdirs" -gt 0 ]; then
        echo "## Subdirectories" >> "$index_file"
        for subdir in $(find "$dir" -maxdepth 1 -mindepth 1 -type d | sort); do
            local subname=$(basename "$subdir")
            local subcount=$(find "$subdir" -name "*.md" ! -name "_index.md" | wc -l)
            echo "- **$subname/** ($subcount docs)" >> "$index_file"
        done
        echo "" >> "$index_file"
    fi

    # List files
    if [ "$count" -gt 0 ]; then
        echo "## Files" >> "$index_file"
        for f in "$dir"/*.md; do
            [ "$(basename "$f")" = "_index.md" ] && continue
            local fname=$(basename "$f")
            local heading=$(head -1 "$f" 2>/dev/null | sed 's/^#* //')
            local size=$(wc -c < "$f" 2>/dev/null)
            echo "- [$fname]($fname) — $heading ($size bytes)" >> "$index_file"
        done
    fi
}

# Process all directories (bottom-up so parent indexes reflect children)
find "$BRAIN_DIR" -type d | sort -r | while read dir; do
    # Skip directories we don't want to index
    case "$dir" in
        */invoices/data|*/invoices/pdfs|*/.clawhub|*/references|*/marketing-skills-ARCHIVED*) continue ;;
    esac
    generate_index "$dir"
done

echo "Generated _index.md for all brain directories"
