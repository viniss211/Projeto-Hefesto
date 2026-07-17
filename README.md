# HEFESTO

Assistente pessoal de IA para Windows, desenvolvido em Python, com suporte a conversa em linguagem natural, memória persistente, execução controlada de ferramentas locais e fallback automático entre diferentes modelos de IA.

> **Status atual:** versão `0.5.0`  
> **Interface disponível:** terminal/PowerShell  
> **Próxima etapa planejada:** entrada e resposta por voz

---

## Visão geral

O HEFESTO foi projetado para funcionar como um assistente pessoal executado no computador do usuário.

Atualmente, ele consegue:

- Conversar em português pelo terminal.
- Usar modelos de IA online e locais.
- Alternar automaticamente entre provedores.
- Abrir programas permitidos no Windows.
- Salvar preferências e informações em memória persistente.
- Recuperar memórias salvas anteriormente.
- Registrar conversas em SQLite.
- Registrar tentativas de provedores e execuções em arquivos de log.
- Preparar ações sensíveis para confirmação antes da execução.
- Expor ferramentas em formato compatível com function calling.

O projeto ainda está em desenvolvimento. Recursos como voz, interface gráfica, criação automática de skills e automação avançada serão adicionados nas próximas versões.

---

## Arquitetura atual

```text
Usuário
  │
  │ texto pelo terminal
  ▼
CLI do HEFESTO
  │
  ▼
AssistantAgent
  ├── Histórico da conversa
  ├── Instruções do sistema
  ├── Registro de ferramentas
  ├── Sistema de aprovação
  └── Controle do número máximo de etapas
  │
  ▼
FallbackProvider
  ├── Groq
  ├── Ollama
  └── OpenAI opcional
  │
  ▼
Modelo de IA
  │
  ├── responde diretamente
  │
  └── solicita uma ferramenta
         │
         ▼
    ToolRegistry
      ├── list_applications
      ├── open_application
      ├── remember_information
      └── recall_information
         │
         ▼
      Resultado da ferramenta
         │
         ▼
      Modelo produz a resposta final
```

---

## Componentes principais

| Componente | Função |
|---|---|
| `AssistantAgent` | Coordena o modelo, o histórico, as ferramentas e a resposta final. |
| `FallbackProvider` | Tenta os provedores de IA na ordem configurada. |
| `ToolRegistry` | Mantém a lista de ferramentas autorizadas e controla sua execução. |
| `MemoryStore` | Salva e recupera memórias e mensagens usando SQLite. |
| `GroqProvider` | Usa um modelo hospedado na Groq. |
| `OllamaProvider` | Usa um modelo executado localmente no computador. |
| `OpenAIProvider` | Usa a API da OpenAI quando configurada. |
| `setup_logging` | Cria logs rotativos do sistema. |
| `terminal_approval_handler` | Solicita confirmação antes de ações marcadas como sensíveis. |

---

## Requisitos

- Windows 10 ou Windows 11
- Python 3.12 ou superior compatível
- Git
- PowerShell
- Ambiente virtual Python
- Ollama instalado para uso local
- Chave da Groq para uso online gratuito dentro dos limites da conta
- Chave da OpenAI somente se esse provedor for utilizado

---

## Preparação do ambiente

Entre na pasta do projeto:

```powershell
cd "C:\caminho\para\Projeto-Hefesto"
```

Crie o ambiente virtual, caso ainda não exista:

```powershell
py -3.12 -m venv .venv
```

Ative o ambiente:

```powershell
.\.venv\Scripts\Activate.ps1
```

Caso o PowerShell bloqueie a ativação:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

Depois ative novamente:

```powershell
.\.venv\Scripts\Activate.ps1
```

Instale o projeto e as dependências de desenvolvimento:

```powershell
python -m pip install -e ".[dev]"
```

---

## Configuração do arquivo `.env`

Crie o arquivo local a partir do exemplo:

```powershell
Copy-Item .env.example .env
```

Exemplo de configuração:

