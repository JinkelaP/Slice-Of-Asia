for file in $(find . -type f -name "*.JPG"); do
    # fetch the file name without extension
    base="${file%.*}"
    # rename the file by replacing the extension from .JPG to .jpg
    newname="${base}.jpg"
    # rename the file in the filesystem with the new name
    git mv "$file" "$newname"
done