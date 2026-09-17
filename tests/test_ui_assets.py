"""Static checks for the dashboard's shared visual system."""
import re
import tomllib
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CSS_PATH = ROOT / '.streamlit' / 'styles.css'
CONFIG_PATH = ROOT / '.streamlit' / 'config.toml'
APP_PATH = ROOT / 'app.py'


def relative_luminance(color):
    channels = [int(color[index:index + 2], 16) / 255 for index in (1, 3, 5)]
    linear = [value / 12.92 if value <= 0.04045
              else ((value + 0.055) / 1.055) ** 2.4 for value in channels]
    return 0.2126 * linear[0] + 0.7152 * linear[1] + 0.0722 * linear[2]


def contrast_ratio(first, second):
    lighter, darker = sorted(
        [relative_luminance(first), relative_luminance(second)], reverse=True)
    return (lighter + 0.05) / (darker + 0.05)


class UIAssetTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.css = CSS_PATH.read_text(encoding='utf-8')
        cls.app_source = APP_PATH.read_text(encoding='utf-8')
        cls.tokens = dict(re.findall(r'(--ss-[\w-]+):\s*(#[0-9a-fA-F]{6})', cls.css))
        cls.theme = tomllib.loads(CONFIG_PATH.read_text(encoding='utf-8'))['theme']

    def test_core_text_pairs_meet_wcag_aa(self):
        pairs = [
            ('ink on canvas', self.tokens['--ss-ink'], self.tokens['--ss-canvas']),
            ('muted on canvas', self.tokens['--ss-muted'], self.tokens['--ss-canvas']),
            ('white on teal', '#ffffff', self.tokens['--ss-teal']),
            ('white on dark teal', '#ffffff', self.tokens['--ss-teal-dark']),
        ]
        for name, foreground, background in pairs:
            with self.subTest(pair=name):
                self.assertGreaterEqual(contrast_ratio(foreground, background), 4.5)

    def test_streamlit_theme_matches_design_tokens(self):
        self.assertEqual(self.theme['primaryColor'].lower(), self.tokens['--ss-teal'])
        self.assertEqual(self.theme['backgroundColor'].lower(), self.tokens['--ss-canvas'])
        self.assertEqual(self.theme['textColor'].lower(), self.tokens['--ss-ink'])

    def test_app_buttons_do_not_depend_on_material_icon_font(self):
        self.assertNotIn(':material/', self.app_source)

    def test_internal_streamlit_icons_have_font_independent_fallbacks(self):
        for selector in [
            'stSidebarCollapseButton',
            'stExpandSidebarButton',
            'stExpander',
        ]:
            with self.subTest(selector=selector):
                self.assertIn(selector, self.css)
        self.assertIn('[aria-expanded="false"]', self.css)
        self.assertIn('font-size:0!important', self.css)


if __name__ == '__main__':
    unittest.main()