```dotenv
APP_NAME=Hefesto
APP_ENV=development
LOG_LEVEL=INFO

# Ordem de tentativa dos provedores.
AI_PROVIDER_CHAIN=groq,ollama

AI_TIMEOUT_SECONDS=120
MAX_TOOL_ROUNDS=8

# Groq
GROQ_API_KEY=gsk_COLOQUE_SUA_CHAVE_AQUI
GROQ_BASE_URL=https://api.groq.com/openai/v1
GROQ_MODEL=openai/gpt-oss-20b

# Ollama
OLLAMA_BASE_URL=http://localhost:11434/v1
OLLAMA_MODEL=qwen2.5:3b

# OpenAI opcional
OPENAI_API_KEY=
OPENAI_MODEL=gpt-5-mini
```

> O arquivo `.env` não deve ser enviado ao GitHub.

---

## Provedores e troca de modelos

O HEFESTO aceita uma cadeia de provedores:

```dotenv
AI_PROVIDER_CHAIN=groq,ollama
```

A ordem importa.

Nesse exemplo:

1. O sistema tenta usar a Groq.
2. Caso a Groq falhe, atinja o limite ou fique indisponível, o sistema tenta o Ollama.
3. Se todos falharem, o HEFESTO informa que nenhum provedor respondeu.

### Usar somente Groq

```dotenv
AI_PROVIDER_CHAIN=groq
```

### Usar somente Ollama

```dotenv
AI_PROVIDER_CHAIN=ollama
```

### Usar Groq, Ollama e OpenAI

```dotenv
AI_PROVIDER_CHAIN=groq,ollama,openai
```

### Alterar o modelo da Groq

```dotenv
GROQ_MODEL=openai/gpt-oss-20b
```

Troque o valor pelo nome de outro modelo disponível na sua conta e compatível com chamadas de ferramentas.

### Alterar o modelo local do Ollama

```dotenv
OLLAMA_MODEL=qwen2.5:3b
```

Antes de usar outro modelo, faça o download:

```powershell
ollama pull NOME_DO_MODELO
```

Exemplo:

```powershell
ollama pull qwen2.5:3b
```

Confira os modelos instalados:

```powershell
ollama list
```

Teste diretamente no Ollama:

```powershell
ollama run qwen2.5:3b
```

Para encerrar o chat do Ollama:

```text
/bye
```

### Verificar se o Ollama está ativo

```powershell
Invoke-RestMethod http://localhost:11434/api/tags
```

Caso o servidor não esteja rodando:

```powershell
ollama serve
```

### Verificar uso do modelo local

```powershell
ollama ps
```

---

## Comandos disponíveis no HEFESTO

### Comandos principais

| Comando | Função | Exemplo |
|---|---|---|
| `assistente` | Mostra o status atual do sistema. | `assistente` |
| `assistente --chat` | Inicia uma conversa contínua pelo terminal. | `assistente --chat` |
| `assistente --perguntar "MENSAGEM"` | Envia uma única mensagem em linguagem natural para a IA. | `assistente --perguntar "Abra a calculadora"` |
| `assistente --listar-ferramentas` | Exibe os schemas das ferramentas registradas. | `assistente --listar-ferramentas` |
| `assistente --listar-programas` | Mostra os programas que podem ser abertos. | `assistente --listar-programas` |
| `assistente --abrir PROGRAMA` | Abre diretamente um programa permitido, sem usar a IA. | `assistente --abrir calculadora` |
| `assistente --lembrar CHAVE VALOR` | Salva diretamente uma informação na memória. | `assistente --lembrar editor_preferido "VS Code"` |
| `assistente --recordar CONSULTA` | Pesquisa diretamente uma informação na memória. | `assistente --recordar "VS Code"` |
| `assistente --categoria CATEGORIA` | Define a categoria utilizada junto com `--lembrar` ou `--recordar`. | `--categoria preferencias` |
| `assistente --importancia N` | Define a importância da memória de 1 a 5. | `--importancia 4` |

---

## Exemplos de uso

### Ver o status

```powershell
assistente
```

Saída esperada:

```text
==================================================
Assistente Local v0.5.0
Status: online
Ferramentas carregadas: 4
==================================================
IA, memória e ferramentas inicializadas.
Use 'assistente --chat' para conversar.
```

