def wrap_text(text, width):
    words = text.split()
    lines = []
    current_words = []

    for word in words:
        if (
            sum(len(word) for word in current_words)
            + len(current_words)
            - 1
            + len(word)
            + 1
            > width
        ):
            lines.append(" ".join(current_words))
            current_words = [word]
        else:
            current_words.append(word)

    if current_words:
        lines.append(" ".join(current_words))

    return "\n".join(lines)


if __name__ == "__main__":
    sample_text =  """
            - create_dirs (bool, optional): Whether to create
                directories for the runner. Defaults to True.
        """
    print(wrap_text(sample_text, 50))
