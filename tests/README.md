# Testes ADSS

Suite de testes abrangente para o cliente Astronomy TAP Service (ADSS) usando pytest.

## Visão Geral

A suite de testes cobre os principais componentes do projeto:
- **Models** (User, Query, Role, Schema, Table, Column)
- **Utilitários** (parse_datetime, parquet_to_dataframe, format_table_name, prepare_query_params, handle_response_errors)
- **Exceções** (ADSSClientError, AuthenticationError, PermissionDeniedError, etc.)
- **Autenticação** (Auth class)
- **Cliente Principal** (ADSSClient)

## Estrutura

```
tests/
├── __init__.py                 # Definições de teste
├── conftest.py                 # Fixtures reutilizáveis compartilhadas
├── test_models.py              # Testes de modelos de dados
├── test_utils.py               # Testes de funções utilitárias
├── test_exceptions.py          # Testes de exceções customizadas
├── test_auth.py                # Testes de autenticação
└── test_client.py              # Testes do cliente principal
```

## Execução dos Testes

### Todos os testes
```powershell
python -m pytest tests/ -v
```

### Testes com cobertura
```powershell
python -m pytest tests/ --cov=adss --cov-report=html
```

### Testes de um módulo específico
```powershell
python -m pytest tests/test_models.py -v
```

### Testes com match por padrão
```powershell
python -m pytest tests/ -k "datetime" -v
```

### Testes sem output verboso
```powershell
python -m pytest tests/ -q
```

## Estatísticas

- **Total de testes**: 73
- **Status**: ✅ Todos passando
- **Tempo de execução**: ~3 segundos

### Cobertura por Componente

| Módulo | Testes | Tipo |
|--------|--------|------|
| test_models.py | 18 | User, Query, Role, Metadata models |
| test_utils.py | 25 | Parsing, conversão, tratamento de erros |
| test_exceptions.py | 17 | Hierarquia e criação de exceções |
| test_auth.py | 10 | Autenticação e configuração |
| test_client.py | 3 | Cliente principal |

## Fixtures Disponíveis

As seguintes fixtures estão disponíveis em `conftest.py`:

- `mock_user_dict` - Dicionário com dados de usuário para testes
- `mock_query_dict` - Dicionário com dados de query
- `mock_role_dict` - Dicionário com dados de role
- `mock_http_response` - Mock de resposta HTTP
- `mock_base_url` - URL base padrão para testes
- `mock_username` / `mock_password` - Credenciais de teste
- `sample_datetime_str` - String ISO datetime para testes
- `sample_parquet_bytes` - Dados parquet codificados para teste

## Cobertura de Testes

### Models (test_models.py)
- ✅ Criar User a partir de dicionário
- ✅ Parsing de datetime em User
- ✅ Criar Role com permissões
- ✅ Propriedades Query (is_complete, is_running)
- ✅ Models de metadata (Column, Table, Schema)

### Utils (test_utils.py)
- ✅ Parse datetime (ISO, com Z, sem Z, inválido)
- ✅ Conversão Parquet para DataFrame
- ✅ Formatação de nomes de tabelas
- ✅ Preparação de parâmetros (tipos, conversão, filtro)
- ✅ Tratamento de erros HTTP (401, 403, 404, 500)

### Exceções (test_exceptions.py)
- ✅ Criação de exceções com mensagens
- ✅ Associação de resposta HTTP a exceções
- ✅ Herança e cadeia de exceções
- ✅ Tipos específicos (Auth, Permission, NotFound, Query, Validation)

### Autenticação (test_auth.py)
- ✅ Inicialização com base URL
- ✅ Desativação de SSL verification
- ✅ Timeouts e variáveis de ambiente
- ✅ Integração com httpx

### Cliente (test_client.py)
- ✅ Estrutura de classe (métodos, atributos)
- ✅ Aceitação de kwargs customizados
- ✅ Tratamento de erros de autenticação

## Mocks e Patches

Os testes usam `unittest.mock` para isolar componentes:
- `@patch` para mockar dependências externas
- `Mock()` para criar objetos simulados
- `MagicMock()` para mocks com comportamento automático

## Executando com Cobertura

Para gerar relatório HTML de cobertura:

```powershell
python -m pytest tests/ --cov=adss --cov-report=html
# Abrir htmlcov/index.html no navegador
```

## Adicionando Novos Testes

1. Crie um arquivo `test_*.py` em `tests/`
2. Defina classes começando com `Test`
3. Defina funções começando com `test_`
4. Use fixtures do `conftest.py` quando possível
5. Execute com `pytest` para validar

Exemplo:
```python
def test_algo_novo(self, mock_user_dict):
    """Testa algo novo."""
    user = User.from_dict(mock_user_dict)
    assert user.username == "testuser"
```

## Troubleshooting

### Erro: ModuleNotFoundError
Certifique-se de que o diretório raiz do projeto está no PYTHONPATH.

### Erro: ImportError para dependências
Instale dependências de teste:
```powershell
pip install -e ".[test]"
```

### Timeout nos testes
Aumente o timeout:
```powershell
python -m pytest tests/ --timeout=30
```

## Boas Práticas

- ✅ Use fixtures para dados compartilhados
- ✅ Mantenha testes pequenos e focados
- ✅ Use nomes descritivos (test_feature_condition)
- ✅ Mock dependências externas
- ✅ Agrupe testes relacionados em classes
- ✅ Adicione docstrings explicativos
