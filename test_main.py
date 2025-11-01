from functions import process_orders, process_text, search_orders
import pandas as pd
from unittest.mock import MagicMock
import pytest

class FakeText:
    def __init__(self, content=""):
        self.content = content
    def get(self, start, end):
        return self.content + "\n"
    def delete(self, start, end):
        self.content = ""
    def insert(self, index, string):
        self.content = string

class FakeEntry:
    def __init__(self, value=""):
        self.value = value
    def get(self):
        return self.value

class FakeLabel:
    def __init__(self):
        self.text = ""
    def config(self, text):
        self.text = text

def test_process_orders_with_separator():
    input_text = FakeText("62134598 62130089")
    separator_entry = FakeEntry(";")
    output_text = FakeText()
    process_orders(input_text, separator_entry, output_text)
    assert output_text.content == "62134598;62130089"

def test_process_orders_default_separator():
    input_text = FakeText("62134598, 62130089")
    separator_entry = FakeEntry("")
    output_text = FakeText()
    process_orders(input_text, separator_entry, output_text)
    assert output_text.content == "62134598,62130089"

def test_process_orders_empty():
    input_text = FakeText("")
    separator_entry = FakeEntry(",")
    output_text = FakeText()
    with pytest.raises(ValueError, match="Não existe nenhuma ordem a ser processada"):
        process_orders(input_text, separator_entry, output_text)

def test_process_text_remove_spaces():
    ptext_input = FakeText("olá mundo teste")
    separator_entry = FakeEntry(",")
    output_text = FakeText()
    process_text(ptext_input, separator_entry, space_choice=False, output_text=output_text)
    assert output_text.content == "olá,mundo,teste"

def test_process_text_keep_spaces():
    ptext_input = FakeText("olá mundo")
    separator_entry = FakeEntry(";")
    output_text = FakeText()
    process_text(ptext_input, separator_entry, space_choice=True, output_text=output_text)
    assert output_text.content == "olá mundo"

def test_process_text_empty():
    ptext_input = FakeText("")
    separator_entry = FakeEntry(",")
    output_text = FakeText()
    with pytest.raises(ValueError, match="Nenhum texto inserido"):
        process_text(ptext_input, separator_entry, space_choice=False, output_text=output_text)

def test_search_orders_found():
    search_input = FakeText("tem 62112345 e 62199999 no texto")
    search_output = FakeText()
    number_of_lines = FakeLabel()
    search_orders(search_input, search_output, number_of_lines)
    assert "62112345" in search_output.content
    assert "62199999" in search_output.content
    assert number_of_lines.text == "Quantidade de ordens encontradas: 2"

def test_search_orders_not_found():
    search_input = FakeText("nenhum código válido")
    search_output = FakeText()
    number_of_lines = FakeLabel()
    with pytest.raises(ValueError, match="Nenhuma ordem encontrada"):
        search_orders(search_input, search_output, number_of_lines)
    assert search_output.content == ""
