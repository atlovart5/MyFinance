 Visão Geral do Projeto

  Este é um projeto de uma aplicação de finanças pessoais chamada "FinBot", desenvolvida em Python com a biblioteca Dash para a
  interface do usuário. O objetivo principal é criar um assistente financeiro inteligente, capaz de processar, analisar e visualizar
  dados financeiros de forma clara e intuitiva. A aplicação permite que os usuários importem extratos bancários e faturas de cartão de
   crédito, e a IA integrada oferece insights, previsões e gerenciamento de orçamento.

  Comandos Importantes

   - Instalar dependências:
   1   pip install -r requirements.txt
   - Executar a aplicação:
   1   python app/app.py
   - Executar os testes:

   1   python run_tests.py
   - Executar o linter/formatter (opcional, mas recomendado):
   1   ruff check .
   2   ruff format .

  Estrutura de Diretórios

   - `app/`: Contém todo o código-fonte da aplicação Dash.
     - `app/componentes/`: Módulos com componentes de UI reutilizáveis, como o layout responsivo e a barra lateral de navegação.
     - `app/paginas/`: Cada arquivo .py representa uma página/seção da aplicação, como o Dashboard, Orçamento, Previsão, etc.
     - `app/app.py`: Ponto de entrada principal da aplicação. Define a estrutura do app, o roteamento e inicializa o servidor.
     - `app/backend.py`: Lógica de negócio principal. Lida com o processamento de dados, cálculos financeiros e interações com os
       arquivos de dados.
     - `app/config.py`: Configurações da aplicação, como caminhos de arquivos e variáveis de ambiente.
   - `data/`: Diretório para armazenamento de dados.
     - `data/raw/`: Armazena os dados brutos importados pelo usuário (extratos e faturas em formato CSV).
     - `data/processed/`: Contém os dados processados e consolidados, como o dados_consolidados.csv, que serve de base para as
       visualizações.
     - `data/relatorios/`: Local para salvar relatórios gerados, como PDFs mensais.
   - `tests/`: Contém os testes automatizados para garantir a qualidade e a corretude do código.
   - `requirements.txt`: Lista de todas as dependências Python do projeto.
   - `README.md`: Documentação geral do projeto.

  Pontos de Entrada da Aplicação

   - Aplicação Web: A execução começa em app/app.py. Este arquivo inicializa o Dash e monta as diferentes páginas definidas em
     app/paginas/.
   - Lógica de Backend: A maior parte da manipulação de dados e lógica de negócios está centralizada em app/backend.py. As páginas da
     aplicação importam funções deste módulo para processar e exibir os dados.
   - Testes: O script run_tests.py é o ponto de entrada para executar todos os testes definidos no diretório tests/.

  Convenções de Código

   - Estilo: O código segue as convenções da PEP 8.
   - Formatação: Recomenda-se o uso do ruff para linting e formatação para manter a consistência do código.
   - Nomenclatura:
     - Funções e variáveis: snake_case (e.g., calcular_total_despesas).
     - Classes: PascalCase (e.g., FinanceiroApp).
     - Constantes: UPPERCASE_SNAKE_CASE (e.g., DATA_PATH).
   - Documentação: Funções e classes devem ter docstrings explicando seu propósito, argumentos e o que retornam.

  Objetivo da IA (Assistente de Desenvolvimento)

  O objetivo é que você, como uma IA especialista em programação, me auxilie a aprimorar e expandir este projeto. Suas tarefas
  incluirão:

   1. Refatoração e Otimização: Melhorar a estrutura do código, a performance e a legibilidade, aplicando as melhores práticas de
      desenvolvimento em Python e Dash.
   2. Implementação de Novas Funcionalidades: Adicionar novas páginas, componentes interativos, e lógicas de backend, como análise de
      investimentos, planejamento de aposentadoria, ou integração com APIs financeiras.
   3. Melhoria da IA Financeira: Aprimorar os algoritmos de análise e previsão financeira, tornando o "FinBot" um especialista
      financeiro ainda mais competente para o usuário final.
   4. Testes e Qualidade: Escrever testes unitários e de integração para garantir a robustez e a confiabilidade da aplicação.
   5. UI/UX: Sugerir e implementar melhorias na interface do usuário para torná-la mais intuitiva, moderna e amigável.

  Você deve assumir o papel de um desenvolvedor sênior, capaz de entender o contexto do projeto e propor soluções elegantes e
  eficientes.