### Fazer uma pergunta simples

```powershell
assistente --perguntar "Responda apenas dizendo que o sistema está funcionando."
```

### Perguntar quais programas podem ser abertos

```powershell
assistente --perguntar "Quais programas você consegue abrir?"
```

### Abrir a calculadora usando linguagem natural

```powershell
assistente --perguntar "Abra a calculadora para mim."
```

### Abrir um programa sem passar pela IA

```powershell
assistente --abrir calculadora
```

### Abrir o Bloco de Notas

```powershell
assistente --abrir "bloco de notas"
```

### Abrir o Paint

```powershell
assistente --abrir paint
```

### Abrir o Explorador de Arquivos

```powershell
assistente --abrir "explorador de arquivos"
```

### Abrir o VS Code

```powershell
assistente --abrir vscode
```

---

## Memória persistente

O HEFESTO utiliza SQLite para guardar informações entre diferentes execuções.

O banco padrão fica em:

```text
data/assistant.db
```

### Salvar uma informação diretamente

```powershell
assistente --lembrar editor_preferido "VS Code" --categoria preferencias --importancia 4
```

### Consultar uma memória diretamente

```powershell
assistente --recordar "VS Code" --categoria preferencias
```

### Salvar uma informação usando linguagem natural

```powershell
assistente --perguntar "Lembre que meu editor preferido é o VS Code."
```

### Recuperar uma informação usando linguagem natural

```powershell
assistente --perguntar "Qual é meu editor preferido?"
```

### Categorias sugeridas

| Categoria | Uso sugerido |
|---|---|
| `perfil` | Nome, idioma e informações gerais do usuário. |
| `preferencias` | Editor, navegador, estilo de resposta e escolhas recorrentes. |
| `trabalho` | Projetos, ferramentas e rotinas profissionais. |
| `projetos` | Informações específicas sobre projetos em andamento. |
| `rotinas` | Hábitos e tarefas repetidas. |
| `general` | Categoria padrão quando nenhuma outra é informada. |

### Importância das memórias

| Valor | Significado sugerido |
|---|---|
| `1` | Informação comum ou temporária. |
| `2` | Informação útil, mas pouco relevante. |
| `3` | Preferência ou fato recorrente. |
| `4` | Informação importante para personalização. |
| `5` | Informação essencial para o comportamento do assistente. |

---

## Conversa contínua

Inicie:

```powershell
assistente --chat
```

Exemplo:

```text
Você: Olá

Assistente: Olá! Como posso ajudar?

Você: Quais programas você consegue abrir?

[FERRAMENTA: list_applications | OK]

Assistente: Posso abrir a calculadora, o bloco de notas, o Paint...

Você: Abra a calculadora

[FERRAMENTA: open_application | OK]

Assistente: A calculadora foi aberta.

Você: sair

Conversa encerrada.
```

Comandos que encerram o modo de conversa:

```text
sair
exit
encerrar
```

---

## Ferramentas registradas

| Ferramenta | Função | Aprovação atual |
|---|---|---|
| `list_applications` | Lista os programas autorizados. | Não |
| `open_application` | Abre um programa autorizado no Windows. | Não |
| `remember_information` | Salva um fato ou preferência no SQLite. | Não |
| `recall_information` | Pesquisa memórias existentes. | Não |

A IA não executa comandos arbitrários no PowerShell. Ela somente pode solicitar ferramentas que estejam registradas no `ToolRegistry`.

---

## Programas atualmente autorizados

| Nome aceito | Programa |
|---|---|
| `calculadora` | Calculadora do Windows |
| `bloco de notas` | Bloco de Notas |
| `paint` | Microsoft Paint |
| `explorador de arquivos` | Explorador de Arquivos |
| `vscode` | Visual Studio Code |

Alguns aliases também são reconhecidos:

```text
calc
calculator
notepad
explorer
code
vs code
visual studio code
```

---

## Segurança

O sistema atual aplica algumas proteções básicas:

