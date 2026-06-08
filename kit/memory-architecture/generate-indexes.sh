#!/bin/bash
# AgentivAI — Auto-generate _index.md for every directory in the Context Tree
#
# Usage: ./generate-indexes.sh [base-path]
# Default base: brain/knowledge/

set -e

BASE="${1:-brain/knowledge}"

echo "📋 Generating _index.md files for: $BASE"
echo ""

generate_index() {
  local dir="$1"
  local name=$(basename "$dir")
  local index_file="$dir/_index.md"
  
  # Count .md files (excluding _index.md)
  local count=$(find "$dir" -maxdepth 1 -name "*.md" ! -name "_index.md" 2>/dev/null | wc -l | tr -d ' ')
  
  # Count subdirectories
  local subdirs=$(find "$dir" -maxdepth 1 -mindepth 1 -type d 2>/dev/null | wc -l | tr -d ' ')
  
  # Skip if no content
  if [ "$count" -eq 0 ] && [ "$subdirs" -eq 0 ]; then
    return
  fi
  
  # Generate header
  echo "# $(echo "$name" | sed 's/-/ /g' | awk '{for(i=1;i<=NF;i++) $i=toupper(substr($i,1,1)) tolower(substr($i,2))}1')" > "$index_file"
  echo "" >> "$index_file"
  echo "**Files:** $count | **Subdirectories:** $subdirs" >> "$index_file"
  echo "*Generated: $(date -u +%Y-%m-%d %H:%M UTC)*" >> "$index_file"
  echo "" >> "$index_file"
  
  # List subdirectories
  if [ "$subdirs" -gt 0 ]; then
    echo "## Domains" >> "$index_file"
    echo "" >> "$index_file"
    for subdir in $(find "$dir" -maxdepth 1 -mindepth 1 -type d | sort); do
      local subname=$(basename "$subdir")
      local subcount=$(find "$subdir" -name "*.md" ! -name "_index.md" 2>/dev/null | wc -l | tr -d ' ')
      echo "- **[$subname/]($subname/_index.md)** — $subcount files" >> "$index_file"
    done
    echo "" >> "$index_file"
  fi
  
  # List files
  if [ "$count" -gt 0 ]; then
    echo "## Files" >> "$index_file"
    echo "" >> "$index_file"
    echo "| File | Topic |" >> "$index_file"
    echo "|------|-------|" >> "$index_file"
    for f in $(find "$dir" -maxdepth 1 -name "*.md" ! -name "_index.md" | sort); do
      local fname=$(basename "$f")
      local heading=$(head -5 "$f" | grep "^# " | head -1 | sed 's/^# //')
      [ -z "$heading" ] && heading="(no heading)"
      echo "| [$fname]($fname) | $heading |" >> "$index_file"
    done
    echo "" >> "$index_file"
  fi
  
  echo "  ✓ $index_file ($count files, $subdirs subdirs)"
}

# Generate for all directories (bottom-up so counts are accurate)
find "$BASE" -type d | sort -r | while read dir; do
  generate_index "$dir"
done

echo ""
echo "✅ All _index.md files generated"
echo ""
echo "📊 Summary:"
echo "  Directories: $(find "$BASE" -type d | wc -l | tr -d ' ')"
echo "  Index files: $(find "$BASE" -name "_index.md" | wc -l | tr -d ' ')"
echo "  Knowledge files: $(find "$BASE" -name "*.md" ! -name "_index.md" | wc -l | tr -d ' ')"
