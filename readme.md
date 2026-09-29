# 📊 Dashboard de Salários na Área de Dados

Este projeto foi desenvolvido durante a Imersão Dados com Python da Alura e agora foi aprimorado com uma interface mais profissional, filtros avançados e uma visão executiva dos principais indicadores do mercado de dados.

## 🚀 Dashboard online

O projeto também está publicado no Streamlit:

https://imersao-de-dados-com-python-alura-jose-souza.streamlit.app/

## 🧠 Recursos da aplicação

- Filtros por ano, senioridade, tipo de contrato, tamanho da empresa, país e cargo
- Busca por nome de cargo
- Faixa salarial interativa em USD
- KPIs com salário médio, máximo, mediana e cargo mais frequente
- Gráficos de barras, histograma, pizza, choropleth, boxplot e tendência ao longo do tempo
- Dados detalhados em tabela filtrada

## 🛠️ Stack principal

- Python
- Pandas
- Streamlit
- Plotly

## ▶️ Como executar localmente

### 1) Pré-requisitos

- Python 3.11+
- Git

### 2) Clone o repositório

```bash
git clone https://github.com/seu-usuario/Imersao-de-dados-com-Python-Alura.git
cd Imersao-de-dados-com-Python-Alura
```

### 3) Crie e ative um ambiente virtual

Windows:

```powershell
python -m venv .venv
.venv\Scripts\Activate
```

Linux/macOS:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 4) Instale as dependências

```bash
pip install -r requirements.txt
```

### 5) Execute o dashboard

```bash
streamlit run app.py
```

## 🧪 Validação

Para executar os testes locais:

```bash
python -m unittest discover -s tests
```

## 📁 Estrutura do projeto

- `app.py`: ponto de entrada da aplicação
- `src/dashboard_app.py`: lógica principal, filtros e gráficos
- `dados-imersao-final.csv`: conjunto de dados utilizado
- `requirements.txt`: dependências da aplicação
- `tests/`: testes automatizados
- `.gitignore`: arquivos temporários e cache do ambiente

## 📌 Observação

A aplicação prioriza o arquivo local `dados-imersao-final.csv` e, se ele não estiver disponível, faz fallback para a fonte remota do projeto.
