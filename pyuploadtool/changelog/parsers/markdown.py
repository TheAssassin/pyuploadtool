from .parser import ChangelogParser


class MarkdownChangelogParser(ChangelogParser):
    def render_to_markdown(self) -> str:
        """
        Parses the changelog to Markdown format
        :return: a string containing parsed markdown information
        """
        markdown_changelog = list()
        # add the title if it is provided
        if self.title is not None:
            markdown_changelog.append(f"# {self.title}")

        for spec in self.changelog.structure():

            if len(self.changelog[spec]) > 0:
                # append a new line before then next section
                markdown_changelog.append("\n")
                markdown_changelog.append(f"## {self.changelog.structure().get(spec)}")

            for commit in self.changelog[spec]:
                commit_link_text = commit.author.name if commit.author.name is not None else commit.sha[:7]
                if self.commit_link_prefix:
                    author = f"([{commit_link_text}]({self.commit_link_prefix}/{commit.sha}))"
                else:
                    author = f"({commit_link_text})"

                markdown_changelog.append(f"* {commit.message} {author}")

        return "\n".join(markdown_changelog)