- Ferramentas precisam estar registradas.
- Programas utilizam uma lista permitida.
- Comandos arbitrários não são enviados diretamente ao shell.
- Abertura de programas utiliza `shell=False`.
- Ferramentas podem declarar `requires_approval = True`.
- Ações sensíveis podem solicitar confirmação no terminal.
- Argumentos com nomes como senha, token e API key são removidos dos logs.
- O agente possui limite máximo de etapas.
- Chaves são armazenadas somente no `.env`.
- O arquivo `.env` não deve ser versionado.

Uma ferramenta futura poderá exigir aprovação assim:

```python
class ExampleSensitiveTool(BaseTool):
    name = "example_sensitive_action"
    description = "Exemplo de ação sensível."
    requires_approval = True
```

Ao ser solicitada, o HEFESTO exibirá:

```text
AÇÃO SENSÍVEL SOLICITADA
Ferramenta: example_sensitive_action
...
Autorizar execução? [s/N]:
```

---

## Logs

O HEFESTO cria logs em:

```text
logs/hefesto.log
```

Ver as últimas linhas:

```powershell
Get-Content .\logs\hefesto.log -Tail 30
```

Acompanhar o arquivo em tempo real:

```powershell
Get-Content .\logs\hefesto.log -Wait
```

Os logs são rotativos:

- Tamanho máximo por arquivo: aproximadamente 2 MB.
- Quantidade de backups: 5.
- Arquivos antigos são substituídos automaticamente.

Exemplo de log:

```text
2026-07-17 10:00:00 | INFO | assistente_local.ai.fallback_provider | Tentando provedor de IA: groq
2026-07-17 10:00:01 | INFO | assistente_local.ai.fallback_provider | Resposta obtida pelo provedor: groq
```

---

## Testando o fallback

Para forçar temporariamente uma falha da Groq, altere no `.env`:

```dotenv
GROQ_BASE_URL=http://127.0.0.1:9/v1
```

Garanta que o Ollama esteja ativo:

```powershell
ollama list
```

Execute:

```powershell
assistente --perguntar "Responda apenas dizendo: fallback funcionando."
```

Confira o log:

```powershell
Get-Content .\logs\hefesto.log -Tail 30
```

O esperado é:

```text
Tentando provedor de IA: groq
Provedor groq indisponível. Tentando próximo provedor.
Tentando provedor de IA: ollama
Resposta obtida pelo provedor: ollama
```

Depois restaure:

```dotenv
GROQ_BASE_URL=https://api.groq.com/openai/v1
```

---

## Testes e qualidade de código

Formatar o projeto:

```powershell
ruff format .
```

Verificar problemas:

```powershell
ruff check .
```

Executar os testes:

```powershell
python -m pytest
```

Executar tudo em sequência:

```powershell
ruff format .
ruff check .
python -m pytest
```

---

## Estrutura de diretórios

```text
Projeto-Hefesto/
├── src/
│   └── assistente_local/
│       ├── ai/
│       │   ├── base.py
│       │   ├── fallback_provider.py
│       │   ├── groq_provider.py
│       │   ├── ollama_provider.py
│       │   └── openai_provider.py
│       ├── config/
│       │   └── settings.py
│       ├── memory/
│       │   ├── database.py
│       │   └── store.py
│       ├── observability/
│       │   ├── logging_setup.py
│       │   └── redaction.py
│       ├── tools/
│       │   ├── applications.py
│       │   ├── base.py
│       │   ├── bootstrap.py
│       │   ├── memory.py
│       │   └── registry.py
│       ├── agent.py
│       ├── main.py
│       └── __init__.py
├── tests/
├── skills/
├── data/
├── logs/
├── config/
├── .env.example
├── .gitignore
├── pyproject.toml
└── README.md
```

---

## Fluxo de execução de uma ferramenta

Exemplo:

```text
Usuário:
"Abra a calculadora"

1. O terminal envia a mensagem para o AssistantAgent.
2. O agente envia o histórico, as instruções e os schemas ao modelo.
3. O modelo solicita:

   open_application(application="calculadora")

4. O ToolRegistry verifica se a ferramenta existe.
5. A ferramenta valida se o programa está permitido.
6. O Windows abre a calculadora.
7. O resultado é devolvido ao modelo.
8. O modelo gera a resposta final.
9. A interação é salva no SQLite.
10. A execução é registrada no log de auditoria.
```

