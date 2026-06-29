printf "Project tree (with assets removed)\n"
tree | rg -v "(\.pyc|pycache|\.png)"

printf "\nFile lengths:\n"

while IFS= read -r file; do
  lines=$(wc -l <"$file")
  printf "%s lines: %s\n" "$file" "$lines"
done < <(fd -e py) | column -t | sort -k 3 -n
