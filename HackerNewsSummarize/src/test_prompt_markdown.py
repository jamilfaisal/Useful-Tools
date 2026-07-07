import tempfile
import unittest
from pathlib import Path

from src.prompt_markdown import render_prompt_markdown, write_prompt_markdown


class TestPromptMarkdown(unittest.TestCase):
    def test_render_prompt_markdown_uses_template_file(self):
        template_path = Path(tempfile.mkdtemp()) / "prompt_template.md"
        template_text = "Template content line 1\nTemplate content line 2\n"
        template_path.write_text(template_text, encoding="utf-8")

        self.assertEqual(render_prompt_markdown(template_path), template_text)

    def test_write_prompt_markdown_writes_rendered_template(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            template_path = Path(temp_dir) / "prompt_template.md"
            output_path = Path(temp_dir) / "output" / "prompt.md"
            template_text = "Prompt from template\n"
            template_path.write_text(template_text, encoding="utf-8")

            written_path = write_prompt_markdown(output_path, template_path=template_path)

            self.assertEqual(written_path, output_path)
            self.assertEqual(output_path.read_text(encoding="utf-8"), template_text)


if __name__ == "__main__":
    unittest.main()
