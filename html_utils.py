class HtmlUtils:
    @staticmethod
    def bold(text: str) -> str:
        return f'<b>{text}</b>'

    @staticmethod
    def italic(text: str) -> str:
        return f'<i>{text}</i>'

    @staticmethod
    def hyperlink(text: str, link: str) -> str:
        return f'<a href="{link}">{text}</a>'