import pandas as pd

input_path = r""

rename_map = {
    "CardCode": "codigo_do_pn",
    "CardName": "nome_do_pn",
    "CardFName": "nome_estrangeiro",
    "Address": "endereço",
    "StreetNo": "número",
    "Block": "bairro",
    "City": "cidade",
    "State2": "estado",
    "Country": "pais",
    "ZipCode": "cep",
    "CodGrupoEconomicoTratado": "cod._grupo_economico",
    "U_U_GP_Nome_grupo_economico": "nome_do_grupo_economico",
    "CreditLine": "limite_de_credito",
    "CNPJ_CPF": "cnpj_cpf",
    "E_Mail": "e_mail",
    "CreateDate": "data_de_criacao",
    "U_GP_Protege": "delinte",
    "validFor": "ativo",
    "U_sourcepn": "origem_do_pn",
    "PrimeiraCompra": "primeira_compra",
    "UltimaCompra": "ultima_compra",
    "DiasSemCompra": "dias_sem_compra",
    "NomeVendedor": "Vendedor",
    "NomeGrupoCliente": "grupo_cliente",
    "NomeListaPreco": "lista_de_preco",
    "Phone1": "telefone",
    "Phone2": "DDD",
    "Balance": "saldo em conta",
    "U_GL_IdWake": "id_wake",
    "U_GL_AtualizacaoWake": "atualizacao_wake",
    "U_GL_ListaPreco": "lista_preco_wake",
    "U_GL_IdWakeParceiro": "id_wake_parceiro",
    "U_GL_IntegraWake": "integra_wake",
    "U_GL_EmailWake": "email_wake",
    "U_dtUltimaAnaliseCredito": "data_de_analise_credito",
    "Inadimplente": "inadimplente",
    "DataBoletoMaisAntigoInadimplente": "dt_boleto_inadimplente",
}

df = pd.read_excel(input_path, usecols=[name_columns for name_columns in rename_map])

df = df.rename(columns=rename_map)  # Rename the column

"""
def transforma_clientes(df: pd.DataFrame) -> pd.DataFrame:
    
    for i in df.columns:
        if i 
    
    
    return df.DataFrame
"""