---

## Limitações atuais

Nesta versão, o HEFESTO ainda não possui:

- Entrada por microfone.
- Resposta falada.
- Palavra de ativação.
- Interface gráfica.
- Controle avançado de janelas.
- Automação de navegador.
- Leitura e criação geral de arquivos.
- Envio de e-mails.
- Criação automática de novas skills.
- Sandbox para código gerado pela IA.
- Identificação de usuário por voz.
- Funcionamento como serviço em segundo plano.

---

## Roadmap

| Versão planejada | Objetivo |
|---|---|
| `0.6.0` | Microfone, transcrição de voz e resposta falada. |
| `0.7.0` | Interface desktop com PySide6. |
| `0.8.0` | Automação de navegador e arquivos. |
| `0.9.0` | Skills externas e carregamento dinâmico. |
| `1.0.0` | Instalador, interface final e fluxo estável. |

---

## Solução de problemas

### O comando `assistente` não existe

Ative o ambiente virtual:

```powershell
.\.venv\Scripts\Activate.ps1
```

Reinstale em modo editável:

```powershell
python -m pip install -e ".[dev]"
```

Teste alternativamente:

```powershell
python -m assistente_local.main
```

### A Groq informa chave ausente

Confira o `.env`:

```dotenv
GROQ_API_KEY=gsk_SUA_CHAVE
```

Verifique sem mostrar a chave:

```powershell
python -c "from dotenv import load_dotenv; import os; load_dotenv(); print(bool(os.getenv('GROQ_API_KEY')))"
```

Resultado esperado:

```text
True
```

### O Ollama não responde

Confira:

```powershell
ollama list
```

Depois:

```powershell
Invoke-RestMethod http://localhost:11434/api/tags
```

Se necessário:

```powershell
ollama serve
```

### O modelo local ainda não foi baixado

```powershell
ollama pull qwen2.5:3b
```

### A IA responde, mas não abre programas

Liste as ferramentas:

```powershell
assistente --listar-ferramentas
```

Liste os programas permitidos:

```powershell
assistente --listar-programas
```

Teste a ferramenta diretamente:

```powershell
assistente --abrir calculadora
```

### A OpenAI retorna erro 429

Isso normalmente indica falta de créditos ou limite da API.

Use:

```dotenv
AI_PROVIDER_CHAIN=groq,ollama
```

para manter a OpenAI fora da cadeia principal.

### O banco precisa ser recriado durante o desenvolvimento

Feche o HEFESTO e remova o banco:

```powershell
Remove-Item .\data\assistant.db
```

Na próxima execução, as tabelas serão recriadas.

> Essa operação apaga todas as memórias e mensagens armazenadas.

---

## Comandos antes do commit

Formate e teste:

```powershell
ruff format .
ruff check .
python -m pytest
```

Confira os arquivos:

```powershell
git status
```

Verifique se estes itens não aparecem no commit:

```text
.env
data/assistant.db
logs/hefesto.log
.venv/
```

Depois:

```powershell
git add .
git commit -m "feat: adiciona fallback de ia logs aprovacoes e documentacao"
git push
```

---

## Estado atual do projeto

O HEFESTO já possui uma base funcional para:

```text
texto natural
   ↓
modelo de IA
   ↓
decisão de usar ferramenta
   ↓
execução validada no Windows
   ↓
memória persistente
   ↓
resposta final
   ↓
logs e fallback automático
```

O próximo grande módulo será a interação por voz:

```text
microfone
   ↓
speech-to-text
   ↓
AssistantAgent
   ↓
text-to-speech
   ↓
resposta falada
```

---

## Licença

Defina a licença do projeto antes de publicar uma versão estável.

Sugestão para um projeto aberto:

```text
MIT License
```

Adicione um arquivo `LICENSE` na raiz quando decidir a licença final.