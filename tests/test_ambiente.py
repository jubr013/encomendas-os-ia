import sys
from importlib.metadata import version

import encomendas_os


def test_python_atende_a_versao_minima():
    assert sys.version_info >= (3, 12)


def test_versao_do_pacote_instalado_confere_com_o_codigo():
    assert version("encomendas-os") == encomendas_os.__version__
