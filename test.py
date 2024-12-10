import unittest
from io import StringIO
from main import ConfigParser


class TestConfigParser(unittest.TestCase):
    def setUp(self):
        """Инициализация парсера для тестов."""
        self.parser = ConfigParser()

    def test_parse_constant(self):
        """Тестирование парсинга констант."""
        text = """
        x <- 125;
        y <- $x 10 +$;
        """
        result = self.parser.parse(text)
        self.assertEqual(self.parser.constants["x"], 125)
        self.assertEqual(self.parser.constants["y"], 135)

    def test_parse_struct_simple(self):
        """Тестирование простой структуры."""
        text = """
        struct myStruct {
            a = 15,
            b = 'value',
        }
        """
        result = self.parser.parse(text)
        self.assertIn("myStruct", result)
        self.assertEqual(result["myStruct"]["a"], 15)
        self.assertEqual(result["myStruct"]["b"], "value")

    def test_parse_struct_with_expression(self):
        """Тестирование структуры с выражениями."""
        text = """
        x <- 10;
        struct myStruct {
            a = $x 5 +$,
            b = 'test',
            c = $x 3 mod$,
        }
        """
        result = self.parser.parse(text)
        self.assertIn("myStruct", result)
        self.assertEqual(result["myStruct"]["a"], 15)
        self.assertEqual(result["myStruct"]["b"], "test")
        self.assertEqual(result["myStruct"]["c"], 1)



    def test_invalid_struct_declaration(self):
        """Тестирование некорректного объявления структуры."""
        text = """
        struct myStruct {
            a = 15,
            b = 'value'
        """
        with self.assertRaises(SyntaxError):
            self.parser.parse(text)





    def test_ignore_comments(self):
        """Тестирование игнорирования комментариев."""
        text = """
        *> Это комментарий
        x <- 10;
        *> Ещё один комментарий
        struct myStruct {
            a = 15,
            *> Комментарий внутри структуры
            b = 'value',
        }
        """
        result = self.parser.parse(text)
        self.assertIn("myStruct", result)
        self.assertEqual(result["myStruct"]["a"], 15)
        self.assertEqual(result["myStruct"]["b"], "value")


if __name__ == "__main__":
    unittest.main()
