"""CSV records must retain a one-to-one mapping to their header fields."""
import unittest

import pandas as pd

from student_success.schema import defaults, parse_csv, validate_features, ValidationError


class CSVStructureTests(unittest.TestCase):
    def setUp(self):
        self.frame = pd.DataFrame([defaults()])

    def test_excess_field_never_becomes_an_implicit_index(self):
        for sep in [',', ';']:
            header, row = self.frame.to_csv(index=False, sep=sep).splitlines()
            for malformed in ['999' + sep + row, row + sep + '999']:
                with self.subTest(sep=sep, row=malformed):
                    with self.assertRaises(ValidationError) as caught:
                        parse_csv((header + '\n' + malformed + '\n').encode())
                    self.assertEqual(caught.exception.issues.iloc[0]['row'], 1)
                    self.assertIn('Jumlah field', caught.exception.issues.iloc[0]['message'])

    def test_short_record_reports_its_data_row(self):
        header, row = self.frame.to_csv(index=False).splitlines()
        with self.assertRaises(ValidationError) as caught:
            parse_csv((header + '\n' + row + '\n' + row.rsplit(',', 1)[0]).encode())
        self.assertEqual(caught.exception.issues.iloc[0]['row'], 2)

    def test_quoted_delimiters_newlines_and_extra_named_columns(self):
        for sep in [',', ';']:
            frame = self.frame.copy()
            frame['note'] = 'A, B; "quoted"\nsecond line'
            parsed = parse_csv(frame.to_csv(index=False, sep=sep).encode('utf-8-sig'))
            self.assertEqual(parsed.loc[0, 'note'], frame.loc[0, 'note'])
            self.assertEqual(list(parsed.index), [0])
            pd.testing.assert_frame_equal(validate_features(parsed), validate_features(self.frame))

    def test_unclosed_quote_duplicate_and_blank_headers_are_rejected(self):
        header, row = self.frame.to_csv(index=False).splitlines()
        for content in [header + '\n"' + row, header + ',Course\n' + row + ',1',
                        header + ',\n' + row + ',extra']:
            with self.subTest(content=content):
                with self.assertRaises(ValidationError):
                    parse_csv(content.encode())

    def test_blank_lines_are_not_records_but_missing_values_still_fail(self):
        header, row = self.frame.to_csv(index=False).splitlines()
        parsed = parse_csv((header + '\n\n' + row + '\n\n').encode())
        self.assertEqual(len(validate_features(parsed)), 1)
        missing = self.frame.copy()
        missing['Admission_grade'] = ''
        with self.assertRaises(ValidationError):
            validate_features(parse_csv(missing.to_csv(index=False).encode()))

    def test_row_and_byte_limits(self):
        header, row = self.frame.to_csv(index=False).splitlines()
        self.assertEqual(len(parse_csv((header + '\n' + (row + '\n') * 10000).encode())), 10000)
        with self.assertRaises(ValidationError):
            parse_csv((header + '\n' + (row + '\n') * 10001).encode())
        with self.assertRaises(ValidationError):
            parse_csv(b'x' * (10 * 1024 * 1024 + 1))


if __name__ == '__main__':
    unittest.main()
