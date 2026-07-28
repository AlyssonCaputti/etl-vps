"""Adaptadores de leitura das fontes SAP.

Este modulo e a PORTA de entrada do pipeline (Ports & Adapters).

Regra fundamental: `transform/` e `pipeline/` nunca sabem de onde o dado veio.
Eles recebem um DataFrame. Quando a origem migrar de arquivo para API, basta
adicionar um adaptador aqui - nenhuma outra camada muda.

Duas decisoes de design que valem explicacao:

1. PROJECAO EXPLICITA (usecols/columns)
   As fontes SAP tem 530 (clientes) e 481 (itens) colunas, das quais ~28%
   carregam informacao. Ler tudo custa 3.9x mais tempo e 47x mais memoria
   (medido). Alem disso, listar as colunas cria um CONTRATO: se o SAP renomear
   ou remover um campo que usamos, falha aqui - alto e claro - em vez de gerar
   NaN silencioso tres camadas adiante.

2. TIPOS EXPLICITOS (dtype)
   Inferencia de tipo do pandas e frag1l e perde dados. Exemplos reais destas
   fontes: `CodeBars` (EAN-13) veio como float64 -> `6901532700915.0`, e zeros
   a esquerda desaparecem. `Phone2` (DDD) veio int64. Identificadores sao
   TEXTO, nunca numero: se voce nao faz aritmetica com o campo, ele e string.
"""

from __future__ import annotations

from pathlib import Path
from typing import Protocol

import pandas as pd


class SourceReader(Protocol):
    """Contrato que todo adaptador de leitura deve satisfazer.

    Usamos `Protocol` (PEP 544) em vez de `ABC` por dois motivos:

    - Structural typing: qualquer objeto com um `read() -> DataFrame` satisfaz
      o contrato, sem precisar herdar. Isso permite que um adaptador de API,
      escrito depois, encaixe sem tocar nesta classe.
    - Testes: um stub de 3 linhas com um metodo `read` e um SourceReader valido.
      Com ABC voce seria obrigado a herdar so para satisfazer o verificador.

    O trade-off: ABC valida em tempo de execucao (erro ao instanciar classe
    incompleta); Protocol so valida no type checker. Aqui preferimos a
    flexibilidade, porque a lista de adaptadores vai crescer.
    """

    def read(self) -> pd.DataFrame:
        """Devolve o dado bruto da fonte, com colunas e tipos ja normalizados."""
        ...


class CsvReader:
    """Le uma fonte CSV com projecao e tipos explicitos."""

    def __init__(
        self,
        path: Path,
        columns: list[str] | None = None,
        dtypes: dict[str, str] | None = None,
        sep: str = ";",
        encoding: str = "utf-8",
    ) -> None:
        self.path = path
        self.columns = columns
        self.dtypes = dtypes or {}
        self.sep = sep
        self.encoding = encoding

    def read(self) -> pd.DataFrame:
        # Validacao de existencia ANTES de tentar ler: a mensagem de erro do
        # pandas para caminho de rede inacessivel e obscura, e num compartilhamento
        # SMB a diferenca entre "arquivo nao existe" e "rede caiu" importa muito
        # no diagnostico de uma falha de madrugada.
        if not self.path.exists():
            raise FileNotFoundError(
                f"Fonte nao encontrada: {self.path}\n"
                "Verifique se o compartilhamento de rede esta acessivel."
            )

        df = pd.read_csv(
            self.path,
            sep=self.sep,
            encoding=self.encoding,
            # usecols: projecao. Se uma coluna listada nao existir no arquivo,
            # o pandas levanta ValueError - exatamente o que queremos.
            usecols=self.columns,
            # dtype: desliga a inferencia para as colunas declaradas.
            dtype=self.dtypes,
            # Nao deixa o pandas transformar strings vazias em NaN de forma
            # inconsistente entre colunas.
            keep_default_na=True,
        )

        if df.empty:
            raise ValueError(
                f"Fonte veio VAZIA: {self.path}\n"
                "Arquivo existe mas nao tem linhas - provavel falha no upstream."
            )

        return df


class ExcelReader:
    """Le uma fonte Excel com projecao e tipos explicitos.

    Nota de performance: `.xlsx` e um ZIP com XML dentro. Nao e splittable e
    e consideravelmente mais lento que CSV - `clientes` tem 25 MB e 530 colunas.
    Se algum dia voce puder influenciar o upstream, pedir CSV em vez de XLSX
    e a melhoria de maior impacto neste pipeline.
    """

    def __init__(
        self,
        path: Path,
        columns: list[str] | None = None,
        dtypes: dict[str, str] | None = None,
        sheet_name: str | int = 0,
    ) -> None:
        self.path = path
        self.columns = columns
        self.dtypes = dtypes or {}
        self.sheet_name = sheet_name

    def read(self) -> pd.DataFrame:
        if not self.path.exists():
            raise FileNotFoundError(
                f"Fonte nao encontrada: {self.path}\n"
                "Verifique se o compartilhamento de rede esta acessivel."
            )

        df = pd.read_excel(
            self.path,
            sheet_name=self.sheet_name,
            usecols=self.columns,
            dtype=self.dtypes,
            engine="openpyxl",
        )

        if df.empty:
            raise ValueError(f"Fonte veio VAZIA: {self.path}")

        return df


class ParquetReader:
    """Le da camada bronze (Parquet).

    Aqui a projecao e qualitativamente melhor que em CSV: Parquet e colunar,
    entao pedir 6 de 481 colunas realmente le apenas os blocos dessas 6 colunas
    do disco. Em CSV o parser e obrigado a varrer todos os bytes da linha para
    encontrar os separadores, mesmo descartando o resultado depois.

    Isso se chama projection pushdown de verdade - e o motivo pelo qual
    formatos colunares dominam analytics.
    """

    def __init__(self, path: Path, columns: list[str] | None = None) -> None:
        self.path = path
        self.columns = columns

    def read(self) -> pd.DataFrame:
        if not self.path.exists():
            raise FileNotFoundError(f"Parquet nao encontrado: {self.path}")

        # Tipos vem do metadado do arquivo - nao ha inferencia nem necessidade
        # de declarar dtype. Essa e uma das grandes vantagens sobre CSV.
        return pd.read_parquet(self.path, columns=self.columns)
